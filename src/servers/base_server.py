"""Role-parameterized FastMCP server factory (Track B).

Two independent instances run in production: cop (:8001) and thief (:8002).
The server is a thin, rule-free message bus + verification layer:
tools only — NO LLM, NO game rules (architecture law, spec §5.2).
Auth: bearer token at handshake; the returned session_id is the capability
for subsequent calls. Rotation of the token env var = revoke (PRD_mcp_servers).
"""
from __future__ import annotations

import os
import secrets
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path

from fastmcp import FastMCP

from src.common.config import Config
from src.common.logging import JsonlLogger
from src.common.schemas import Role


@dataclass
class _Session:
    team: str
    client_role: str
    inbox: deque = field(default_factory=deque)
    positions: dict[int, tuple[int, int]] = field(default_factory=dict)
    last_turn: int = -1


def expected_token(role: Role, config: Config) -> str:
    env = config.mcp.token_env_cop if role is Role.COP else config.mcp.token_env_thief
    return os.environ.get(env, f"dev-{role.value}-token")


def create_server(role: Role, config: Config, token: str | None = None) -> FastMCP:
    """Build the MCP server for one role. `token` overrides env (tests)."""
    valid_token = token or expected_token(role, config)
    sessions: dict[str, _Session] = {}
    audit = JsonlLogger(Path(config.logging.dir) / f"mcp_{role.value}.jsonl")

    mcp = FastMCP(name=f"{role.value}-mcp")

    def _session(session_id: str) -> _Session:
        s = sessions.get(session_id)
        if s is None:
            raise ValueError("invalid or expired session_id")
        return s

    @mcp.tool
    def handshake(team: str, client_role: str, token: str) -> dict:
        """Open a session. Requires the server's bearer token."""
        if token != valid_token:
            audit.log("auth_rejected", team=team)
            raise ValueError("invalid token")
        session_id = secrets.token_urlsafe(16)
        sessions[session_id] = _Session(team=team, client_role=client_role)
        audit.log("handshake", team=team, client_role=client_role, session=session_id)
        return {"session_id": session_id, "server_role": role.value, "team": team}

    @mcp.tool
    def send_message(session_id: str, turn: int, text: str) -> dict:
        """Deposit a free-text natural-language message for this server's agent."""
        s = _session(session_id)
        s.inbox.append({"turn": turn, "text": text})
        s.last_turn = max(s.last_turn, turn)
        audit.log("send_message", session=session_id, turn=turn, chars=len(text))
        return {"status": "ok", "queued": len(s.inbox)}

    @mcp.tool
    def receive_message(session_id: str) -> dict:
        """Fetch (and consume) the oldest pending opponent message."""
        s = _session(session_id)
        if not s.inbox:
            audit.log("receive_message", session=session_id, empty=True)
            return {"empty": True}
        msg = s.inbox.popleft()
        audit.log("receive_message", session=session_id, turn=msg["turn"])
        return {"empty": False, **msg}

    @mcp.tool
    def report_position(session_id: str, turn: int, pos: list[int]) -> dict:
        """Mutual location verification: agent registers its ground-truth position.

        Audit-only — never exposed to the opponent (partial observability stands).
        """
        s = _session(session_id)
        s.positions[turn] = (pos[0], pos[1])
        s.last_turn = max(s.last_turn, turn)
        audit.log("report_position", session=session_id, turn=turn, pos=pos)
        return {"status": "ok", "turn": turn}

    @mcp.tool
    def verify_state(session_id: str, turn: int) -> dict:
        """Integrity check: does the client's turn counter match the server's?"""
        s = _session(session_id)
        ok = turn == s.last_turn
        audit.log("verify_state", session=session_id, turn=turn, ok=ok)
        return {"ok": ok, "expected_turn": s.last_turn}

    @mcp.tool
    def get_game_config() -> dict:
        """Public resource: the game parameters this server plays by."""
        return {
            "server_role": role.value,
            "grid_size": list(config.grid_size),
            "max_moves": config.max_moves,
            "num_games": config.num_games,
            "max_barriers": config.max_barriers,
        }

    return mcp
