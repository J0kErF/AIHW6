"""Structured logging: JSONL (machine evidence) + rich console (humans)."""
from __future__ import annotations

import json
import time
from pathlib import Path

from rich.console import Console

console = Console()


class JsonlLogger:
    def __init__(self, path: str | Path, echo: bool = False) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.echo = echo

    def log(self, event: str, **fields: object) -> None:
        record = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "event": event, **fields}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
        if self.echo:
            console.log(f"[dim]{event}[/dim] {fields}")


def run_logger(log_dir: str | Path, run_id: str, echo: bool = False) -> JsonlLogger:
    return JsonlLogger(Path(log_dir) / f"{run_id}.jsonl", echo=echo)
