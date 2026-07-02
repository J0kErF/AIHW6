"""Board renderer (Track D). Pure pygame Surface drawing — no display needed,
so the same code powers the live window, headless PNG export, and tests.
Tech decision (PRD_gui §3): pygame-ce — Surface rendering works without a
display and `pygame.image.save` gives free PNG evidence for the README.
"""
from __future__ import annotations

import pygame

from src.common.config import Config
from src.common.schemas import Role, TurnResult

# palette
BG = (24, 26, 32)
GRID_LINE = (70, 74, 84)
CELL = (38, 41, 50)
BARRIER = (120, 66, 18)
COP = (66, 135, 245)
THIEF = (235, 84, 84)
TEXT = (230, 230, 230)
PANEL_BG = (30, 32, 40)

HEADER_H = 48
PANEL_W = 340
MAX_FEED = 12


def _font(size: int) -> "pygame.font.Font":
    if not pygame.font.get_init():
        pygame.font.init()
    return pygame.font.Font(None, size)


def render(result: TurnResult, config: Config, messages: list[tuple[str, str]] | None = None,
           sub_game: int = 1) -> "pygame.Surface":
    """Draw one frame from a TurnResult (+ optional NL message feed)."""
    w, h = config.grid_size
    cell = config.gui.cell_px
    board_w, board_h = w * cell, h * cell
    surface = pygame.Surface((board_w + PANEL_W, HEADER_H + board_h))
    surface.fill(BG)
    state = result.state

    # header
    font = _font(28)
    small = _font(22)
    status = (
        f"sub-game {sub_game}/{config.num_games}   "
        f"round {state.move_count}/{config.max_moves}   "
        f"turn: {state.turn.value}   barriers {state.barriers_used}/{config.max_barriers}"
    )
    if state.terminal:
        status = f"sub-game {sub_game}: {state.winner.value.upper()} wins ({state.reason})"
    surface.blit(font.render(status, True, TEXT), (12, 12))

    # board
    barriers = {tuple(b) for b in state.barriers}
    for x in range(w):
        for y in range(h):
            rect = pygame.Rect(x * cell + 1, HEADER_H + y * cell + 1, cell - 2, cell - 2)
            pygame.draw.rect(surface, BARRIER if (x, y) in barriers else CELL, rect)
            pygame.draw.rect(surface, GRID_LINE, rect, width=1)
    for role, pos, color in (
        (Role.COP, state.cop_pos, COP),
        (Role.THIEF, state.thief_pos, THIEF),
    ):
        cx = pos[0] * cell + cell // 2
        cy = HEADER_H + pos[1] * cell + cell // 2
        pygame.draw.circle(surface, color, (cx, cy), cell // 3)
        label = _font(cell // 2).render(role.value[0].upper(), True, TEXT)
        surface.blit(label, label.get_rect(center=(cx, cy)))

    # message feed panel (proof of free-language communication)
    panel = pygame.Rect(board_w, HEADER_H, PANEL_W, board_h)
    pygame.draw.rect(surface, PANEL_BG, panel)
    surface.blit(small.render("messages", True, TEXT), (board_w + 10, HEADER_H + 8))
    y_off = HEADER_H + 36
    for speaker, text in (messages or [])[-MAX_FEED:]:
        line = f"{speaker}: {text}"
        if len(line) > 44:
            line = line[:41] + "..."
        color = COP if speaker == Role.COP.value else THIEF
        surface.blit(small.render(line, True, color), (board_w + 10, y_off))
        y_off += 24
    return surface
