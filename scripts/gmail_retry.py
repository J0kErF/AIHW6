"""Retries the Gmail draft smoke until the Gmail API is enabled (E1 tail-end).

Run: uv run python scripts/gmail_retry.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from src.reporting.smoke import main  # noqa: E402


def run() -> int:
    for attempt in range(20):  # ~20 minutes
        try:
            main()
            print("DRAFT CREATED — Gmail pipeline fully proven")
            return 0
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            tag = "API still disabled" if "accessNotConfigured" in msg or "has not been used" in msg else f"{type(e).__name__}: {msg[:180]}"
            print(f"attempt {attempt + 1}: {tag} — retrying in 60s", flush=True)
            time.sleep(60)
    print("GAVE UP after 20 attempts")
    return 1


if __name__ == "__main__":
    sys.exit(run())
