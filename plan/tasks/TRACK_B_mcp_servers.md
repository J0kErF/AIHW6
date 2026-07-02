# TRACK B — MCP Servers (FastMCP × 2)

> Read first: `docs/PRD_mcp_servers.md` (tool contract), `docs/ARCHITECTURE.md` §5–7.
> You own `src/servers/`, `tests/mcp/`. Contract SP-2 is pre-frozen — refine only before
> Track C's first commit, and log any change on the TASK_BOARD.

## Mission
Two independent, role-parameterized FastMCP servers (cop :8001, thief :8002): message bus
+ turn verification + token auth. No game rules, no LLM.

## Tasks
- [x] B1. Add `fastmcp` + `mcp` deps (coordinate pyproject edit with Track A — single PR).
- [x] B2. `src/servers/base_server.py` — shared FastMCP app factory: role, port, token from
       config/env; session store; bounded message queues; JSONL audit log.
- [x] B3. Tools: `handshake`, `send_message`, `receive_message`, `report_position`,
       `verify_state`, `get_game_config` — exact signatures per PRD §2.
- [x] B4. Auth middleware: bearer token check on every call; env var per role
       (`MCP_COP_TOKEN`, `MCP_THIEF_TOKEN`); documented rotation (= revoke) procedure.
- [x] B5. Entrypoints `cop_server.py` / `thief_server.py` (`uv run python -m src.servers.cop_server`).
- [x] B6. Client helper `src/servers/client.py` — thin typed wrapper the orchestrator uses
       (connect(url, token), call tools) — works for OUR servers and any conforming team's.
- [x] B7. Tests: auth reject/accept; 50-message order/loss test between two client sessions;
       `verify_state` divergence detection; restart resilience (queues empty, session re-handshake).
- [x] B8. Confirm identical code path runs with public URL config (no localhost assumptions,
       no hardcoded ports) — Track F will deploy it untouched.

## Definition of Done
Both servers run locally; `tests/mcp` green; audit JSONL produced; client helper consumed
by Track C without questions; TASK_BOARD updated.
