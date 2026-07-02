"""Schema fidelity + guard tests (no network)."""
import json
import random

import pytest

from src.engine.series import SeriesManager, random_policy
from src.reporting.builder import ReportValidityError, build_internal_report, report_body
from src.reporting.models import BonusReport
from tests.conftest import make_config

SPEC_INTERNAL_KEYS = {
    "group_name",
    "students",
    "github_repo",
    "cop_mcp_url",
    "thief_mcp_url",
    "timezone",
    "sub_games",
    "totals",
}

SPEC_BONUS_KEYS = {
    "report_type",
    "groups",
    "github_repo_group_1",
    "github_repo_group_2",
    "mcp_url_group_1_cop",
    "mcp_url_group_1_thief",
    "mcp_url_group_2_cop",
    "mcp_url_group_2_thief",
    "timezone",
    "students_group_1",
    "students_group_2",
    "sub_games",
    "totals_by_group",
    "bonus_claim",
    "mutual_agreement",
}


def completed_series():
    cfg = make_config()
    rng = random.Random(cfg.random_seed)
    sm = SeriesManager(cfg, random_policy(rng), random_policy(rng), rng=rng)
    sm.run_series()
    return cfg, sm


def test_internal_report_keys_match_spec_exactly():
    cfg, sm = completed_series()
    report = build_internal_report(sm.records, sm.totals(), cfg)
    payload = json.loads(report_body(report))
    assert set(payload.keys()) == SPEC_INTERNAL_KEYS
    assert payload["group_name"] == "moamteam"
    assert payload["timezone"] == "Asia/Jerusalem"
    assert len(payload["sub_games"]) == cfg.num_games
    assert set(payload["totals"].keys()) == {"cop", "thief"}


def test_body_is_pure_parseable_json():
    cfg, sm = completed_series()
    body = report_body(build_internal_report(sm.records, sm.totals(), cfg))
    parsed = json.loads(body)  # would raise on any prefix/suffix text
    assert body.strip().startswith("{") and body.strip().endswith("}")
    assert parsed["totals"]["cop"] == sum(r.cop_points for r in sm.records)


def test_guard_rejects_wrong_subgame_count():
    cfg, sm = completed_series()
    with pytest.raises(ReportValidityError, match="exactly"):
        build_internal_report(sm.records[:-1], sm.totals(), cfg)


def test_guard_rejects_totals_mismatch():
    cfg, sm = completed_series()
    totals = sm.totals()
    totals.cop += 1
    with pytest.raises(ReportValidityError, match="totals"):
        build_internal_report(sm.records, totals, cfg)


def test_bonus_report_keys_match_spec():
    cfg, sm = completed_series()
    bonus = BonusReport(
        groups={"group_1": "moamteam", "group_2": "other"},
        github_repo_group_1="https://github.com/a/b",
        github_repo_group_2="https://github.com/c/d",
        mcp_url_group_1_cop="u1",
        mcp_url_group_1_thief="u2",
        mcp_url_group_2_cop="u3",
        mcp_url_group_2_thief="u4",
        timezone="Asia/Jerusalem",
        students_group_1=[],
        students_group_2=[],
        sub_games=sm.records,
        totals_by_group={"moamteam": 60, "other": 80},
        bonus_claim={"moamteam": 7, "other": 10},
        mutual_agreement=True,
    )
    assert set(bonus.model_dump(mode="json").keys()) == SPEC_BONUS_KEYS
