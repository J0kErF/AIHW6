"""LLM-driven agent (C2/C3/C4/C5 glued): persona -> LLM -> parse -> guard.

Per turn: read opponent's free-text message, update belief, ask the LLM for
{action, message, belief}, repair once on parse failure, and let the heuristic
guard replace illegal proposals. The game NEVER crashes on a bad LLM reply.
"""
from __future__ import annotations

import json
from pathlib import Path

from src.agents.belief import BeliefGrid
from src.agents.llm_adapter import LlmAdapter, LlmError
from src.agents.parser import ParseFailure, parse_decision, to_engine_action
from src.agents.strategy import guard, heuristic_action
from src.common.config import Config
from src.common.schemas import Action, Direction, Move, Observation, PlaceBarrier, Role

_PERSONA_DIR = Path(__file__).parent / "personas"

REPAIR_PROMPT = (
    "Your previous reply was not valid JSON matching the contract. "
    "Reply again with ONLY the JSON object, nothing else."
)


def _action_name(a: Action) -> str:
    if isinstance(a, Move):
        return a.direction.value
    if isinstance(a, PlaceBarrier):
        return "barrier"
    return "pass"


class TurnDecision:
    def __init__(
        self, action: Action, message: str, used_fallback: bool, belief_guess: tuple[int, int] | None
    ) -> None:
        self.action = action
        self.message = message
        self.used_fallback = used_fallback
        self.belief_guess = belief_guess


class LlmAgent:
    def __init__(self, role: Role, config: Config, adapter: LlmAdapter) -> None:
        self.role = role
        self.config = config
        self.adapter = adapter
        self.system_prompt = (_PERSONA_DIR / f"{role.value}.md").read_text(encoding="utf-8")
        self.belief = BeliefGrid(config.grid_size)
        self.history: list[str] = []  # recent exchange, newest last

    def reset(self) -> None:
        self.belief = BeliefGrid(self.config.grid_size)
        self.history.clear()

    # -- per-turn pipeline -----------------------------------------------------
    def decide(self, obs: Observation, legal: list[Action], opponent_message: str | None) -> TurnDecision:
        # 1. belief update from hard evidence
        self.belief.motion_spread(list(map(tuple, obs.visible_barriers)))
        self.belief.observe(
            tuple(obs.self_pos),
            self.config.observation.vision_radius,
            tuple(obs.opponent_pos) if obs.opponent_pos else None,
        )
        if opponent_message:
            self.history.append(f"{self.role.opponent.value}: {opponent_message}")

        # 2. LLM proposal (with one repair round-trip)
        user = self._user_prompt(obs, legal, opponent_message)
        decision = None
        try:
            decision = parse_decision(self.adapter.complete(self.system_prompt, user))
        except (ParseFailure, LlmError):
            for _ in range(self.config.illegal_move_policy.llm_repair_attempts):
                try:
                    decision = parse_decision(
                        self.adapter.complete(self.system_prompt, user + "\n\n" + REPAIR_PROMPT)
                    )
                    break
                except (ParseFailure, LlmError):
                    continue

        # 3. belief hint from the LLM's linguistic interpretation
        if decision and decision.belief:
            self.belief.apply_hint(tuple(decision.belief))
        target = self.belief.argmax()

        # 4. legality guard / full heuristic fallback
        if decision is None:
            action = heuristic_action(self.role, obs, legal, target)
            message = self._fallback_message()
            used_fallback = True
            guess = None
        else:
            action, used_fallback = guard(
                self.role, to_engine_action(decision), legal, obs, target
            )
            message = decision.message or self._fallback_message()
            guess = tuple(decision.belief) if decision.belief else None

        self.history.append(f"{self.role.value}: {message}")
        self.history[:] = self.history[-12:]
        return TurnDecision(action, message, used_fallback, guess)

    # -- prompt building ---------------------------------------------------------
    def _user_prompt(self, obs: Observation, legal: list[Action], opponent_message: str | None) -> str:
        ctx = {
            "role": self.role.value,
            "grid_size": list(obs.grid_size),
            "self_pos": list(obs.self_pos),
            "round": obs.move_count,
            "max_rounds": obs.max_moves,
            "vision_radius": self.config.observation.vision_radius,
            "opponent_visible": obs.opponent_visible,
            "opponent_pos_if_visible": list(obs.opponent_pos) if obs.opponent_pos else None,
            "known_barriers": [list(b) for b in obs.visible_barriers],
            "barriers_left": obs.barriers_left,
            "belief_argmax": list(self.belief.argmax()),
            "legal_actions": [_action_name(a) for a in legal],
        }
        lines = [
            f"CONTEXT (JSON): {json.dumps(ctx)}",
            "",
            "RECENT EXCHANGE:",
            *(self.history[-6:] or ["(none yet)"]),
            "",
            f"OPPONENT'S LATEST MESSAGE: {opponent_message or '(none)'}",
            "",
            "Choose one legal action and compose your message. JSON only.",
        ]
        return "\n".join(lines)

    def _fallback_message(self) -> str:
        if self.role is Role.COP:
            return "Keep running — every step you take, I learn your pattern."
        return "Still free, officer. Your guesses are getting colder."


def direction_names() -> list[str]:
    return [d.value for d in Direction]
