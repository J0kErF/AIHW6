"""Provider-agnostic LLM access (Track C, PRD_agents_llm C1).

Approach 1 (spec §7.1): the ORCHESTRATOR calls a public cloud API. The MCP
servers never see the LLM. Providers: "anthropic" (real), "mock" (full-pipeline
tests / --mock-llm ladder runs). Model, temperature, tokens: config only.
"""
from __future__ import annotations

import json
import os
import random
import re
import time
from typing import Protocol

from src.common.config import Config
from src.common.logging import JsonlLogger


class LlmError(Exception):
    pass


class LlmAdapter(Protocol):
    def complete(self, system: str, user: str) -> str: ...


class AnthropicAdapter:
    def __init__(self, config: Config, logger: JsonlLogger | None = None) -> None:
        api_key = os.environ.get(config.llm.api_key_env)
        if not api_key:
            raise LlmError(
                f"env var {config.llm.api_key_env} not set — put the API key in .env "
                "(never in the repo) or run with --mock-llm"
            )
        import anthropic  # lazy: mock runs must not require the package/key

        self._client = anthropic.Anthropic(api_key=api_key)
        self._cfg = config.llm
        self._log = logger

    def complete(self, system: str, user: str) -> str:
        last_err: Exception | None = None
        for attempt in range(self._cfg.retries + 1):
            try:
                t0 = time.time()
                resp = self._client.messages.create(
                    model=self._cfg.model,
                    system=system,
                    max_tokens=self._cfg.max_tokens,
                    temperature=self._cfg.temperature,
                    messages=[{"role": "user", "content": user}],
                )
                text = "".join(b.text for b in resp.content if b.type == "text")
                if self._log:
                    self._log.log(
                        "llm_call",
                        model=self._cfg.model,
                        latency_s=round(time.time() - t0, 3),
                        in_tokens=resp.usage.input_tokens,
                        out_tokens=resp.usage.output_tokens,
                        attempt=attempt,
                    )
                return text
            except Exception as e:  # noqa: BLE001 - provider errors are opaque
                last_err = e
        raise LlmError(f"LLM failed after {self._cfg.retries + 1} attempts: {last_err}")


class OpenAICompatAdapter:
    """OpenAI-compatible providers — used for DeepSeek (config.llm.base_url)."""

    def __init__(self, config: Config, logger: JsonlLogger | None = None) -> None:
        api_key = os.environ.get(config.llm.api_key_env)
        if not api_key:
            raise LlmError(
                f"env var {config.llm.api_key_env} not set — put the API key in .env "
                "(never in the repo) or run with --mock-llm"
            )
        from openai import OpenAI  # lazy

        # hard request timeout so one slow call can't eat the whole turn budget
        self._client = OpenAI(api_key=api_key, base_url=config.llm.base_url, timeout=45.0)
        self._cfg = config.llm
        self._log = logger

    def complete(self, system: str, user: str) -> str:
        last_err: Exception | None = None
        for attempt in range(self._cfg.retries + 1):
            try:
                t0 = time.time()
                resp = self._client.chat.completions.create(
                    model=self._cfg.model,
                    temperature=self._cfg.temperature,
                    max_tokens=self._cfg.max_tokens,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                )
                if self._log:
                    usage = resp.usage
                    self._log.log(
                        "llm_call",
                        model=self._cfg.model,
                        latency_s=round(time.time() - t0, 3),
                        in_tokens=getattr(usage, "prompt_tokens", None),
                        out_tokens=getattr(usage, "completion_tokens", None),
                        attempt=attempt,
                    )
                return resp.choices[0].message.content or ""
            except Exception as e:  # noqa: BLE001
                last_err = e
        raise LlmError(f"LLM failed after {self._cfg.retries + 1} attempts: {last_err}")


_MOCK_MESSAGES = {
    "cop": [
        "I'm sweeping the area methodically. You can't hide forever.",
        "Something moved near the wall — closing the distance now.",
        "I've set up my position. Every exit is being watched.",
        "You left traces. I am closer than you think.",
    ],
    "thief": [
        "You're cold, officer. I'm nowhere near where you're looking.",
        "Heading for the far corner... or maybe that's what I want you to think.",
        "Nice barrier. Shame it's guarding an empty square.",
        "I can see you stumbling around. This grid is my home.",
    ],
}


class MockAdapter:
    """Deterministic, key-free stand-in that exercises the REAL prompt→parse path.

    It reads the CONTEXT JSON block the agent embeds in the user prompt, picks a
    legal action, and answers in the exact output contract — including a slice of
    deliberately malformed replies to exercise the repair/fallback machinery.
    """

    def __init__(self, seed: int = 0, malformed_rate: float = 0.0) -> None:
        self.rng = random.Random(seed)
        self.malformed_rate = malformed_rate

    def complete(self, system: str, user: str) -> str:
        if self.rng.random() < self.malformed_rate:
            return "Sure! I think I will just wander around aimlessly today."
        m = re.search(r"CONTEXT \(JSON\): (\{.*?\})\n", user, re.DOTALL)
        ctx = json.loads(m.group(1)) if m else {}
        legal = ctx.get("legal_actions", ["pass"])
        role = ctx.get("role", "cop")
        w, h = ctx.get("grid_size", [5, 5])
        decision = {
            "action": self.rng.choice(legal),
            "message": self.rng.choice(_MOCK_MESSAGES.get(role, ["..."])),
            "belief": [self.rng.randrange(w), self.rng.randrange(h)],
            "reasoning": "mock heuristic wander",
        }
        return json.dumps(decision)


def make_adapter(config: Config, logger: JsonlLogger | None = None) -> LlmAdapter:
    provider = config.llm.provider
    if provider == "anthropic":
        return AnthropicAdapter(config, logger)
    if provider in ("deepseek", "openai"):
        return OpenAICompatAdapter(config, logger)
    if provider == "mock":
        return MockAdapter(seed=config.random_seed)
    raise LlmError(
        f"unknown llm.provider {provider!r} (supported: anthropic, deepseek, openai, mock)"
    )
