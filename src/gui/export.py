"""PNG evidence export (README requirement: GUI screenshots)."""
from __future__ import annotations

from pathlib import Path

import pygame


def save_png(surface: "pygame.Surface", path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surface, str(path))
    return path
