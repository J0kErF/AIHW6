# PRD — GUI & Visualization (Track D)

> Owns: `src/gui/`. Spec Table 4 stage 6: "visual interface showing agent movement and
> barriers in real time". README requires **GUI screenshots** as evidence.

## 1. Goal

A live board view driven by engine events: agents, barriers, move counter, current turn,
score, and the natural-language message feed. Plus export utilities (screenshots, replay).

## 2. Functional requirements

1. **Renderer** subscribes to engine `TurnResult` events (in-process observer or JSONL tail)
   — read-only; GUI can never mutate game state.
2. Displays: grid (any size from config), cop, thief, barriers, per-cell coordinates
   toggle, move `k/25`, sub-game `n/6`, running totals.
3. **Message panel**: chronological NL messages (speaker-tagged) — the visual proof of
   free-language communication.
4. **Speed control / step mode** for demos; headless mode (no GUI) must remain default for
   cloud runs (`config.gui.enabled`).
5. **Screenshot/export**: PNG snapshot per sub-game end + final summary frame, saved to
   `artifacts/` for the README.
6. (Nice) Replay from a game log JSONL.

## 3. Technology decision

Choose the cheapest thing that screenshots well; recommendation order:
`pygame` (simple canvas) → `textual`/`rich` TUI (fast, but screenshots less "graphic") →
`tkinter`. Decision recorded here once made.

## 4. Acceptance criteria

- [ ] Live view correct on 2×2 and 5×5 without code change.
- [ ] Barriers visibly distinct; capture/turn-limit endings clearly announced.
- [ ] Auto-saved PNGs exist after a full series run (≥ 7 images: 6 sub-games + summary).
- [ ] Headless mode: zero GUI imports on cloud path (no display crash).
