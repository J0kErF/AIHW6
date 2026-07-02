"""E2E: full autonomous series through REAL MCP servers (in-memory transport),
mock LLM exercising the genuine prompt->parse->guard->engine->message path.
This is sanity-ladder stages 1-4 automated (spec Table 2).
"""
import json
from pathlib import Path

import pytest

from src.common.config import Config
from src.orchestrator import Orchestrator
from tests.conftest import make_config


def e2e_config(tmp_path, grid) -> Config:
    return make_config(
        grid_size=list(grid),
        llm={"provider": "mock"},
        logging={"dir": str(tmp_path / "logs")},
        gui={"export_png": True, "artifacts_dir": str(tmp_path / "shots")},
        turn_timeout_s=30,
    )


@pytest.mark.parametrize("grid", [(2, 2), (3, 3), (4, 4), (5, 5)])
async def test_autonomous_series_ladder(tmp_path, grid):
    cfg = e2e_config(tmp_path, grid)
    orch = Orchestrator(cfg, in_memory=True)
    await orch.connect()
    try:
        records = await orch.run_series()
    finally:
        await orch.close()

    # exactly num_games valid sub-games, correct scoring
    assert len(records) == cfg.num_games
    for r in records:
        assert (r.cop_points, r.thief_points) in {
            (cfg.scoring.cop_win, cfg.scoring.thief_loss),
            (cfg.scoring.cop_loss, cfg.scoring.thief_win),
        }

    # report builds and is pure JSON with spec keys
    body = await orch.report(send_email=False)
    payload = json.loads(body)
    assert payload["group_name"] == cfg.identity.group_name
    assert len(payload["sub_games"]) == cfg.num_games

    # evidence artifacts: turn JSONL + per-sub-game PNGs
    turn_log = Path(orch.turn_log_path)
    assert turn_log.exists() and turn_log.stat().st_size > 0
    shots = list(Path(cfg.gui.artifacts_dir).glob("*.png"))
    assert len(shots) >= cfg.num_games

    # CLI-log evidence: NL messages flowed and belief accuracy was tracked
    events = [json.loads(l) for l in Path(orch.log.path).read_text(encoding="utf-8").splitlines()]
    turns = [e for e in events if e["event"] == "turn"]
    assert turns and all(e["verify_ok"] for e in turns)
    assert all(isinstance(e["message"], str) and e["message"] for e in turns)
    assert any(e["belief_accuracy"] == 0 for e in turns)  # inference sometimes exact


async def test_free_language_not_a_coordinate_protocol(tmp_path):
    """Grading-trap guard: messages must be prose, not coordinate exchanges."""
    cfg = e2e_config(tmp_path, (3, 3))
    orch = Orchestrator(cfg, in_memory=True)
    await orch.connect()
    try:
        await orch.run_sub_game(1)
    finally:
        await orch.close()
    events = [json.loads(l) for l in Path(orch.log.path).read_text(encoding="utf-8").splitlines()]
    msgs = [e["message"] for e in events if e["event"] == "turn"]
    assert msgs
    for m in msgs:
        assert not any(tok in m for tok in ("(0,", "(1,", "(2,", "[0,", "[1,", "[2,")), m
        assert len(m.split()) >= 4  # real sentences, not codes
