import copy
import json
from pathlib import Path

import pytest

from src.common.config import Config

ROOT = Path(__file__).resolve().parents[1]
_BASE = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))


def make_config(**overrides) -> Config:
    """Config from the real config.json with test overrides (deep-merged)."""
    raw = copy.deepcopy(_BASE)

    def merge(dst: dict, src: dict) -> None:
        for k, v in src.items():
            if isinstance(v, dict) and isinstance(dst.get(k), dict):
                merge(dst[k], v)
            else:
                dst[k] = v

    merge(raw, overrides)
    return Config.model_validate(raw)


@pytest.fixture
def config() -> Config:
    return make_config()
