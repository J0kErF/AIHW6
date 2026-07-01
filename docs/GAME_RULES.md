# GAME_RULES — Normative Rulebook (single source of truth)

> Any code that disagrees with this document is a bug. Any change here requires updating
> `config.json` defaults and the tests in `TESTING.md`.

## 1. Entities

- **Cop** — pursuer. Wins by capture. May place barriers.
- **Thief** — evader. Wins by surviving. May NOT place barriers.
- **Board** — 2D grid `grid_size = [W, H]` (default `[5, 5]`). Every cell has coordinates
  `(x, y)`, `0 ≤ x < W`, `0 ≤ y < H`.
- **Barrier** — an impassable cell for BOTH players (like a wall / board edge).

## 2. Structure: sub-game vs game

- **Sub-game**: one chase round, hard-capped at `max_moves = 25` moves.
- **Game**: an ordered series of `num_games = 6` sub-games played back-to-back;
  all results are accumulated and reported together in one email.
- **Technical loss**: a sub-game that dies from a technical failure (timeout, crash,
  malformed pipeline) is **void** — it must be re-run so exactly 6 **valid** sub-games exist.

## 3. Turn order & moves

1. Play is **turn-based**. By default the **Thief moves first**, then the Cop, alternating.
2. On each turn an agent performs exactly one action:
   - **Move** to an adjacent cell in any of the **8 directions** (N, NE, E, SE, S, SW, W, NW), or
   - **Stay** is not a listed action — an agent changes location **or** performs a special action;
   - **Special action (Cop only): place barrier** on the cell **the Cop currently stands on**
     (see §5).
3. Illegal destinations: off-board cells, barrier cells. An LLM decision resolving to an
   illegal move must be caught by the engine and re-requested / mapped to a legal fallback
   (engine-level guard; count policy defined in `config.json` → `illegal_move_policy`).
4. The whole game is a **state machine**: every move produces a new board state.

## 4. Win conditions (per sub-game)

- **Cop wins** the moment the Cop arrives at exactly the square occupied by the Thief (capture).
- **Thief wins** if he survives all `max_moves = 25` moves without capture.

## 5. Barriers

- Placed only by the **Cop**, as an alternative to moving, on the **cell he stands on**.
- From that move on the cell is **impassable for the Thief AND for the Cop** (like a wall).
- Hard limit: `max_barriers = 5` per sub-game.
- The Thief can never place barriers.

## 6. Scoring (per sub-game, from config — never hard-coded)

| Sub-game outcome | Cop points | Thief points |
|---|---|---|
| Cop wins (capture) | **20** (`scoring.cop_win`) | 5 (`scoring.thief_loss`) |
| Thief wins (escape) | 5 (`scoring.cop_loss`) | **10** (`scoring.thief_win`) |

- Team maximum over a full inter-group game: **90** = 3×20 (as cop) + 3×10 (as thief).
- Team minimum: **30**.

## 7. Partial observability (Dec-POMDP grounds)

- Neither agent is handed the opponent's exact coordinates by the engine as its "protocol".
- Each agent gets: its own position, the board layout it knows (incl. barriers it has seen),
  and the opponent's **free-text natural-language message** (which may describe intentions,
  local observations — or attempt **deception**).
- A configurable **vision radius** (`observation.vision_radius`) controls what an agent
  directly observes; outside it, the agent must **infer** from messages.
- Formal model (mandatory in README):
  `⟨n, S, {Aᵢ}, P, R, {Ωᵢ}, O, γ⟩` where
  `n = 2` agents; `S` = player positions + barrier set + move counter;
  `Aᵢ` = 8 moves (+ barrier for Cop); `P` = deterministic transition;
  `R` = scoring table; `Ωᵢ` = partial observations (own pos, local vision, opponent message);
  `O` = observation function; `γ` = discount factor.

## 8. Communication rules

- Every turn, the acting agent produces a **free natural-language message** (text) that is
  delivered to the opponent through the MCP layer.
- Messages MAY contain truths, partial truths, or deception. There is **no fixed schema**
  for message content — that is the point of the exercise.
- The receiving agent uses its MCP tools + LLM to read, interpret, update its belief about
  the opponent's location, and choose its next action.
- Agents are independent and must not rely on each other's internal implementation.

## 9. Start conditions

- Cop and Thief start positions: random or strategically chosen (configurable:
  `start_positions.mode = "random" | "fixed"`), never the same cell.

## 10. Sanity ladder (must be demonstrable at any time)

`2×2 → 3×3 / 3×2 → 4×4 / 4×3 → 5×5` — the engine must accept any grid size from config
with no code change (generic architecture requirement).
