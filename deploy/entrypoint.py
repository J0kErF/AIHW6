"""Cloud entrypoint: role + port from env (PaaS platforms inject PORT)."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.common.config import load_config
from src.common.schemas import Role
from src.servers.base_server import create_server


def main() -> None:
    role = Role(os.environ.get("MCP_ROLE", "cop"))
    config = load_config(os.environ.get("CONFIG_PATH", "config.json"))
    default_port = config.mcp.cop_port if role is Role.COP else config.mcp.thief_port
    port = int(os.environ.get("PORT", default_port))
    server = create_server(role, config)
    server.run(transport="http", host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
