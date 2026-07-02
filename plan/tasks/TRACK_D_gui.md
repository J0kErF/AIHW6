# TRACK D — GUI & Visualization

> Read first: `docs/PRD_gui.md`. You own `src/gui/`, `artifacts/`.
> **No start gate** — build against a mocked `TurnResult` stream now; swap to the real
> event source when Track A posts SP-1 (schema is already sketched in PRD_game_engine §3).

## Mission
Live, read-only visualization: board, agents, barriers, score, and the natural-language
message feed — plus automatic PNG evidence for the README.

## Tasks
- [x] D1. Pick tech (pygame recommended; record decision + reason in `docs/PRD_gui.md` §3).
- [x] D2. `gui/events.py` — consume `TurnResult` via in-process observer AND via JSONL tail
       (so GUI can replay logs offline).
- [x] D3. `gui/board_view.py` — grid render (any W×H), cop/thief sprites, barrier cells,
       header: move k/25, sub-game n/6, totals, whose turn.
- [x] D4. `gui/message_panel.py` — scrolling NL message feed, speaker-tagged, turn-stamped.
- [ ] D5. Controls: pause/step/speed; `config.gui.enabled` honored; headless = no GUI import.
- [x] D6. `gui/export.py` — auto PNG at each sub-game end + final summary board →
       `artifacts/screenshots/` (README evidence).
- [x] D7. Replay mode: `uv run python -m src.gui.replay artifacts/logs/<run>.jsonl`.
- [x] D8. Mock-driven demo script (`tests/gui/demo_mock.py`) so D is verifiable before C exists.

## Definition of Done
Mock demo runs on 2×2 and 5×5; live run alongside orchestrator shows correct state each
turn; ≥7 PNGs auto-saved per series; headless cloud path clean (no display dependency).
