# PRD — Master Product Requirements · HW6 "Cop & Thief over MCP"

> Version 1.0 · Owner: moamteam · Grade target: **98%+** (see `GRADING_RUBRIC.md`)

## 1. Product vision

A fully autonomous dual-agent pursuit system: two LLM-driven agents (Cop, Thief) that
negotiate a partially-observable grid chase **purely through free natural-language
messages routed over two MCP servers**, run 6 valid sub-games end-to-end without human
intervention, visualize the chase live, and automatically email a machine-readable JSON
report to the grader.

## 2. Users

- **Grader (Dr. Segal / automated checker)** — receives JSON-only email; reads scientific README; may probe our public MCP URLs.
- **Opposing team (bonus)** — connects their agents to our cloud MCP servers.
- **Us (developers)** — need reproducible local runs, sanity ladder, clear logs.

## 3. Functional requirements (traceable IDs)

| ID | Requirement | Source | Sub-PRD |
|---|---|---|---|
| F-01 | Grid game engine, generic size from config, 8-dir movement, turn-based (thief first), state machine | spec §4.2 | PRD_game_engine |
| F-02 | Capture / 25-move survival win conditions; scoring 20/10/5/5 from config | spec §4.3–4.4 | PRD_game_engine |
| F-03 | Cop barriers: on current cell, block both, max 5, cop-only | spec §4.3 | PRD_game_engine |
| F-04 | Sub-game (≤25 moves) / game (6 valid sub-games) accounting, technical-loss rerun | spec §4.1, §9 | PRD_game_engine |
| F-05 | Two independent FastMCP servers (cop/thief) exposing message + verification tools | spec §5 | PRD_mcp_servers |
| F-06 | Token-based auth on both servers, revocable | spec §6 | PRD_cloud_security |
| F-07 | Free natural-language inter-agent messages; interpretation via LLM; deception allowed | spec §5.1 | PRD_agents_llm |
| F-08 | MCP client (orchestrator) owns LLM calls; server never hosts the LLM | spec §5.2 | PRD_agents_llm |
| F-09 | Decision mechanism: heuristic baseline; optional Tabular Q-Learning (Bellman, ε-greedy) | spec §8 | PRD_agents_llm |
| F-10 | Partial observability: vision radius, belief tracking from messages | spec §2, §11 | PRD_agents_llm |
| F-11 | GUI: real-time board, agents, barriers, message feed | spec §13 stage 6 | PRD_gui |
| F-12 | Local full run (localhost, ports 8001/8002) then cloud deploy with 2 public URLs | spec §6 | PRD_cloud_security |
| F-13 | Automated Gmail report: cop agent sends single email, JSON-only body, to rmisegal+uoh26b@gmail.com after 6 valid sub-games | spec §9 | PRD_reporting_gmail |
| F-14 | Internal + bonus JSON schemas exactly as specified | spec §9.1–9.2 | REPORTING_SPEC |
| F-15 | Central config.json — zero hard-coded parameters | spec §10 | all |
| F-16 | Scientific README: Dec-POMDP model, orchestration-challenge analysis, visual proofs, cloud CLI logs | spec §11 | README |
| F-17 | Sanity ladder 2×2 → 5×5 runnable at any time | spec §4.5 | TESTING |
| F-18 | Bonus: inter-group cloud series, role swap 3+3, mutual-agreement dual reporting | spec §12 | PRD_cloud_security + REPORTING_SPEC |

## 4. Non-functional requirements

| ID | Requirement |
|---|---|
| N-01 | Fully autonomous run: zero manual intervention from start to sent email |
| N-02 | Deterministic engine given a seed (`config.random_seed`) — reproducible tests |
| N-03 | Structured logs (JSONL + human CLI) sufficient as README evidence |
| N-04 | Secrets never committed; `.env` + external secrets folder |
| N-05 | Each turn ≤ configurable timeout; technical failures detected → sub-game voided & re-run |
| N-06 | Public GitHub repo, clean history, meaningful commits |
| N-07 | Code quality: typed Python, `pydantic` schemas, tests green (`pytest`) |

## 5. Sub-PRD index

- `PRD_game_engine.md` — Track A
- `PRD_mcp_servers.md` — Track B
- `PRD_agents_llm.md` — Track C
- `PRD_gui.md` — Track D
- `PRD_reporting_gmail.md` — Track E
- `PRD_cloud_security.md` — Track F
- `REPORTING_SPEC.md` — frozen JSON contracts (shared)

## 6. Milestones (map to plan/PLAN.md phases)

M1 engine green on 2×2 → M2 local MCP loop → M3 full local 5×5 autonomous game →
M4 NL + strategy quality pass → M5 GUI → M6 cloud URLs live + secured →
M7 Gmail automation verified → M8 README + evidence → M9 (bonus) inter-group series.

## 7. Out of scope

Deep RL / neural nets; MCP for Google services (video shows it exists — we use plain API);
production-grade user management; game strategy perfection.
