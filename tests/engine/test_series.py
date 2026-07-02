"""Series/sanity-ladder tests: any grid size from config, zero code change."""
import random

import pytest

from src.common.schemas import Role
from src.engine.errors import TechnicalLossError
from src.engine.series import SeriesManager, random_policy
from tests.conftest import make_config

LADDER = [(2, 2), (3, 2), (3, 3), (4, 3), (4, 4), (5, 5)]


def build_series(grid, **overrides) -> SeriesManager:
    cfg = make_config(grid_size=list(grid), **overrides)
    rng = random.Random(cfg.random_seed)
    return SeriesManager(cfg, random_policy(rng), random_policy(rng), rng=rng)


@pytest.mark.parametrize("grid", LADDER)
def test_full_series_on_every_ladder_grid(grid):
    sm = build_series(grid)
    records = sm.run_series()
    assert len(records) == sm.config.num_games
    for r in records:
        assert r.winner in (Role.COP, Role.THIEF)
        assert r.reason in ("capture", "move_limit")
        assert 0 <= r.moves_played <= sm.config.max_moves
        assert 0 <= r.barriers_used <= sm.config.max_barriers
    t = sm.totals()
    assert t.cop == sum(r.cop_points for r in records)
    assert t.thief == sum(r.thief_points for r in records)


def test_invariants_every_turn_5x5():
    cfg = make_config()
    seen = []

    def on_turn(tr):
        s = tr.state
        w, h = cfg.grid_size
        for pos in (tuple(s.cop_pos), tuple(s.thief_pos)):
            assert 0 <= pos[0] < w and 0 <= pos[1] < h
        barriers = {tuple(b) for b in s.barriers}
        assert tuple(s.thief_pos) not in barriers or s.terminal is False or True
        # thief never stands on a barrier
        assert tuple(s.thief_pos) not in barriers
        assert s.barriers_used <= cfg.max_barriers
        seen.append(tr.turn_index)

    rng = random.Random(cfg.random_seed)
    sm = SeriesManager(cfg, random_policy(rng), random_policy(rng), on_turn=on_turn, rng=rng)
    sm.run_series()
    assert seen, "on_turn events must fire"


def test_scoring_follows_config_not_constants():
    """Weird config proof: behavior tracks config values (no-hardcode acceptance)."""
    sm = build_series(
        (7, 3),
        max_moves=9,
        num_games=4,
        max_barriers=2,
        scoring={"cop_win": 7, "thief_win": 3, "cop_loss": 2, "thief_loss": 1},
    )
    records = sm.run_series()
    assert len(records) == 4
    for r in records:
        assert r.moves_played <= 9 and r.barriers_used <= 2
        assert (r.cop_points, r.thief_points) in {(7, 1), (2, 3)}


def test_technical_loss_voided_and_rerun():
    cfg = make_config(grid_size=[3, 3])
    rng = random.Random(cfg.random_seed)
    failures = {"left": 2}

    base = random_policy(rng)

    def flaky_cop(obs, legal):
        if failures["left"] > 0:
            failures["left"] -= 1
            raise TechnicalLossError("simulated transport crash")
        return base(obs, legal)

    sm = SeriesManager(cfg, flaky_cop, random_policy(rng), rng=rng)
    records = sm.run_series()
    assert len(records) == cfg.num_games          # still exactly 6 valid
    assert sm.technical_losses == 2               # both crashes voided, not recorded
    assert [r.index for r in records] == list(range(1, cfg.num_games + 1))
