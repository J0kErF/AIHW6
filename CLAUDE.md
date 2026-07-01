# CLAUDE.md — Operating Instructions for AI Agents in aihw6

## What this project is
HW6: two autonomous LLM agents (Cop/Thief) playing grid pursuit, coordinating ONLY via
free natural-language messages over two FastMCP servers; fully autonomous through an
auto-emailed JSON report. Grade target 98%+.

## Read order (before writing any code)
0. **`AGENT_MEMORY.md` — ALWAYS FIRST.** Shared cross-chat memory: ground truth, current
   status, decisions, blockers, next actions. Follow its read/update protocol.
1. `docs/HW6_DECLARATION.md` — what/grounds/deliverables
2. `docs/GAME_RULES.md` — normative rules (code that disagrees = bug)
3. Your track file in `plan/tasks/TRACK_*.md` + its PRD in `docs/`
4. `plan/TASK_BOARD.md` — ownership, sync points, status protocol

## Before ending any work session
Update `AGENT_MEMORY.md` per its rules: session-log entry (VERIFIED vs CLAIMED), status
snapshot cells you changed, any new decisions/blockers. An unlogged session = lost work
for the next chat.

## Hard rules (violations lose grade points — spec-mandated)
- **No hard-coded parameters.** Everything through `config.json` via `src/common/config.py`.
- **LLM never inside MCP servers.** Servers expose tools only.
- **Agents never exchange raw coordinates as protocol.** Free natural language only.
- **Email body = JSON only.** Exactly 6 valid sub-games; technical losses void & re-run.
- **Secrets never committed.** `.env`, `credentials.json`, `token.json` stay out of git.

## Multi-agent work protocol
- One agent per track; touch ONLY paths owned by your track (`plan/TASK_BOARD.md` table).
- Contracts (`GAME_RULES.md`, `REPORTING_SPEC.md`, PRD interfaces) are frozen: to change
  one, update the doc FIRST and log it under "Contract changes" on the TASK_BOARD.
- Update your track file checkboxes + TASK_BOARD status when starting/finishing work.
- Commit prefix: `[A]`…`[F]` per track. Keep `uv run pytest` green on main.

## Conventions
- Python ≥3.11, uv-managed, typed, pydantic schemas in `src/common/schemas.py` (Track A owns).
- Logging via `src/common/logging.py` → JSONL in `artifacts/logs/` + console.
- Tests in `tests/<track>/`; sanity ladder grids 2×2→5×5 must always pass config-only.
- Windows host: PowerShell-safe commands in docs; paths may contain spaces — quote them.
