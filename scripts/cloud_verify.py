"""Cloud acceptance battery (Track F evidence): run against the URLs in config.

Checks per server: tool listing, WRONG-token rejection (401-equivalent proof),
handshake, 50-message order/no-loss, verify_state. Writes a timestamped evidence
file to artifacts/security/.

Run: uv run python scripts/cloud_verify.py [--config config.json]
"""
from __future__ import annotations

import argparse
import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import os

from dotenv import load_dotenv

from src.common.config import load_config
from src.common.schemas import Role
from src.servers.base_server import expected_token
from src.servers.client import GameMcpClient


async def check_server(role: Role, url: str, token: str, lines: list[str]) -> bool:
    ok = True
    lines.append(f"\n=== {role.value} @ {url}")
    # 1. wrong token must be rejected
    try:
        async with GameMcpClient(url, token="definitely-wrong-token") as c:
            await c.handshake("moamteam", "probe")
        lines.append("FAIL: wrong token was ACCEPTED")
        ok = False
    except Exception as e:  # noqa: BLE001
        lines.append(f"OK  : wrong token rejected ({type(e).__name__})")
    # 2. real token: handshake + config + 50 ordered messages + verify_state
    try:
        async with GameMcpClient(url, token=token) as c:
            sid = await c.handshake("moamteam", "verifier")
            lines.append(f"OK  : handshake session {sid[:8]}...")
            gc = await c.get_game_config()
            lines.append(f"OK  : game config {gc}")
            t0 = time.time()
            for i in range(50):
                await c.send_message(i, f"order-check message {i}")
            got = []
            while True:
                m = await c.receive_message()
                if m["empty"]:
                    break
                got.append(m["turn"])
            assert got == list(range(50)), f"order broken: {got[:5]}..."
            lines.append(f"OK  : 50 messages, order preserved, {time.time()-t0:.1f}s round-trip")
            v = await c.verify_state(49)
            lines.append(f"OK  : verify_state {v}")
    except Exception as e:  # noqa: BLE001
        lines.append(f"FAIL: {type(e).__name__}: {e}")
        ok = False
    return ok


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json")
    args = parser.parse_args()
    load_dotenv()
    config = load_config(args.config)
    lines = [f"cloud_verify @ {time.strftime('%Y-%m-%d %H:%M:%S')}"]
    results = []
    for role, url in ((Role.COP, config.mcp.cop_url), (Role.THIEF, config.mcp.thief_url)):
        env = config.mcp.token_env_cop if role is Role.COP else config.mcp.token_env_thief
        token = os.environ.get(env, expected_token(role, config))
        results.append(await check_server(role, url, token, lines))
    verdict = "ALL CHECKS PASSED" if all(results) else "FAILURES PRESENT"
    lines.append(f"\n{verdict}")
    out = Path("artifacts/security")
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"cloud_verify_{time.strftime('%Y%m%d_%H%M%S')}.txt"
    path.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"\nevidence -> {path}")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    asyncio.run(main())
