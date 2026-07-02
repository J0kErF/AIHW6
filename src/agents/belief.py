"""Belief grid over the opponent's position (Dec-POMDP inference, C4).

Update sources each turn:
1. motion spread — the opponent moves at most 1 cell (Chebyshev) per action;
2. direct vision — inside the radius: collapse; outside: zero that neighborhood;
3. linguistic hint — the LLM's interpreted guess, blended with low confidence
   (messages may be deception; the weight is a parameter, not a truth claim).
Accuracy metric per turn (belief argmax vs ground truth) feeds the README's
ambiguity analysis (sanity ladder stage 3).
"""
from __future__ import annotations

import numpy as np

from src.common.schemas import Cell
from src.engine.board import chebyshev


class BeliefGrid:
    def __init__(self, grid_size: Cell, hint_weight: float = 0.25) -> None:
        self.w, self.h = grid_size
        self.hint_weight = hint_weight
        self.p = np.full((self.w, self.h), 1.0 / (self.w * self.h))

    # -- update steps ---------------------------------------------------------
    def motion_spread(self, barriers: list[Cell]) -> None:
        """Opponent moved <=1 cell: convolve mass into the 8-neighborhood."""
        spread = np.zeros_like(self.p)
        for x in range(self.w):
            for y in range(self.h):
                if self.p[x, y] <= 0:
                    continue
                targets = [
                    (nx, ny)
                    for nx in range(max(0, x - 1), min(self.w, x + 2))
                    for ny in range(max(0, y - 1), min(self.h, y + 2))
                    if (nx, ny) not in set(map(tuple, barriers))
                ]
                share = self.p[x, y] / len(targets)
                for nx, ny in targets:
                    spread[nx, ny] += share
        self.p = spread
        self._normalize()

    def observe(self, self_pos: Cell, vision_radius: int, opponent_pos: Cell | None) -> None:
        if opponent_pos is not None:  # visible: certainty
            self.p[:] = 0.0
            self.p[opponent_pos[0], opponent_pos[1]] = 1.0
            return
        for x in range(self.w):  # not visible: exclude the whole vision disk
            for y in range(self.h):
                if chebyshev((x, y), tuple(self_pos)) <= vision_radius:
                    self.p[x, y] = 0.0
        self._normalize()

    def apply_hint(self, hint: Cell | None) -> None:
        """Blend the LLM's message-derived guess (deception-aware low weight)."""
        if hint is None or not (0 <= hint[0] < self.w and 0 <= hint[1] < self.h):
            return
        bump = np.zeros_like(self.p)
        bump[hint[0], hint[1]] = 1.0
        self.p = (1 - self.hint_weight) * self.p + self.hint_weight * bump
        self._normalize()

    # -- queries ---------------------------------------------------------------
    def argmax(self) -> Cell:
        idx = int(np.argmax(self.p))
        return (idx // self.h, idx % self.h)

    def accuracy(self, true_pos: Cell) -> int:
        """Chebyshev distance from belief argmax to ground truth (0 = perfect)."""
        return chebyshev(self.argmax(), tuple(true_pos))

    def _normalize(self) -> None:
        total = self.p.sum()
        if total <= 0:  # inconsistent evidence — reset to uniform, stay live
            self.p = np.full((self.w, self.h), 1.0 / (self.w * self.h))
        else:
            self.p /= total
