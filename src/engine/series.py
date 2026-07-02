"""Series management: exactly `num_games` VALID sub-games (spec §4.1, §9).

Technical losses (TechnicalLossError from a policy/transport) void the sub-game
and it is re-run; voided runs never enter the records.
"""
from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import Callable, Protocol

from src.common.config import Config
from src.common.schemas import (
    Action,
    Observation,
    Pass,
    Role,
    SubGameRecord,
    Totals,
    TurnResult,
)
from src.engine.engine import Engine
from src.engine.errors import TechnicalLossError


class Policy(Protocol):
    """Decision interface (Track C implements LLM-backed versions)."""

    def __call__(self, obs: Observation, legal: list[Action]) -> Action: ...


OnTurn = Callable[[TurnResult], None]


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


class SeriesManager:
    def __init__(
        self,
        config: Config,
        cop_policy: Policy,
        thief_policy: Policy,
        on_turn: OnTurn | None = None,
        rng: random.Random | None = None,
    ) -> None:
        self.config = config
        self.policies = {Role.COP: cop_policy, Role.THIEF: thief_policy}
        self.on_turn = on_turn
        self.engine = Engine(config, rng=rng)
        self.records: list[SubGameRecord] = []
        self.technical_losses = 0

    # -- single sub-game -------------------------------------------------------
    def run_next_sub_game(self) -> SubGameRecord:
        started = _now()
        state = self.engine.new_sub_game()
        while not state.terminal:
            role = state.turn
            legal = self.engine.legal_actions(role)
            obs = self.engine.observation(role)
            action = self.policies[role](obs, legal) if legal else Pass()
            result = self.engine.apply(role, action)
            state = result.state
            self.engine.state = state  # keep engine's copy authoritative
            if self.on_turn:
                self.on_turn(result)
        record = self._record_from_state(started, _now())
        self.records.append(record)
        return record

    def _record_from_state(self, started: str, ended: str) -> SubGameRecord:
        s = self.engine.state
        assert s is not None and s.terminal and s.winner is not None and s.reason is not None
        sc = self.config.scoring
        if s.winner is Role.COP:
            cop_pts, thief_pts = sc.cop_win, sc.thief_loss
        else:
            cop_pts, thief_pts = sc.cop_loss, sc.thief_win
        return SubGameRecord(
            index=len(self.records) + 1,
            winner=s.winner,
            reason=s.reason,
            moves_played=s.move_count,
            barriers_used=s.barriers_used,
            cop_points=cop_pts,
            thief_points=thief_pts,
            started_at=started,
            ended_at=ended,
        )

    # -- full series -----------------------------------------------------------
    def run_series(self, max_attempts_factor: int = 3) -> list[SubGameRecord]:
        """Run until `num_games` VALID sub-games exist; re-run technical losses."""
        max_attempts = self.config.num_games * max_attempts_factor
        attempts = 0
        while len(self.records) < self.config.num_games:
            if attempts >= max_attempts:
                raise RuntimeError(
                    f"could not complete {self.config.num_games} valid sub-games "
                    f"in {max_attempts} attempts ({self.technical_losses} technical losses)"
                )
            attempts += 1
            try:
                self.run_next_sub_game()
            except TechnicalLossError:
                self.technical_losses += 1  # voided: nothing recorded, loop re-runs
        return self.records

    def totals(self) -> Totals:
        return Totals(
            cop=sum(r.cop_points for r in self.records),
            thief=sum(r.thief_points for r in self.records),
        )


def random_policy(rng: random.Random) -> Policy:
    """Baseline policy for tests/sanity ladder."""

    def _policy(obs: Observation, legal: list[Action]) -> Action:
        return rng.choice(legal)

    return _policy
