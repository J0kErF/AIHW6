"""Defensive parsing of LLM output into a typed decision (PRD_agents_llm C3)."""
from __future__ import annotations

import json
import re

from pydantic import BaseModel, ConfigDict, ValidationError

from src.common.schemas import Action, Direction, Move, Pass, PlaceBarrier

ACTION_NAMES = {d.value for d in Direction} | {"barrier", "pass"}


class AgentDecision(BaseModel):
    model_config = ConfigDict(extra="ignore")
    action: str
    message: str = ""
    belief: tuple[int, int] | None = None
    reasoning: str | None = None


class ParseFailure(Exception):
    pass


_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


def parse_decision(text: str) -> AgentDecision:
    """Extract the first JSON object from (possibly chatty) LLM text."""
    match = _JSON_RE.search(text)
    if not match:
        raise ParseFailure(f"no JSON object in LLM output: {text[:120]!r}")
    try:
        decision = AgentDecision.model_validate(json.loads(match.group(0)))
    except (json.JSONDecodeError, ValidationError) as e:
        raise ParseFailure(f"invalid decision JSON: {e}") from e
    if decision.action not in ACTION_NAMES:
        raise ParseFailure(f"unknown action {decision.action!r}")
    return decision


def to_engine_action(decision: AgentDecision) -> Action:
    if decision.action == "barrier":
        return PlaceBarrier()
    if decision.action == "pass":
        return Pass()
    return Move(direction=Direction(decision.action))
