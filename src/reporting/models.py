"""Frozen report contracts — mirror docs/REPORTING_SPEC.md byte-for-byte (keys)."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from src.common.schemas import SubGameRecord


class TotalsModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cop: int
    thief: int


class InternalReport(BaseModel):
    """Spec §9.1 — Internal Game JSON."""

    model_config = ConfigDict(extra="forbid")
    group_name: str
    students: list[str]
    github_repo: str
    cop_mcp_url: str
    thief_mcp_url: str
    timezone: str
    sub_games: list[SubGameRecord]
    totals: TotalsModel


class BonusReport(BaseModel):
    """Spec §9.2 — Inter-Group Bonus JSON (kept for interop; bonus itself waived)."""

    model_config = ConfigDict(extra="forbid")
    report_type: str = "bonus_game"
    groups: dict[str, str]
    github_repo_group_1: str
    github_repo_group_2: str
    mcp_url_group_1_cop: str
    mcp_url_group_1_thief: str
    mcp_url_group_2_cop: str
    mcp_url_group_2_thief: str
    timezone: str
    students_group_1: list[str]
    students_group_2: list[str]
    sub_games: list[SubGameRecord]
    totals_by_group: dict[str, int]
    bonus_claim: dict[str, int]
    mutual_agreement: bool
