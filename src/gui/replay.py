"""Replay a recorded game in the live window (D7).

Usage: uv run python -m src.gui.replay artifacts/logs/<run>_turns.jsonl [--config config.json]
"""
from __future__ import annotations

import argparse

from src.common.config import load_config
from src.gui.events import read_turns
from src.gui.live import run_live


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("log", help="path to a *_turns.jsonl file")
    parser.add_argument("--config", default="config.json")
    args = parser.parse_args()
    run_live(read_turns(args.log), load_config(args.config))


if __name__ == "__main__":
    main()
