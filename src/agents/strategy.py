"""Heuristic baseline & legality guard (C5): the safety net under the LLM."""
from __future__ import annotations

from src.common.schemas import Action, Cell, Move, Observation, Pass, Role
from src.engine.board import chebyshev, step


def heuristic_action(role: Role, obs: Observation, legal: list[Action], target: Cell) -> Action:
    """Cop: minimize distance to target (belief argmax). Thief: maximize."""
    moves = [a for a in legal if isinstance(a, Move)]
    if not moves:
        return legal[0] if legal else Pass()
    sign = 1 if role is Role.COP else -1

    def score(a: Move) -> int:
        return sign * chebyshev(step(tuple(obs.self_pos), a.direction), tuple(target))

    return min(moves, key=score)


def guard(
    role: Role,
    proposed: Action,
    legal: list[Action],
    obs: Observation,
    target: Cell,
) -> tuple[Action, bool]:
    """Return (action, was_fallback). Illegal LLM proposals never crash a game."""
    if not legal:
        return Pass(), False
    for candidate in legal:
        if candidate == proposed:
            return proposed, False
    return heuristic_action(role, obs, legal, target), True
