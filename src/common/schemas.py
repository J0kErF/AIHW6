"""Shared typed contracts (SP-1). Owned by Track A; changes go through TASK_BOARD."""
from __future__ import annotations

from enum import Enum
from typing import Literal, Union

from pydantic import BaseModel, ConfigDict, Field

Cell = tuple[int, int]


class Role(str, Enum):
    COP = "cop"
    THIEF = "thief"

    @property
    def opponent(self) -> "Role":
        return Role.THIEF if self is Role.COP else Role.COP


class Direction(str, Enum):
    N = "N"
    NE = "NE"
    E = "E"
    SE = "SE"
    S = "S"
    SW = "SW"
    W = "W"
    NW = "NW"


# y grows downward (rendering convention); N decreases y.
DIRECTION_VECTORS: dict[Direction, Cell] = {
    Direction.N: (0, -1),
    Direction.NE: (1, -1),
    Direction.E: (1, 0),
    Direction.SE: (1, 1),
    Direction.S: (0, 1),
    Direction.SW: (-1, 1),
    Direction.W: (-1, 0),
    Direction.NW: (-1, -1),
}


class Move(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["move"] = "move"
    direction: Direction


class PlaceBarrier(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["barrier"] = "barrier"


class Pass(BaseModel):
    """Only legal when an agent has no legal action (fully walled in)."""

    model_config = ConfigDict(extra="forbid")
    kind: Literal["pass"] = "pass"


Action = Union[Move, PlaceBarrier, Pass]

WinReason = Literal["capture", "move_limit"]


class GameState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cop_pos: Cell
    thief_pos: Cell
    barriers: list[Cell] = Field(default_factory=list)
    move_count: int = 0  # completed rounds (thief+cop both acted)
    turn: Role
    terminal: bool = False
    winner: Role | None = None
    reason: WinReason | None = None
    barriers_used: int = 0


class Observation(BaseModel):
    """Partial observation for one agent (Dec-POMDP Omega_i)."""

    model_config = ConfigDict(extra="forbid")
    role: Role
    self_pos: Cell
    visible_barriers: list[Cell]
    opponent_visible: bool
    opponent_pos: Cell | None  # only set when opponent_visible
    move_count: int
    max_moves: int
    grid_size: Cell
    barriers_left: int  # cop only semantics; informational for thief


class TurnResult(BaseModel):
    """Event emitted after every applied action; GUI/log/report all consume this."""

    model_config = ConfigDict(extra="forbid")
    turn_index: int  # 0-based count of individual actions
    actor: Role
    action: Action
    state: GameState
    message: str | None = None  # NL message attached by orchestrator (Track C)


class SubGameRecord(BaseModel):
    """Maps 1:1 to REPORTING_SPEC sub_games[] entries."""

    model_config = ConfigDict(extra="forbid")
    index: int
    winner: Role
    reason: WinReason
    moves_played: int
    barriers_used: int
    cop_points: int
    thief_points: int
    started_at: str
    ended_at: str


class Totals(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cop: int = 0
    thief: int = 0
