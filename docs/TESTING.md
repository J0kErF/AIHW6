# TESTING — Sanity Ladder & Acceptance Strategy

> Spec §4.5 mandates gradual sanity checks across grid sizes. This is also our
> integration-risk firewall: every phase lands only after its ladder stage is green.

## 1. The ladder (spec Table 2)

| Stage | Grid | What we validate | Gate for |
|---|---|---|---|
| 1 | 2×2 | engine rules, pipeline integration, message transfer correctness | Phase 2 (MCP loop) |
| 2 | 3×3 / 3×2 | coordination convergence, hyper-parameter calibration, failure identification | Phase 4 (strategy) |
| 3 | 4×4 / 4×3 | observation-ambiguity effects; initial distance vs vision radius | Phase 5 (NL quality) |
| 4 | 5×5 | final test run, graph generation, whole-game analysis | Phase 8 (submission) |

## 2. Test pyramid

### Unit (Track A mostly)
- Move legality on every grid size (bounds, diagonals, barriers).
- Barrier: cop-only, current-cell-only, quota 5, blocks both.
- Terminal detection: capture, 25-move cap; scoring table from config.
- Config: schema validation, missing-key rejection, no-hardcode grep test.

### Integration
- MCP: handshake/auth, 50-message exchange, order & loss, turn verification (`verify_state`).
- LLM adapter: mocked provider — malformed JSON output → repair → fallback path.
- Orchestrator: full sub-game with scripted (mock) LLM on 2×2; deterministic seed.
- Technical-loss: kill a server mid-sub-game → sub-game voided → re-run → still 6 valid.

### End-to-end
- E2E-L: full 6-sub-game series, localhost, real LLM, GUI headless, report built (draft mode).
- E2E-C: same against cloud URLs from external network; CLI logs captured to `artifacts/logs/`.
- E2E-Mail: Gmail draft contains pure JSON; then one real send to our own address.

## 3. Metrics captured every run (README material)

- Belief accuracy per turn (‖belief argmax − true pos‖ Chebyshev).
- Capture rate & mean sub-game length per grid size.
- Message stats: length, ambiguity flags, deception attempts (self-declared by persona log).
- If Q-Learning: episode reward curve (CSV → plot).
- LLM cost/latency per turn.

## 4. Commands

```powershell
uv run pytest -q                                     # unit + integration
uv run python -m src.orchestrator --grid 2x2 --mock-llm   # stage 1 ladder
uv run python -m src.orchestrator --grid 3x3              # stage 2
uv run python -m src.orchestrator --grid 4x4              # stage 3
uv run python -m src.orchestrator                          # stage 4 (config 5×5)
```

## 5. Definition of Done (whole HW)

All acceptance boxes in the six PRDs checked + GRADING_RUBRIC self-audit ≥ 98/100 +
E2E-C log archived + report email verified in draft + README complete.
