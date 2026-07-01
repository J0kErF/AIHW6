# PRD — Game Engine (Track A)

> Owns: `src/engine/`, `src/common/` (config loader, schemas). The most upstream track —
> every other track consumes its contracts, so **interfaces freeze first**.

## 1. Goal

A pure, deterministic, LLM-free game core: board, state machine, rule enforcement,
scoring, sub-game/game accounting. No I/O besides logging. 100% unit-testable.

## 2. Functional requirements

1. **Board**: `grid_size=[W,H]` from config; any size ≥ 2×2 works unchanged (F-01, F-17).
2. **State**: `GameState { cop_pos, thief_pos, barriers:set[(x,y)], move_count, turn: "thief"|"cop", history[] }`.
3. **Actions**: `Move(direction ∈ 8)` for both; `PlaceBarrier()` cop-only, on current cell,
   ≤ `max_barriers`; validation returns typed errors (OffBoard, BarrierBlocked, BarrierQuotaExceeded, NotYourTurn).
4. **Turn order**: thief first, alternating; engine advances only on valid action.
5. **Terminal detection**: capture (cop_pos == thief_pos after cop move — and clarify: if
   thief moves onto cop's cell, treat as capture too; decision recorded in code + README),
   or `move_count == max_moves` ⇒ thief wins.
6. **Scoring**: from `config.scoring`; returns per-sub-game result record.
7. **Sub-game/game manager**: runs series of `num_games`; marks technical losses void;
   re-queues until 6 valid results; aggregates totals.
8. **Observation builder**: given state + `vision_radius`, produce each agent's partial
   observation `Ω_i` (own pos, visible cells, visible barriers, opponent visible? bool).
9. **Determinism**: all randomness through one seeded RNG (`config.random_seed`).
10. **Config loader** (`src/common/config.py`): loads/validates `config.json` via pydantic;
    single instance injected everywhere — **no constant duplicated in code**.

## 3. Frozen contracts (other tracks build against these)

```python
class Engine:
    def new_sub_game(self) -> GameState ...
    def legal_actions(self, agent: Role) -> list[Action] ...
    def apply(self, agent: Role, action: Action) -> TurnResult   # includes new state + terminal info
    def observation(self, agent: Role) -> Observation
class SeriesManager:
    def run_next_sub_game(self) -> SubGameRecord
    def totals(self) -> Totals            # feeds REPORTING_SPEC sub_games[] / totals{}
```

`SubGameRecord` fields must map 1:1 to the `sub_games[]` entry in `REPORTING_SPEC.md`.

## 4. Acceptance criteria

- [ ] `pytest tests/engine` green on grids 2×2, 3×2, 3×3, 4×3, 4×4, 5×5.
- [ ] Property tests: no illegal state reachable via `apply`; barrier quota enforced;
      capture always terminal; 25-move cap always terminal.
- [ ] Changing any value in `config.json` changes behavior with zero code edits.
- [ ] Grep proof: no magic numbers for grid/moves/barriers/scores in `src/`.
