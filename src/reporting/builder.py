"""Report builder with the exactly-6-valid-sub-games guard (spec §9)."""
from __future__ import annotations

import json

from src.common.config import Config
from src.common.schemas import SubGameRecord, Totals
from src.reporting.models import InternalReport, TotalsModel


class ReportValidityError(Exception):
    pass


def build_internal_report(
    records: list[SubGameRecord], totals: Totals, config: Config
) -> InternalReport:
    if len(records) != config.num_games:
        raise ReportValidityError(
            f"need exactly {config.num_games} valid sub-games, got {len(records)} "
            "(technical losses must be re-run, never reported)"
        )
    expected_cop = sum(r.cop_points for r in records)
    expected_thief = sum(r.thief_points for r in records)
    if (totals.cop, totals.thief) != (expected_cop, expected_thief):
        raise ReportValidityError("totals do not match sub-game records")
    return InternalReport(
        group_name=config.identity.group_name,
        students=config.identity.students,
        github_repo=config.identity.github_repo,
        cop_mcp_url=config.mcp.cop_url,
        thief_mcp_url=config.mcp.thief_url,
        timezone=config.identity.timezone,
        sub_games=records,
        totals=TotalsModel(cop=totals.cop, thief=totals.thief),
    )


def report_body(report: InternalReport) -> str:
    """The email body: the JSON document and NOTHING else (spec §9)."""
    return json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2)
