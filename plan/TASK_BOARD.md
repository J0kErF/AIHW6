# TASK_BOARD — Multi-Agent Parallel Work Board

> Protocol: one agent per track. An agent touches ONLY its owned paths. Cross-track needs
> go through the frozen contracts (docs/) — if a contract must change, stop, update the
> doc first, note it here under "Contract changes", then continue.
> Status legend: ⬜ todo · 🔵 in-progress · ✅ done · ⛔ blocked (name the blocker)

## Tracks & ownership

| Track | Agent role | Owned paths | Task file | Status | Blocked by |
|---|---|---|---|---|---|
| A | Engine dev | `src/engine/`, `src/common/`, `tests/engine/` | `tasks/TRACK_A_game_engine.md` | ✅ 2026-07-02 (21 tests) | — |
| B | MCP dev | `src/servers/`, `tests/mcp/` | `tasks/TRACK_B_mcp_servers.md` | ✅ 2026-07-02 (6 tests + live :8001 HTTP smoke) | — |
| C | Agents/LLM dev | `src/agents/`, `src/orchestrator.py`, `tests/orchestrator/` | `tasks/TRACK_C_agents_llm.md` | ⬜ **UNBLOCKED** | needs LLM API key (ask user) |
| D | GUI dev | `src/gui/`, `artifacts/` | `tasks/TRACK_D_gui.md` | 🔵 core done (render/export/replay; live window untested, no pause/step yet) | — |
| E | Reporting dev | `src/reporting/`, secrets setup (out of repo) | `tasks/TRACK_E_reporting_gmail.md` | 🔵 code done (5 tests); E1 Google Cloud setup + OAuth run pending (manual, with user) | E1 user session |
| F | Cloud/sec ops | `deploy/`, `docs/RUNBOOK_cloud.md` | `tasks/TRACK_F_cloud_security.md` | ⬜ | SP-3 (local E2E) |

## Wave plan

- **Wave 1 (now, 4 agents parallel):** A, B, D (mock events), E (Google setup + builder).
- **Wave 2:** C (after A & B freeze interfaces — they must post "SP-1/SP-2 FROZEN" here).
- **Wave 3:** F (after C posts "SP-3 GREEN"), then all-hands P9 README.

## Sync-point log

| SP | Status | Posted by | Date |
|---|---|---|---|
| SP-0 config/rules/report schemas | ✅ frozen (docs committed) | foundation | 2026-07-02 |
| SP-1 engine interfaces | ✅ FROZEN — `src/common/schemas.py` + `Engine`/`SeriesManager`/`Policy` in `src/engine/` | Track A | 2026-07-02 |
| SP-2 MCP tool signatures | ✅ FROZEN — implemented in `src/servers/base_server.py`, client wrapper `src/servers/client.py` | Track B | 2026-07-02 |
| SP-3 local E2E green | ⬜ (Track C next: orchestrator + LLM) | | |

## Contract changes

- **2026-07-02 — Bonus (P10 / spec §12) WAIVED**: bonus window closed for students.
  Affected: Track F (F8 dropped), Track E (E8 bonus builder is now low priority /
  interop-proof only). Internal-report path unchanged.
- **2026-07-02 — Git policy**: local repository only; user provides the GitHub URL at the
  end → update `config.json.identity.github_repo` if it differs from the provisional
  `https://github.com/J0kErF/AIHW6`, then push and share with `rmisegal@gmail.com`.

## Shared conventions (all agents)

- Python ≥3.11, typed, pydantic models in `src/common/schemas.py` (Track A owns the file;
  others request additions via this board).
- All constants via `Config` object — a PR adding a magic number fails review.
- Logging: `src/common/logging.py` → JSONL to `artifacts/logs/` + rich console.
- Tests colocated per track (`tests/<track>/`); `uv run pytest` must stay green on main.
- Commit prefix per track: `[A] …`, `[B] …`, etc.
