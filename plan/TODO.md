# TODO — Global Checklist (mirror of phases; tick here only when track DoD met)

## Foundation (this commit)
- [x] Read spec PDF + Google guide + both video transcripts
- [x] docs/: declaration, rules, architecture, environment, PRDs, reporting spec, testing, rubric
- [x] plan/: PLAN, TODO, TASK_BOARD, 6 track files
- [x] config.json initial (all spec parameters)
- [x] `git init` + foundation commit (LOCAL only — user provides GitHub repo URL at the end, then push)
- [x] Real student names/ids in config.json + REPORTING_SPEC (from moamteam-ex05: Mohammad Yosef [REDACTED], Amear Abu Farekh [REDACTED])
- [x] Bonus decision: **WAIVED** — bonus window closed for students; P10 dropped
- [ ] Confirm final repo URL (provisional: https://github.com/J0kErF/AIHW6, pattern from AIHW5) → update config.json if different → push

## P1 — Engine (Track A)
- [ ] pyproject.toml (uv) + src skeleton + pydantic config loader
- [ ] Board/state/actions/validation + barriers + terminal detection + scoring
- [ ] SeriesManager (6 valid sub-games, technical-loss rerun)
- [ ] Observation builder (vision radius)
- [ ] Unit tests all grid sizes; ladder stage 1 (2×2) green

## P2 — MCP servers (Track B)
- [ ] cop_server + thief_server (FastMCP, :8001/:8002), role-parameterized
- [ ] Tools: handshake, send/receive_message, report_position, verify_state, get_game_config
- [ ] Bearer-token auth + rotation procedure + audit JSONL
- [ ] 50-message integration test green

## P3–P5 — Orchestrator, strategy, NL (Track C)
- [ ] LLM adapter (provider from config, retries, cost log)
- [ ] Personas + JSON action output + repair + heuristic fallback
- [ ] Belief grid + motion-constraint update
- [ ] Full autonomous local series (mock LLM → real LLM), ladder stages 2–3
- [ ] Heuristic baseline; optional Q-Table + learning-curve export
- [ ] Deception/ambiguity demonstrated in transcripts

## P6 — GUI (Track D)
- [ ] Tech pick recorded in PRD_gui; renderer on TurnResult events
- [ ] Live board any grid size + message feed + score header
- [ ] PNG auto-export per sub-game + summary; headless default

## P7 — Cloud & security (Track F)
- [ ] Platform account + deploy scripts; 2 public HTTPS URLs
- [ ] Tokens live + 401 evidence + revoke drill
- [ ] External-network verification + cloud E2E series + logs archived

## P8 — Reporting (Track E)
- [ ] Google Cloud project: Gmail+Calendar APIs enabled, OAuth screen, scopes, Desktop client, test users
- [ ] credentials.json + token.json in external secrets dir; auth flow tested
- [ ] Report builder (internal + bonus schemas) + validity guard (exactly 6)
- [ ] Draft-mode e2e → real send to ourselves → wire recipient from config

## P9 — Submission
- [ ] README.md scientific report (Dec-POMDP, challenges, proofs) complete
- [ ] Artifacts: GUI PNGs, cloud CLI logs, curves, 401 proof
- [ ] GRADING_RUBRIC self-audit — every box, target ≥98
- [ ] Final autonomous run → real email to rmisegal+uoh26b@gmail.com
- [ ] Push to GitHub repo (URL from user), share with rmisegal@gmail.com (standing instruction #1)
- [ ] Repo contains PRD/PLAN/TODO markdown folder + root README (standing instruction — submit.txt)
- [ ] Fill submission PDF template per member (`moamteam-ex06.pdf`), honest self-score
- [ ] Tag `submission-hw6`

## P10 — Bonus — ~~WAIVED~~ (window closed for students; tasks dropped)
