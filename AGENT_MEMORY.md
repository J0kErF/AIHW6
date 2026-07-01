# AGENT_MEMORY — Shared State for AI Agents (cross-chat, cross-agent)

> **Purpose:** this file is the single shared memory between chat sessions and between
> parallel agents. A brand-new chat pointed at this folder should be productive after
> reading ONLY this file (then follow its pointers). It records *state and decisions*,
> not documentation — docs live in `docs/`, tasks in `plan/`.

---

## 🤖 RULES FOR THE AI — when and how to update this file

**Read protocol (every new session):**
1. Read this file FIRST, top to bottom.
2. Then read `CLAUDE.md` (hard rules) and your track file in `plan/tasks/` if assigned.
3. Trust this file over your assumptions, but verify claims that code can prove
   (e.g. "tests green" → run `uv run pytest`) before building on them.

**Update protocol — you MUST update this file when any of these happens:**
| Trigger | What to write |
|---|---|
| You finish a work session / long task | One entry in **Session Log** (date, agent/track, what changed, what's verified vs untested) |
| You make a decision not already in docs/ | One line in **Decisions Log** with the why |
| You get blocked or find a contradiction | Entry in **Blockers & Open Questions** |
| You change a frozen contract | Update `plan/TASK_BOARD.md` "Contract changes" AND note it here in the session entry |
| Status of a phase/track flips (started/green/broken) | Update the **Status Snapshot** table |
| User gives new facts (deadlines, URLs, credentials location, scope changes) | Update **Ground Truth** immediately — this outranks everything else |

**How to write here:**
- Append; never rewrite history. Newest session entries on TOP of the Session Log.
- Absolute dates (`2026-07-02`), never "today"/"yesterday".
- Terse but complete sentences — a cold-start agent must understand with zero context.
- State verification level honestly: `VERIFIED` (ran it) vs `CLAIMED` (wrote it, didn't run).
- Keep the file under ~200 lines: when Session Log grows past ~15 entries, compress the
  oldest into one "archive summary" line each. Never compress Ground Truth or Decisions.
- Never put secrets here (no keys, tokens, passwords — paths/env-var names only).

---

## 📌 Ground Truth (user-provided facts — highest authority)

- Team: **moamteam** — Mohammad Yosef ([REDACTED]), Amear Abu Farekh ([REDACTED]).
- Assignment: ex06 "Dual AI agent race via MCP servers" (spec PDF in parent folder).
- Grade target: **98%** → treat spec "recommended" items as mandatory (see `docs/GRADING_RUBRIC.md`).
- **Bonus is WAIVED** (window closed for students — user confirmed 2026-07-02). Do not build bonus features.
- Git: **local repo only**; user will provide the GitHub URL at the end → then push and
  share with `rmisegal@gmail.com`. Provisional URL in config: `https://github.com/J0kErF/AIHW6`.
- Report email target: `rmisegal+uoh26b@gmail.com`, JSON-only body, sent automatically.
- User's email: mohammad@mryosef.com. Environment: Windows 11, PowerShell, uv, Python ≥3.11.

## 📊 Status Snapshot (update the cell, keep the table)

| Item | Status | Last verified |
|---|---|---|
| Foundation docs + plan (27 files) | ✅ committed `f4e7a47` | 2026-07-02 |
| Track A — engine (`src/engine`, `src/common`) | ⬜ not started | — |
| Track B — MCP servers (`src/servers`) | ⬜ not started | — |
| Track C — agents/orchestrator | ⬜ not started (gate: SP-1+SP-2) | — |
| Track D — GUI | ⬜ not started | — |
| Track E — reporting/Gmail | ⬜ not started (Google Cloud project NOT yet created) | — |
| Track F — cloud deploy | ⬜ not started (gate: SP-3) | — |
| Local E2E (SP-3) | ⬜ | — |
| Cloud E2E + evidence | ⬜ | — |
| README scientific report | 🟡 skeleton only | 2026-07-02 |
| Final email + submission | ⬜ | — |

## 🧭 Decisions Log (why-record; newest first)

- 2026-07-02 — LLM: Approach 1 (cloud API, Anthropic first) primary; Approach 3 (hybrid)
  for cloud phase; Ollama documented only. Why: spec recommends, zero exposure risk.
- 2026-07-02 — Ports 8001 (cop) / 8002 (thief); thief moves first; vision_radius default 2.
  Why: spec + config-driven defaults; radius < board makes partial observability real.
- 2026-07-02 — Bonus waived; P10/F8 dropped. Why: window closed (user).
- 2026-07-02 — Multi-agent work split into tracks A–F with path ownership + frozen
  contracts (`plan/TASK_BOARD.md`). Why: parallel agents without merge conflicts.

## 🚧 Blockers & Open Questions

- (open) Final GitHub repo URL — waiting on user at submission time.
- (open) LLM API key availability: which provider key does the team actually have?
  Affects `config.llm` — currently set to Anthropic/claude-haiku. Ask user before Track C E2E.
- (open) Google Cloud project for Gmail API not created yet — Track E task E1 is manual
  (browser); needs the user or a guided session.

## ▶️ Next Actions (whoever reads this next)

1. Kick off **Wave 1** (parallel): Track A (engine+commons), Track B (MCP servers),
   Track D (GUI vs mock events), Track E (report builder vs fixtures; E1 Google setup with user).
2. Track A must post "SP-1 FROZEN" on `plan/TASK_BOARD.md` ASAP — it unblocks Track C.
3. After each track session: tick boxes in its `plan/tasks/TRACK_*.md`, update TASK_BOARD
   status, and log a session entry below.

## 📝 Session Log (newest first)

### 2026-07-02 — foundation agent (Claude, main chat)
- Created full foundation: `docs/` (declaration, rules, architecture, environment, PRD +
  6 sub-PRDs, reporting spec, testing, rubric), `plan/` (PLAN, TODO, TASK_BOARD, tracks
  A–F), `config.json`, README skeleton, `CLAUDE.md`, `.gitignore`. VERIFIED files exist.
- Filled team identity from `moamteam-ex05.pdf`; waived bonus everywhere; git init on
  `main`, commit `f4e7a47` (27 files). VERIFIED via `git log`.
- No source code exists yet — `src/`, `tests/`, `pyproject.toml` are still to be created.
