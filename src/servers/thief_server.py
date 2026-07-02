"""Thief MCP server entrypoint: `uv run python -m src.servers.thief_server`."""
from __future__ import annotations

from src.common.schemas import Role
from src.servers.cop_server import main

if __name__ == "__main__":
    main(role=Role.THIEF)
