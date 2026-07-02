"""Cop MCP server entrypoint: `uv run python -m src.servers.cop_server`."""
from __future__ import annotations

import argparse

from src.common.config import load_config
from src.common.schemas import Role
from src.servers.base_server import create_server


def main(role: Role = Role.COP) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()
    config = load_config(args.config)
    port = config.mcp.cop_port if role is Role.COP else config.mcp.thief_port
    server = create_server(role, config)
    server.run(transport="http", host=args.host, port=port)


if __name__ == "__main__":
    main()
