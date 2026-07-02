"""Typed rule-violation errors (PRD_game_engine A6)."""


class IllegalActionError(Exception):
    """Base for every rejected action."""


class NotYourTurnError(IllegalActionError):
    pass


class OffBoardError(IllegalActionError):
    pass


class BarrierBlockedError(IllegalActionError):
    pass


class BarrierQuotaExceededError(IllegalActionError):
    pass


class BarrierNotAllowedError(IllegalActionError):
    """Thief tried to place a barrier, or cell already has one."""


class TerminalStateError(IllegalActionError):
    """Action applied to a finished sub-game."""


class IllegalPassError(IllegalActionError):
    """Pass used while legal actions exist."""


class TechnicalLossError(Exception):
    """Sub-game died from a technical failure — void it and re-run (spec §9)."""
