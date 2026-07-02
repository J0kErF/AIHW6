"""Deterministic game core (Track A). No LLM, no network, no GUI.

Rule decisions recorded here (also in AGENT_MEMORY Decisions Log):
- A "move" in the 25-move cap = one completed ROUND (thief acted, then cop).
- Capture is symmetric: if either agent ends its move on the opponent's cell,
  the COP wins (the two occupy one square = the thief is caught).
- A barrier is placed on the cop's current cell; the cell becomes impassable to
  BOTH agents (the cop may leave it but never re-enter).
- If an agent has zero legal actions (walled in), it must Pass — the game goes on.
"""
from __future__ import annotations

import random

from src.common.config import Config
from src.common.schemas import (
    Action,
    Cell,
    Direction,
    GameState,
    Move,
    Observation,
    Pass,
    PlaceBarrier,
    Role,
    TurnResult,
)
from src.engine import board
from src.engine.errors import (
    BarrierBlockedError,
    BarrierNotAllowedError,
    BarrierQuotaExceededError,
    IllegalPassError,
    NotYourTurnError,
    OffBoardError,
    TerminalStateError,
)


class Engine:
    def __init__(self, config: Config, rng: random.Random | None = None) -> None:
        self.config = config
        self.rng = rng or random.Random(config.random_seed)
        self.state: GameState | None = None
        self._turn_index = 0

    # -- lifecycle -----------------------------------------------------------
    def new_sub_game(self) -> GameState:
        cop, thief = self._start_positions()
        self.state = GameState(
            cop_pos=cop,
            thief_pos=thief,
            turn=Role(self.config.turn_order_first),
        )
        self._turn_index = 0
        return self.state

    def _start_positions(self) -> tuple[Cell, Cell]:
        sp = self.config.start_positions
        if sp.mode == "fixed":
            return tuple(sp.fixed_cop), tuple(sp.fixed_thief)
        cells = board.all_cells(self.config.grid_size)
        cop, thief = self.rng.sample(cells, 2)
        return cop, thief

    # -- queries ---------------------------------------------------------------
    def legal_actions(self, role: Role) -> list[Action]:
        s = self._require_state()
        if s.terminal or s.turn is not role:
            return []
        pos = s.cop_pos if role is Role.COP else s.thief_pos
        actions: list[Action] = []
        barriers = set(map(tuple, s.barriers))
        for d in Direction:
            target = board.step(pos, d)
            if board.in_bounds(target, self.config.grid_size) and target not in barriers:
                actions.append(Move(direction=d))
        if (
            role is Role.COP
            and s.barriers_used < self.config.max_barriers
            and tuple(pos) not in barriers
        ):
            actions.append(PlaceBarrier())
        return actions

    def observation(self, role: Role) -> Observation:
        s = self._require_state()
        self_pos = s.cop_pos if role is Role.COP else s.thief_pos
        opp_pos = s.thief_pos if role is Role.COP else s.cop_pos
        radius = self.config.observation.vision_radius
        visible = board.chebyshev(self_pos, opp_pos) <= radius
        return Observation(
            role=role,
            self_pos=self_pos,
            visible_barriers=[
                b for b in s.barriers if board.chebyshev(self_pos, tuple(b)) <= radius
            ],
            opponent_visible=visible,
            opponent_pos=opp_pos if visible else None,
            move_count=s.move_count,
            max_moves=self.config.max_moves,
            grid_size=self.config.grid_size,
            barriers_left=self.config.max_barriers - s.barriers_used,
        )

    # -- transitions -----------------------------------------------------------
    def apply(self, role: Role, action: Action) -> TurnResult:
        s = self._require_state()
        if s.terminal:
            raise TerminalStateError("sub-game already finished")
        if s.turn is not role:
            raise NotYourTurnError(f"it is {s.turn.value}'s turn, not {role.value}'s")

        if isinstance(action, Pass):
            if self.legal_actions(role):
                raise IllegalPassError("pass only allowed with no legal actions")
        elif isinstance(action, PlaceBarrier):
            self._apply_barrier(role, s)
        elif isinstance(action, Move):
            self._apply_move(role, s, action)
        else:  # pragma: no cover - pydantic union exhausts this
            raise TypeError(f"unknown action {action!r}")

        self._advance_clock(role, s)
        result = TurnResult(
            turn_index=self._turn_index, actor=role, action=action, state=s.model_copy(deep=True)
        )
        self._turn_index += 1
        return result

    def _apply_barrier(self, role: Role, s: GameState) -> None:
        if role is not Role.COP:
            raise BarrierNotAllowedError("only the cop may place barriers")
        if s.barriers_used >= self.config.max_barriers:
            raise BarrierQuotaExceededError(
                f"barrier quota ({self.config.max_barriers}) exhausted"
            )
        if tuple(s.cop_pos) in set(map(tuple, s.barriers)):
            raise BarrierNotAllowedError("cell already has a barrier")
        s.barriers.append(tuple(s.cop_pos))
        s.barriers_used += 1

    def _apply_move(self, role: Role, s: GameState, action: Move) -> None:
        pos = s.cop_pos if role is Role.COP else s.thief_pos
        target = board.step(tuple(pos), action.direction)
        if not board.in_bounds(target, self.config.grid_size):
            raise OffBoardError(f"{target} is outside {self.config.grid_size}")
        if target in set(map(tuple, s.barriers)):
            raise BarrierBlockedError(f"{target} is barred")
        if role is Role.COP:
            s.cop_pos = target
        else:
            s.thief_pos = target
        if tuple(s.cop_pos) == tuple(s.thief_pos):
            s.terminal = True
            s.winner = Role.COP
            s.reason = "capture"

    def _advance_clock(self, actor: Role, s: GameState) -> None:
        if s.terminal:
            return
        s.turn = actor.opponent
        # a round completes when the player who moves SECOND has acted
        second = Role(self.config.turn_order_first).opponent
        if actor is second:
            s.move_count += 1
            if s.move_count >= self.config.max_moves:
                s.terminal = True
                s.winner = Role.THIEF
                s.reason = "move_limit"

    def _require_state(self) -> GameState:
        if self.state is None:
            raise RuntimeError("call new_sub_game() first")
        return self.state
