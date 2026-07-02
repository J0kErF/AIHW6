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
- **LLM = DeepSeek** (user, 2026-07-02): key copied from `../aihw4/.env` into `aihw6/.env`
  as `DEEPSEEK_API_KEY` (gitignored). OpenAI-compatible, base_url `https://api.deepseek.com/v1`,
  model `deepseek-chat`, balance was ~$1.80. Latency can spike to ~35s/call → turn_timeout_s=180,
  client request timeout 45s, max_tokens 256.

## 📊 Status Snapshot (update the cell, keep the table)

| Item | Status | Last verified |
|---|---|---|
| Foundation docs + plan (27 files) | ✅ committed `f4e7a47` | 2026-07-02 |
| Track A — engine (`src/engine`, `src/common`) | ✅ DONE — 21 tests, all ladder grids | 2026-07-02 |
| Track B — MCP servers (`src/servers`) | ✅ DONE — 6 tests + live HTTP smoke :8001 (handshake/messages/401) | 2026-07-02 |
| Track C — agents/orchestrator | ✅ core done — 14 tests + REAL DeepSeek 2×2 series (0 tech losses/fallbacks); open: real-LLM 3×3–5×5 runs, optional Q-learn | 2026-07-02 |
| Track D — GUI | 🔵 core done (render/PNG/replay-roundtrip, 4 tests); live window + pause/step + replay CLI pending | 2026-07-02 |
| Track E — reporting/Gmail | 🔵 code done (5 tests, schemas byte-match spec); E1 Google Cloud setup MANUAL, not done | 2026-07-02 |
| Track F — cloud deploy | 🔵 fully scripted (Dockerfile+render.yaml+runbook+verify battery passed locally); BLOCKED on user: Render account (~2 min) | 2026-07-02 |
| Real-LLM 5×5 rehearsal over :8001/:8002 | ✅ cop 90 : thief 40, 166 turns, 0 tech losses | 2026-07-02 |
| Analysis: vision sweep + Q-learn curve | ✅ `artifacts/analysis/` | 2026-07-02 |
| README scientific report | ✅ v1 complete with real data (refresh cloud §6 after deploy) | 2026-07-02 |
| Local E2E (SP-3) | ⬜ | — |
| Cloud E2E + evidence | ⬜ | — |
| README scientific report | 🟡 skeleton only | 2026-07-02 |
| Final email + submission | ⬜ | — |

## 🧭 Decisions Log (why-record; newest first)

- 2026-07-02 — Rule interpretations (documented in `src/engine/engine.py` docstring, must
  reach README): (1) the 25-move cap counts completed ROUNDS (thief+cop both acted);
  (2) capture is symmetric — either agent ending on the opponent's cell = cop wins;
  (3) barrier cell blocks entry for both, cop may leave it; (4) a fully walled-in agent
  plays `Pass` (only legal with zero legal actions) so the game always progresses.
- 2026-07-02 — MCP auth model: bearer token at `handshake` only; returned session_id is
  the capability for later calls; token rotation via env var = revoke. Why: transport-
  agnostic, testable in-memory, satisfies spec token+revoke requirement.
- 2026-07-02 — GUI tech: pygame-ce; Surface-only rendering (no display) so one code path
  serves live window, headless cloud, and PNG evidence.

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

Only TWO user-manual steps remain; everything else is scripted:
1. **USER: Render.com account** (~2 min, GitHub login) → follow `docs/RUNBOOK_cloud.md`
   §1 (Blueprint deploy from repo → set 2 token env vars → paste 2 URLs into config.json)
   → then run `uv run python scripts/cloud_verify.py` and
   `uv run python -m src.orchestrator --no-email` (cloud E2E) — archive outputs.
2. **USER: Google Cloud OAuth** (~15 min, browser): `docs/ENVIRONMENT.md` §5 → download
   credentials.json → set GOOGLE_CREDENTIALS_PATH/GOOGLE_TOKEN_PATH in .env → run
   `uv run python -m src.reporting.smoke` (creates a DRAFT; browser consent once).
3. After both: refresh README §6 cloud lines, GRADING_RUBRIC self-audit, final graded
   run with dry_run=false, push to the user-provided GitHub URL, share with
   rmisegal@gmail.com, fill moamteam-ex06.pdf.

## 📝 Session Log (newest first)

### 2026-07-02 — Wave 3: rehearsal, analysis, cloud kit, README (Claude, main chat)
- VERIFIED: real-LLM 5×5 series over REAL HTTP servers :8001/:8002 — cop 4 : thief 2
  (two thief move-limit escapes, one barrier), totals 90:40, 166 turns, 0 technical
  losses, 2 guarded fallbacks, 166/166 verify_state OK. Transcript (mean belief err 0.89,
  35% exact inference): `artifacts/transcripts/deepseek_5x5_transcript.md`; 6 PNGs.
  Gotcha fixed en route: config MCP URLs needed the `/mcp` path suffix (FastMCP default).
- VERIFIED: vision-radius sweep (mock agents, 12 games/cell): belief err 5×5
  1.61→0.75→0.12→0 for r=1..4; CSV+plot in `artifacts/analysis/`.
- VERIFIED: tabular Q-learning (C6): 2000 self-play episodes, mean reward 6.81→14.81;
  curve PNG + qtable .npy + QPolicy class (`src/agents/qlearn.py`).
- Cloud kit prepared (F2/F3): `deploy/Dockerfile`+`entrypoint.py`, `render.yaml`
  blueprint, `docs/RUNBOOK_cloud.md`, `scripts/cloud_verify.py` (battery PASSED against
  live local servers — evidence `artifacts/security/cloud_verify_20260702_133253.txt`).
- README rewritten as full scientific report v1 with all real numbers.
- 50 tests green; matplotlib added. Remaining manual: Render account, Google OAuth.

### 2026-07-02 — Wave 2: Track C + DeepSeek (Claude, main chat)
- Built `src/agents/` (llm_adapter with anthropic/deepseek/openai/mock providers, persona
  prompt files, defensive parser + repair, BeliefGrid, heuristic guard, LlmAgent) and
  `src/orchestrator.py` (async loop over two MCP clients, turn timeout → TechnicalLoss,
  JSONL turn log, PNG per sub-game, report + optional Gmail; CLI --grid/--mock-llm/
  --no-email/--in-memory). Added `src/gui/replay.py` (D7).
- User directive: use DeepSeek key from previous HW → found in `../aihw4/.env`, copied to
  `aihw6/.env` (verified gitignored). Config switched to deepseek/deepseek-chat.
- VERIFIED: 50 pytest green (14 new: parser/belief/guard + mock E2E ladder 2×2–5×5 through
  real in-memory MCP servers, incl. free-language anti-coordinate-protocol test).
- VERIFIED: REAL DeepSeek autonomous series on 2×2 (--in-memory --no-email): 6/6 valid
  sub-games, 0 technical losses, 0 fallbacks, verify_ok all turns, spec-shaped report JSON
  (cop 120 / thief 30 — 2×2 is trivially cop-favored, expected). Transcript with real
  banter/deception saved: `artifacts/transcripts/deepseek_2x2_transcript.md`.
- Learned: first DeepSeek run hit 35s/call latency → one turn > 60s timeout → pipeline
  correctly VOIDED it (technical-loss path proven in production). Tuned: turn_timeout_s
  180, request timeout 45s, max_tokens 256.
- SP-3 posted GREEN → Track F unblocked. Open: real-LLM 3×3/4×4/5×5 rehearsals, E1 Google
  setup (user), Q-learn (optional), cloud deploy.

### 2026-07-02 — Wave 1 implementation (Claude, main chat)
- Track A VERIFIED: `src/common/` (config loader, schemas=SP-1, logging) + `src/engine/`
  (board, engine, series, errors); 21 tests green incl. full ladder 2×2→5×5, weird-config
  no-hardcode proof, technical-loss void+rerun.
- Track B VERIFIED: `src/servers/` (base_server factory, cop/thief entrypoints, typed
  async client); 6 in-memory tests + real HTTP smoke on :8001 (handshake, config, message
  round-trip, wrong token → ToolError). Audit JSONL confirmed.
- Track E code VERIFIED by 5 tests (report keys byte-match spec §9.1/§9.2, pure-JSON body,
  6-sub-game + totals guards). `auth.py`/`gmail_sender.py`/`smoke.py` are CLAIMED —
  cannot run until E1 Google setup (manual). Sender defaults to DRAFT (dry_run=true).
- Track D core VERIFIED: pygame-ce Surface renderer + message-feed panel + PNG export +
  JSONL replay round-trip; 4 tests; evidence PNG at `artifacts/screenshots/demo_final_5x5.png`.
- Full suite: **36 passed**. Total runtime deps installed via uv (py 3.13).
- NOT done: orchestrator/LLM (Track C), live GUI window, Google Cloud project, cloud deploy.

### 2026-07-02 — foundation agent (Claude, main chat)
- Created full foundation: `docs/` (declaration, rules, architecture, environment, PRD +
  6 sub-PRDs, reporting spec, testing, rubric), `plan/` (PLAN, TODO, TASK_BOARD, tracks
  A–F), `config.json`, README skeleton, `CLAUDE.md`, `.gitignore`. VERIFIED files exist.
- Filled team identity from `moamteam-ex05.pdf`; waived bonus everywhere; git init on
  `main`, commit `f4e7a47` (27 files). VERIFIED via `git log`.
- No source code exists yet — `src/`, `tests/`, `pyproject.toml` are still to be created.
