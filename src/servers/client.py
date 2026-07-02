"""Typed async client wrapper over any conforming MCP game server.

Works against a URL (local, cloud, or another team's server — bonus interop)
or an in-memory FastMCP instance (tests). Used by the orchestrator (Track C).
"""
from __future__ import annotations

import json
from typing import Any

from fastmcp import Client


def _payload(result: Any) -> dict:
    data = getattr(result, "data", None)
    if isinstance(data, dict):
        return data
    content = getattr(result, "content", None)
    if content:
        return json.loads(content[0].text)
    raise ValueError(f"cannot decode tool result: {result!r}")


class GameMcpClient:
    def __init__(self, target: Any, token: str) -> None:
        self._client = Client(target)
        self._token = token
        self.session_id: str | None = None

    async def __aenter__(self) -> "GameMcpClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *exc) -> None:
        await self._client.__aexit__(*exc)

    async def _call(self, tool: str, **args: Any) -> dict:
        return _payload(await self._client.call_tool(tool, args))

    async def handshake(self, team: str, client_role: str) -> str:
        res = await self._call(
            "handshake", team=team, client_role=client_role, token=self._token
        )
        self.session_id = res["session_id"]
        return self.session_id

    async def send_message(self, turn: int, text: str) -> dict:
        return await self._call(
            "send_message", session_id=self.session_id, turn=turn, text=text
        )

    async def receive_message(self) -> dict:
        return await self._call("receive_message", session_id=self.session_id)

    async def report_position(self, turn: int, pos: tuple[int, int]) -> dict:
        return await self._call(
            "report_position", session_id=self.session_id, turn=turn, pos=list(pos)
        )

    async def verify_state(self, turn: int) -> dict:
        return await self._call("verify_state", session_id=self.session_id, turn=turn)

    async def get_game_config(self) -> dict:
        return await self._call("get_game_config")
