# TRACK C — Agents, LLM & Orchestrator

> Read first: `docs/PRD_agents_llm.md`, `docs/GAME_RULES.md` §7–8, `docs/ARCHITECTURE.md` §4.
> You own `src/agents/`, `src/orchestrator.py`, `tests/orchestrator/`.
> **Start gate:** SP-1 + SP-2 frozen on TASK_BOARD. Until then: write personas/prompts and
> the LLM adapter against mocks.

## Mission
The autonomous loop that is the assignment's core: LLM personas exchanging free natural
language over MCP, inferring positions under partial observability, acting legally, for
6 valid sub-games without a human.

## Tasks
- [x] C1. `agents/llm_adapter.py` — provider-agnostic (`anthropic` first), config-driven
       model/temp/tokens, retries+timeout, per-call cost/latency JSONL.
- [x] C2. `agents/personas/` — cop & thief system prompts (files, not code): role, goal,
       rules digest, output contract `{"action","message","belief","reasoning"}`; explicit
       permission to deceive; forbid raw-coordinate message conventions.
- [x] C3. `agents/parser.py` — defensive JSON extraction; 1 repair round-trip; fallback to heuristic.
- [x] C4. `agents/belief.py` — belief grid: init uniform; update from vision, message
       interpretation (LLM-extracted hints), 1-step motion constraint; expose accuracy metric.
- [x] C5. `agents/strategy.py` — heuristic baseline (Chebyshev pursuit/evasion + barrier
       value); legality guard using `Engine.legal_actions`.
- [ ] C6. `agents/qlearn.py` — optional Tabular Q-Learning (Bellman, ε-greedy, params from
       config); self-play trainer; learning-curve CSV export. (Differentiator — do after C8.)
- [x] C7. `orchestrator.py` — full loop: handshake both servers → per-turn
       (receive msg → LLM decide → validate → apply → send msg → GUI event → verify_state)
       → sub-game end → series accounting → Reporter trigger. Turn timeout + technical-loss
       voiding. CLI flags: `--config --grid --mock-llm --dry-run`.
- [ ] C8. E2E local: mock-LLM 2×2 (ladder 1) → real LLM 3×3 (ladder 2) → 4×4 ambiguity run
       (ladder 3, log belief accuracy vs vision radius) → 5×5 full series (ladder 4).
- [ ] C9. Capture a transcript showing deception + successful inference → `artifacts/transcripts/`.
- [ ] C10. **Post SP-3 GREEN** on TASK_BOARD (unblocks Track F).

## Definition of Done
`uv run python -m src.orchestrator --config config.json` completes 6 valid sub-games
unattended with real LLM locally; transcripts human-verified as free-form; belief metrics
logged; tests green.
