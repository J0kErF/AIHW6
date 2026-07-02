"""Live window (only when config.gui.enabled and a display exists).

Cloud/headless paths never import this module — they use board_view+export only.
"""
from __future__ import annotations

from typing import Iterable

import pygame

from src.common.config import Config
from src.common.schemas import TurnResult
from src.gui.board_view import render


def run_live(events: Iterable[TurnResult], config: Config) -> None:
    pygame.init()
    screen: pygame.Surface | None = None
    clock = pygame.time.Clock()
    messages: list[tuple[str, str]] = []
    sub_game = 1
    for result in events:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                return
        if result.message:
            messages.append((result.actor.value, result.message))
        frame = render(result, config, messages, sub_game=sub_game)
        if screen is None:
            screen = pygame.display.set_mode(frame.get_size())
            pygame.display.set_caption("HW6 — Cop & Thief over MCP")
        screen.blit(frame, (0, 0))
        pygame.display.flip()
        if result.state.terminal:
            sub_game += 1
            messages.clear()
            pygame.time.wait(config.gui.speed_ms * 3)
        clock.tick(1000 / max(config.gui.speed_ms, 1))
    pygame.quit()
