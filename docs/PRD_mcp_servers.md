# PRD — MCP Servers (Track B)

> Owns: `src/servers/`. Two independent FastMCP servers: `cop_server` (:8001),
> `thief_server` (:8002). Identical codebase, role-parameterized — but deployed and run
> as **two separate processes/URLs** (hard spec requirement).

## 1. Goal

Expose the tool surface through which the orchestrator routes free-text messages and
verification calls. Servers hold **no LLM**, no strategy — only tools, message queues,
session/turn bookkeeping, and auth.

## 2. Functional requirements

1. Built with **FastMCP**; HTTP transport; port from config (`mcp.cop_port` / `mcp.thief_port`).
2. **Tool surface (frozen contract):**

| Tool | Signature | Behavior |
|---|---|---|
| `handshake` | `(team: str, role: str, token: str) -> SessionInfo` | validates bearer token; opens/attaches session |
| `send_message` | `(session_id: str, turn: int, text: str) -> ack` | enqueue free-text NL message addressed to opponent |
| `receive_message` | `(session_id: str) -> {turn, text} \| empty` | dequeue pending opponent message |
| `report_position` | `(session_id: str, turn: int, pos: [x,y]) -> ack` | mutual location verification (spec Table 4, stage 2) — used by engine for ground-truth audit, never leaked to opponent |
| `verify_state` | `(session_id: str, turn: int) -> {ok, expected_turn}` | both servers agree on turn counter |
| `get_game_config` | `() -> config slice` | resource for connecting clients (grid size, limits) |

3. **Auth (F-06)**: every tool call requires bearer token; tokens loaded from env/config;
   `revoke` supported by rotating token + server restart (documented procedure).
4. **State kept per session**: message queues (in-memory, bounded), turn counters, audit log.
5. **Transport-agnostic**: same code runs on localhost and cloud (Approach-3 hybrid ready).
6. **Structured audit log** — every tool call logged (JSONL) → README cloud-proof evidence.

## 3. Non-functional

- Startup < 2 s; tool latency budget ≤ 100 ms server-side.
- Zero knowledge of game rules (thin message bus + verification) — rules live in Track A.
- Interoperability: tool names/args stay stable for the bonus round (other teams may call us).

## 4. Acceptance criteria

- [ ] Both servers run locally on 8001/8002; `mcp` client can list & call all tools.
- [ ] Invalid/missing token ⇒ rejected with clear error; rotation procedure documented.
- [ ] Integration test: two clients exchange 50 messages, zero loss, order preserved.
- [ ] Same servers deployable to cloud with no code change (config only) — Track F takes over.
