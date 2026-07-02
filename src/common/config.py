"""Central configuration loader.

Every runtime parameter lives in config.json (spec: absolute prohibition on
hard-coding). This module is the only place that reads it; all code receives a
validated `Config` instance.
"""
from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Identity(_Strict):
    group_name: str
    students: list[str]
    github_repo: str
    timezone: str


class Scoring(_Strict):
    cop_win: int
    thief_win: int
    cop_loss: int
    thief_loss: int


class StartPositions(_Strict):
    mode: str = Field(pattern="^(random|fixed)$")
    fixed_cop: tuple[int, int]
    fixed_thief: tuple[int, int]


class Observation(_Strict):
    vision_radius: int


class IllegalMovePolicy(_Strict):
    llm_repair_attempts: int
    fallback: str


class Mcp(_Strict):
    cop_port: int
    thief_port: int
    cop_url: str
    thief_url: str
    token_env_cop: str
    token_env_thief: str


class Llm(_Strict):
    provider: str
    model: str
    temperature: float
    max_tokens: int
    api_key_env: str
    retries: int
    base_url: str | None = None  # OpenAI-compatible providers (e.g. DeepSeek)


class QLearning(_Strict):
    enabled: bool
    learning_rate: float
    discount_factor: float
    epsilon_start: float
    epsilon_min: float
    epsilon_decay: float
    training_episodes: int


class Gui(_Strict):
    enabled: bool
    cell_px: int
    speed_ms: int
    export_png: bool
    artifacts_dir: str


class Report(_Strict):
    recipient: str
    subject: str
    dry_run: bool
    credentials_path_env: str
    token_path_env: str
    gmail_scopes: list[str]


class Logging(_Strict):
    dir: str
    level: str
    jsonl: bool


class Config(_Strict):
    identity: Identity
    grid_size: tuple[int, int]
    max_moves: int
    num_games: int
    max_barriers: int
    scoring: Scoring
    turn_order_first: str = Field(pattern="^(cop|thief)$")
    start_positions: StartPositions
    observation: Observation
    illegal_move_policy: IllegalMovePolicy
    random_seed: int
    turn_timeout_s: int
    mcp: Mcp
    llm: Llm
    qlearning: QLearning
    gui: Gui
    report: Report
    logging: Logging

    @model_validator(mode="after")
    def _sanity(self) -> "Config":
        w, h = self.grid_size
        if w < 2 or h < 2:
            raise ValueError("grid_size must be at least 2x2")
        if self.max_moves < 1 or self.num_games < 1 or self.max_barriers < 0:
            raise ValueError("max_moves/num_games must be >=1, max_barriers >=0")
        if self.start_positions.mode == "fixed" and (
            tuple(self.start_positions.fixed_cop) == tuple(self.start_positions.fixed_thief)
        ):
            raise ValueError("fixed start positions must differ")
        return self


def load_config(path: str | Path) -> Config:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return Config.model_validate(raw)
