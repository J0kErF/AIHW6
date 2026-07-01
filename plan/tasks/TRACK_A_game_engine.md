# TRACK A — Game Engine & Common Core

> Read first: `docs/GAME_RULES.md` (normative), `docs/PRD_game_engine.md`,
> `config.json`. You own `src/engine/`, `src/common/`, `tests/engine/`.
> You are upstream of everyone: **publish SP-1 (frozen interfaces) ASAP** on the TASK_BOARD.

## Mission
Pure deterministic game core + config/schema/logging commons. No LLM, no network, no GUI.

## Tasks
- [ ] A1. `pyproject.toml` (uv) with deps: pydantic, numpy, pytest, rich. `uv sync` works.
- [ ] A2. `src/common/config.py` — pydantic `Config` mirroring `config.json` exactly;
       fail-fast on unknown/missing keys; loader takes explicit path (CLI `--config`).
- [ ] A3. `src/common/schemas.py` — `Role`, `Action` (Move8/PlaceBarrier), `GameState`,
       `Observation`, `TurnResult`, `SubGameRecord`, `Totals` (must map 1:1 to
       REPORTING_SPEC `sub_games[]`).
- [ ] A4. `src/common/logging.py` — JSONL + console logger, run-id stamped.
- [ ] A5. `src/engine/board.py` — grid, adjacency (8-dir), bounds, barrier set.
- [ ] A6. `src/engine/rules.py` — validation (typed errors), turn order (thief first),
       capture + move-limit detection, barrier semantics (cop-only, current cell, ≤5, blocks both).
- [ ] A7. `src/engine/engine.py` — `Engine.new_sub_game / legal_actions / apply / observation`
       per PRD_game_engine §3; seeded RNG for start positions.
- [ ] A8. `src/engine/series.py` — `SeriesManager`: run/record sub-games, void technical
       losses, re-run to exactly `num_games` valid, `totals()`.
- [ ] A9. Observation builder with `observation.vision_radius` (opponent visible only in radius).
- [ ] A10. Tests: rules matrix on 2×2/3×2/3×3/4×3/4×4/5×5; property tests (no illegal state,
        quota, terminal invariants); no-hardcode grep test.
- [ ] A11. **Post SP-1 FROZEN** on TASK_BOARD with the final signatures.

## Definition of Done
`uv run pytest tests/engine -q` green; ladder stage 1 (scripted 2×2 sub-game) passes;
interfaces published; any config change alters behavior without code edits.
