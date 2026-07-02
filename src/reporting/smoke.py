"""Manual smoke test: fixture report -> Gmail draft (needs Google setup, E1).

Run: uv run python -m src.reporting.smoke
Then check Gmail Drafts: body must be pure JSON.
"""
from __future__ import annotations

import random

from src.common.config import load_config
from src.common.logging import console
from src.engine.series import SeriesManager, random_policy
from src.reporting.builder import build_internal_report
from src.reporting.gmail_sender import send_report


def main() -> None:
    config = load_config("config.json")
    rng = random.Random(config.random_seed)
    sm = SeriesManager(config, random_policy(rng), random_policy(rng), rng=rng)
    sm.run_series()
    report = build_internal_report(sm.records, sm.totals(), config)
    result = send_report(report, config)
    console.print(f"[green]OK[/green] {result['mode']} created: {result['id']}")


if __name__ == "__main__":
    main()
