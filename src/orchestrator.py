"""The MCP client / orchestrator (Track C, spec §5.2): owns the LLM and the loop.

Fully autonomous pipeline: handshake both MCP servers -> per turn
(receive opponent NL message -> LLM decision -> legality guard -> engine apply ->
deliver own message to the opponent's server -> position audit + verify_state)
-> 6 valid sub-games (technical losses voided & re-run) -> JSON report
-> Gmail (draft/send per config).

CLI:
  uv run python -m src.orchestrator --config config.json [--grid 2x2]
      [--mock-llm] [--no-email] [--in-memory]
`--in-memory` runs against in-process FastMCP servers (no ports) — sanity ladder.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import time
from datetime import datetime, timezone

from src.agents.agent import LlmAgent
from src.agents.llm_adapter import make_adapter
from src.common.config import Config, load_config
from src.common.logging import JsonlLogger, console, run_logger
from src.common.schemas import Role, SubGameRecord, TurnResult
from src.engine.engine import Engine
from src.engine.errors import TechnicalLossError
from src.engine.series import SeriesManager
from src.gui.events import write_turn
from src.reporting.builder import build_internal_report, report_body
from src.servers.base_server import create_server, expected_token
from src.servers.client import GameMcpClient


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


class Orchestrator:
    def __init__(self, config: Config, in_memory: bool = False) -> None:
        self.config = config
        self.run_id = time.strftime("run_%Y%m%d_%H%M%S")
        self.log = run_logger(config.logging.dir, self.run_id)
        self.turn_log_path = f"{config.logging.dir}/{self.run_id}_turns.jsonl"
        adapter = make_adapter(config, self.log)
        self.agents = {r: LlmAgent(r, config, adapter) for r in Role}
        self.engine = Engine(config)
        self.records: list[SubGameRecord] = []
        self.technical_losses = 0
        self.in_memory = in_memory
        self.clients: dict[Role, GameMcpClient] = {}
        self.turn_index_global = 0

    # -- connectivity -----------------------------------------------------------
    def _targets(self) -> dict[Role, object]:
        if self.in_memory:
            return {r: create_server(r, self.config) for r in Role}
        return {Role.COP: self.config.mcp.cop_url, Role.THIEF: self.config.mcp.thief_url}

    async def connect(self) -> None:
        targets = self._targets()
        for role in Role:
            token = os.environ.get(
                self.config.mcp.token_env_cop if role is Role.COP else self.config.mcp.token_env_thief,
                expected_token(role, self.config),
            )
            client = GameMcpClient(targets[role], token=token)
            await client.__aenter__()
            await client.handshake(self.config.identity.group_name, role.value)
            self.clients[role] = client
            self.log.log("handshake_ok", role=role.value)
        console.print("[green]MCP handshakes complete[/green]")

    async def close(self) -> None:
        for client in self.clients.values():
            await client.__aexit__(None, None, None)

    # -- game loop ---------------------------------------------------------------
    async def run_sub_game(self, index: int) -> SubGameRecord:
        started = _now_iso()
        state = self.engine.new_sub_game()
        for agent in self.agents.values():
            agent.reset()
        messages: list[tuple[str, str]] = []
        while not state.terminal:
            role = state.turn
            try:
                state = await asyncio.wait_for(
                    self._one_turn(role, index, messages), timeout=self.config.turn_timeout_s
                )
            except asyncio.TimeoutError as e:
                raise TechnicalLossError(f"turn timeout ({self.config.turn_timeout_s}s)") from e
        ended = _now_iso()
        sc = self.config.scoring
        cop_pts, thief_pts = (
            (sc.cop_win, sc.thief_loss) if state.winner is Role.COP else (sc.cop_loss, sc.thief_win)
        )
        record = SubGameRecord(
            index=index,
            winner=state.winner,
            reason=state.reason,
            moves_played=state.move_count,
            barriers_used=state.barriers_used,
            cop_points=cop_pts,
            thief_points=thief_pts,
            started_at=started,
            ended_at=ended,
        )
        self._export_frame(index, messages)
        console.print(
            f"  sub-game {index}: [bold]{state.winner.value}[/bold] wins "
            f"({state.reason}, {state.move_count} rounds, {state.barriers_used} barriers)"
        )
        return record

    async def _one_turn(self, role: Role, sub_game: int, messages: list[tuple[str, str]]):
        agent = self.agents[role]
        own, opp = self.clients[role], self.clients[role.opponent]

        inbox = await own.receive_message()
        opponent_message = None if inbox.get("empty") else inbox["text"]

        obs = self.engine.observation(role)
        legal = self.engine.legal_actions(role)
        decision = agent.decide(obs, legal, opponent_message)
        result: TurnResult = self.engine.apply(role, decision.action)
        result.message = decision.message
        messages.append((role.value, decision.message))

        own_pos = result.state.cop_pos if role is Role.COP else result.state.thief_pos
        await opp.send_message(self.turn_index_global, decision.message)
        await own.report_position(self.turn_index_global, tuple(own_pos))
        verify = await own.verify_state(self.turn_index_global)

        true_opp = result.state.thief_pos if role is Role.COP else result.state.cop_pos
        self.log.log(
            "turn",
            sub_game=sub_game,
            turn=self.turn_index_global,
            actor=role.value,
            action=decision.action.kind,
            fallback=decision.used_fallback,
            belief_accuracy=agent.belief.accuracy(tuple(true_opp)),
            verify_ok=verify["ok"],
            message=decision.message,
        )
        write_turn(self.turn_log_path, result)
        self.turn_index_global += 1
        return result.state

    def _export_frame(self, sub_game: int, messages: list[tuple[str, str]]) -> None:
        if not self.config.gui.export_png:
            return
        try:  # GUI must never kill an autonomous run
            from src.common.schemas import Pass
            from src.gui.board_view import render
            from src.gui.export import save_png

            last = TurnResult(
                turn_index=self.turn_index_global,
                actor=self.engine.state.turn,
                action=Pass(),
                state=self.engine.state,
            )
            save_png(
                render(last, self.config, messages, sub_game=sub_game),
                f"{self.config.gui.artifacts_dir}/{self.run_id}_sub{sub_game}.png",
            )
        except Exception as e:  # noqa: BLE001
            self.log.log("gui_export_failed", error=str(e))

    # -- series ---------------------------------------------------------------
    async def run_series(self) -> list[SubGameRecord]:
        attempts, max_attempts = 0, self.config.num_games * 3
        while len(self.records) < self.config.num_games:
            if attempts >= max_attempts:
                raise RuntimeError("too many technical losses — aborting series")
            attempts += 1
            try:
                self.records.append(await self.run_sub_game(len(self.records) + 1))
            except TechnicalLossError as e:
                self.technical_losses += 1
                self.log.log("technical_loss", error=str(e))
                console.print(f"[yellow]technical loss (voided): {e}[/yellow]")
        return self.records

    def totals(self):
        from src.common.schemas import Totals

        return Totals(
            cop=sum(r.cop_points for r in self.records),
            thief=sum(r.thief_points for r in self.records),
        )

    async def report(self, send_email: bool) -> str:
        report = build_internal_report(self.records, self.totals(), self.config)
        body = report_body(report)
        self.log.log("report_built", totals=report.totals.model_dump())
        if send_email:
            from src.reporting.gmail_sender import send_report

            outcome = send_report(report, self.config)
            console.print(f"[green]report {outcome['mode']}[/green]: {outcome['id']}")
        return body


async def amain(config: Config, in_memory: bool, send_email: bool) -> None:
    orch = Orchestrator(config, in_memory=in_memory)
    await orch.connect()
    try:
        await orch.run_series()
    finally:
        await orch.close()
    t = orch.totals()
    console.print(
        f"[bold]series complete[/bold]: cop {t.cop} — thief {t.thief} "
        f"({orch.technical_losses} technical losses voided) · logs: {orch.turn_log_path}"
    )
    body = await orch.report(send_email)
    if not send_email:
        console.print("[dim]email skipped (--no-email); report body follows[/dim]")
        print(body)


def main() -> None:
    from dotenv import load_dotenv

    load_dotenv()  # local .env: DEEPSEEK_API_KEY, MCP tokens, Google paths
    parser = argparse.ArgumentParser(description="HW6 autonomous game orchestrator")
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--grid", help="override grid size, e.g. 2x2 (sanity ladder)")
    parser.add_argument("--mock-llm", action="store_true", help="use the mock LLM provider")
    parser.add_argument("--no-email", action="store_true", help="build report but do not touch Gmail")
    parser.add_argument("--in-memory", action="store_true", help="in-process MCP servers (no ports)")
    args = parser.parse_args()

    config = load_config(args.config)
    updates: dict = {}
    if args.grid:
        w, h = args.grid.lower().split("x")
        updates["grid_size"] = (int(w), int(h))
    if args.mock_llm:
        updates["llm"] = config.llm.model_copy(update={"provider": "mock"})
    if updates:
        config = config.model_copy(update=updates)
    asyncio.run(amain(config, in_memory=args.in_memory, send_email=not args.no_email))


if __name__ == "__main__":
    main()
