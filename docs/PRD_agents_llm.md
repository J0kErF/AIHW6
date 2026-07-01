# PRD — Agents, LLM & Strategy (Track C)

> Owns: `src/agents/` + `src/orchestrator.py`. The heart of the grade: **communication and
> orchestration of the agent pair is the central success metric** (spec §3).

## 1. Goal

Two LLM personas (Cop, Thief) that each turn: read the opponent's free-text message,
update a belief about the opponent's position, choose a legal action, and compose their
own free-text message (truthful or deceptive). The orchestrator (MCP client) wires
engine ⇄ LLM ⇄ MCP servers into a fully autonomous loop.

## 2. Functional requirements

1. **LLM adapter** (Approach 1): provider, model, temperature, max_tokens from config;
   provider-agnostic interface (`complete(system, messages) -> text`); retries + timeout;
   token/cost counter logged per game.
2. **Personas**: system prompts (in `config`/prompt files, not hard-coded) defining role,
   goals, rules summary, output format:
   `{"action": "...", "message": "<free text>", "belief": [x,y], "reasoning": "..."}`.
   JSON-fenced output parsed defensively; on parse failure → one repair round-trip → fallback heuristic.
3. **Free-language requirement (F-07)**: messages must be natural prose — engine never
   transmits coordinates between agents; personas explicitly allowed to bluff.
4. **Belief tracking (F-10)**: per-agent belief grid over opponent position; updated from
   (a) own vision radius observation, (b) LLM interpretation of the message,
   (c) motion constraints (opponent moves ≤ 1 cell/turn). This is README analysis material.
5. **Decision mechanism (F-09)**:
   - Baseline **heuristic**: Cop minimizes expected Chebyshev distance to belief mass,
     considers barrier placement value; Thief maximizes distance / exploits ambiguity.
   - Optional **Tabular Q-Learning** module (`agents/qlearn.py`): Bellman update
     `Q(s,a) += α [r + γ·max Q(s',·) − Q(s,a)]`, ε-greedy, α≈0.1, γ≈0.9 (all from config);
     trained by self-play episodes; learning-curve data exported for README plots.
   - LLM proposes; strategy layer validates/repairs to legal action (guard from Track A).
6. **Orchestrator loop**: sub-game loop per `GAME_RULES.md`; turn timeout
   (`config.turn_timeout_s`); technical-failure detection → void & re-run sub-game;
   after 6 valid → hand `Totals` to Reporter (Track E).
7. **Interoperability mode**: orchestrator can point cop/thief tool URLs at ANY MCP
   servers (ours local, ours cloud, opponent's cloud) via config — required for bonus.

## 3. Acceptance criteria

- [ ] Full autonomous 6-sub-game series on 5×5 with zero manual input, local and cloud.
- [ ] Transcript shows genuinely free-form messages (varied phrasing, occasional deception)
      — not templated coordinate strings.
- [ ] Illegal LLM proposals never crash a game (guard + fallback path tested).
- [ ] Belief-accuracy metric logged per turn (distance between belief argmax and truth) —
      feeds README ambiguity analysis (sanity stage 3 requirement).
- [ ] If Q-Learning enabled: learning curve CSV + plot generated automatically.
