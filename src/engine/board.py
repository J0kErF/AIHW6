"""Board geometry helpers — pure functions over config-provided dimensions."""
from __future__ import annotations

from src.common.schemas import Cell, Direction, DIRECTION_VECTORS


def in_bounds(pos: Cell, grid_size: Cell) -> bool:
    x, y = pos
    w, h = grid_size
    return 0 <= x < w and 0 <= y < h


def step(pos: Cell, direction: Direction) -> Cell:
    dx, dy = DIRECTION_VECTORS[direction]
    return (pos[0] + dx, pos[1] + dy)


def chebyshev(a: Cell, b: Cell) -> int:
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def all_cells(grid_size: Cell) -> list[Cell]:
    w, h = grid_size
    return [(x, y) for x in range(w) for y in range(h)]
