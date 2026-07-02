"""Event plumbing: live observer hookup + JSONL replay source (read-only)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

from src.common.schemas import TurnResult


def write_turn(path: str | Path, result: TurnResult) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(result.model_dump_json() + "\n")


def read_turns(path: str | Path) -> Iterator[TurnResult]:
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield TurnResult.model_validate(json.loads(line))
