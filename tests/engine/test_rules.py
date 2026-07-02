"""Rule fidelity tests (GAME_RULES.md is normative)."""
import pytest

from src.common.schemas import Direction, Move, Pass, PlaceBarrier, Role
from src.engine.engine import Engine
from src.engine.errors import (
    BarrierBlockedError,
    BarrierNotAllowedError,
    BarrierQuotaExceededError,
    IllegalPassError,
    NotYourTurnError,
    OffBoardError,
    TerminalStateError,
)
from tests.conftest import make_config


def fixed_engine(**overrides) -> Engine:
    defaults = {
        "start_positions": {"mode": "fixed", "fixed_cop": [0, 0], "fixed_thief": [2, 2]},
        "grid_size": [3, 3],
    }
    defaults.update(overrides)
    cfg = make_config(**defaults)
    e = Engine(cfg)
    e.new_sub_game()
    return e


def test_thief_moves_first():
    e = fixed_engine()
    assert e.state.turn is Role.THIEF
    with pytest.raises(NotYourTurnError):
        e.apply(Role.COP, Move(direction=Direction.E))


def test_off_board_rejected():
    e = fixed_engine()
    with pytest.raises(OffBoardError):
        e.apply(Role.THIEF, Move(direction=Direction.SE))  # (2,2) -> (3,3) off 3x3


def test_eight_direction_movement_and_turn_alternation():
    e = fixed_engine()
    e.apply(Role.THIEF, Move(direction=Direction.NW))  # (2,2)->(1,1)
    assert tuple(e.state.thief_pos) == (1, 1)
    assert e.state.turn is Role.COP
    e.apply(Role.COP, Move(direction=Direction.SE))  # (0,0)->(1,1) capture
    assert e.state.terminal and e.state.winner is Role.COP and e.state.reason == "capture"


def test_capture_symmetric_thief_walks_into_cop():
    e = fixed_engine(start_positions={"mode": "fixed", "fixed_cop": [1, 1], "fixed_thief": [2, 2]})
    e.apply(Role.THIEF, Move(direction=Direction.NW))  # onto cop
    assert e.state.terminal and e.state.winner is Role.COP


def test_move_limit_thief_wins():
    e = fixed_engine(max_moves=2)
    # round 1
    e.apply(Role.THIEF, Move(direction=Direction.W))   # (2,2)->(1,2)
    e.apply(Role.COP, Move(direction=Direction.E))     # (0,0)->(1,0)
    assert e.state.move_count == 1 and not e.state.terminal
    # round 2
    e.apply(Role.THIEF, Move(direction=Direction.E))   # back to (2,2)
    e.apply(Role.COP, Move(direction=Direction.W))     # back to (0,0)
    assert e.state.terminal and e.state.winner is Role.THIEF and e.state.reason == "move_limit"
    with pytest.raises(TerminalStateError):
        e.apply(Role.THIEF, Move(direction=Direction.W))


def test_barrier_on_current_cell_blocks_thief():
    e = fixed_engine()
    e.apply(Role.THIEF, Move(direction=Direction.NW))      # (2,2)->(1,1)
    e.apply(Role.COP, PlaceBarrier())                      # barrier at cop's cell (0,0)
    assert (0, 0) in {tuple(b) for b in e.state.barriers}
    assert e.state.barriers_used == 1
    with pytest.raises(BarrierBlockedError):
        e.apply(Role.THIEF, Move(direction=Direction.NW))  # (1,1)->(0,0) barred


def test_barrier_blocks_reentry_and_double_placement():
    e = fixed_engine()
    e.apply(Role.THIEF, Move(direction=Direction.N))       # thief away
    e.apply(Role.COP, PlaceBarrier())                      # barrier @ (0,0), cop stands on it
    e.apply(Role.THIEF, Move(direction=Direction.S))
    with pytest.raises(BarrierNotAllowedError):
        e.apply(Role.COP, PlaceBarrier())                  # same cell again
    e.apply(Role.COP, Move(direction=Direction.E))         # cop leaves (0,0)
    e.apply(Role.THIEF, Move(direction=Direction.N))
    with pytest.raises(BarrierBlockedError):
        e.apply(Role.COP, Move(direction=Direction.W))     # cannot re-enter own barrier


def test_thief_cannot_place_barrier():
    e = fixed_engine()
    with pytest.raises(BarrierNotAllowedError):
        e.apply(Role.THIEF, PlaceBarrier())


def test_barrier_quota_from_config():
    e = fixed_engine(max_barriers=2, max_moves=25)
    moves = [Direction.E, Direction.W]  # cop shuffles to change cells
    for i in range(2):
        e.apply(Role.THIEF, Move(direction=Direction.N if i == 0 else Direction.S))
        e.apply(Role.COP, PlaceBarrier()) if i == 0 else e.apply(
            Role.COP, Move(direction=moves[0])
        )
    # place second barrier on new cell
    e.apply(Role.THIEF, Move(direction=Direction.N))
    e.apply(Role.COP, PlaceBarrier())
    assert e.state.barriers_used == 2
    e.apply(Role.THIEF, Move(direction=Direction.S))
    with pytest.raises(BarrierQuotaExceededError):
        e.apply(Role.COP, PlaceBarrier())


def test_pass_only_when_no_legal_actions():
    e = fixed_engine()
    with pytest.raises(IllegalPassError):
        e.apply(Role.THIEF, Pass())


def test_legal_actions_respect_barriers_and_bounds():
    e = fixed_engine()
    legal = e.legal_actions(Role.THIEF)  # thief at (2,2) corner of 3x3
    dirs = {a.direction for a in legal if a.kind == "move"}
    assert dirs == {Direction.N, Direction.W, Direction.NW}
    assert e.legal_actions(Role.COP) == []  # not cop's turn


def test_vision_radius_partial_observability():
    e = fixed_engine(observation={"vision_radius": 1})
    obs = e.observation(Role.COP)  # cop (0,0), thief (2,2), chebyshev 2 > 1
    assert not obs.opponent_visible and obs.opponent_pos is None
    e2 = fixed_engine(observation={"vision_radius": 2})
    obs2 = e2.observation(Role.COP)
    assert obs2.opponent_visible and tuple(obs2.opponent_pos) == (2, 2)
