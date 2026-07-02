"""Headless GUI tests: render scripted games on 2x2 and 5x5, export PNGs."""
import random
from pathlib import Path

import pytest

from src.engine.series import SeriesManager, random_policy
from src.gui.board_view import render
from src.gui.events import read_turns, write_turn
from src.gui.export import save_png
from tests.conftest import make_config

ROOT = Path(__file__).resolve().parents[2]


def scripted_turns(grid, num_games=1):
    cfg = make_config(grid_size=list(grid), num_games=num_games)
    rng = random.Random(cfg.random_seed)
    turns = []
    sm = SeriesManager(
        cfg, random_policy(rng), random_policy(rng), on_turn=turns.append, rng=rng
    )
    sm.run_series()
    return cfg, turns


@pytest.mark.parametrize("grid", [(2, 2), (5, 5)])
def test_render_and_png_export(grid, tmp_path):
    cfg, turns = scripted_turns(grid)
    messages = [("cop", "I am closing in on the corner..."), ("thief", "You will never find me.")]
    surface = render(turns[-1], cfg, messages)
    w, h = grid
    assert surface.get_width() > w * cfg.gui.cell_px  # board + message panel
    out = save_png(surface, tmp_path / f"demo_{w}x{h}.png")
    assert out.exists() and out.stat().st_size > 0


def test_demo_artifacts_for_readme():
    """Produces real evidence PNGs under artifacts/screenshots (D6)."""
    cfg, turns = scripted_turns((5, 5))
    out_dir = ROOT / "artifacts" / "screenshots"
    frame = render(turns[-1], cfg, [("cop", "gotcha route planned"), ("thief", "heading north, or am I?")])
    path = save_png(frame, out_dir / "demo_final_5x5.png")
    assert path.exists() and path.stat().st_size > 0


def test_jsonl_replay_roundtrip(tmp_path):
    cfg, turns = scripted_turns((3, 3))
    log = tmp_path / "run.jsonl"
    for t in turns:
        write_turn(log, t)
    replayed = list(read_turns(log))
    assert len(replayed) == len(turns)
    assert replayed[-1].state.terminal
    assert replayed[0].actor == turns[0].actor
