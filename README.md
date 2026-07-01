# Dual AI Agent Pursuit via MCP Servers — Cop & Thief under Partial Observability

> **moamteam** · Assignment 6, "Orchestration of AI Agents" (Dr. Yoram Segal, University of Haifa)
> Two autonomous LLM agents chase each other on a dynamic grid, coordinating exclusively
> through **free natural-language messages routed over two independent MCP servers** —
> from handshake to an automatically emailed JSON report, with zero human intervention.

> 🚧 **Status: foundation.** This README is the skeleton of the final scientific report;
> sections marked `TODO(evidence)` are filled from `artifacts/` as tracks land.
> Project docs: [`docs/`](docs/) · Plan & task board: [`plan/`](plan/)

---

## 1. Abstract

`TODO(final)` — 150-word summary: problem, architecture, result (6 valid autonomous
sub-games locally and in the cloud), and key findings on language-based coordination.

## 2. Formal model — Dec-POMDP

The pursuit game is a **Decentralized Partially Observable Markov Decision Process**:

$$\langle n,\; S,\; \{A_i\},\; P,\; R,\; \{\Omega_i\},\; O,\; \gamma \rangle$$

| Element | Instantiation here |
|---|---|
| $n$ | 2 agents (Cop, Thief) |
| $S$ | $\text{pos}_c \times \text{pos}_t \times 2^{\text{cells}}\ (\text{barriers}) \times \{0..25\}\ (\text{move counter}) \times \text{turn}$ |
| $A_{cop}$ | 8 compass moves ∪ {place\_barrier} (≤5, on current cell) |
| $A_{thief}$ | 8 compass moves |
| $P$ | deterministic transitions; illegal actions rejected by the engine |
| $R$ | capture: (+20, +5); escape at move 25: (+5, +10) — from `config.json` |
| $\Omega_i$ | own position, cells within vision radius $r$, known barriers, opponent's **free-text message** |
| $O$ | deterministic local vision + stochastic linguistic channel (message may be truthful, vague, or deceptive) |
| $\gamma$ | 0.9 (Q-learning experiments) |

`TODO(final)`: state-space size analysis per grid, and why the linguistic channel makes
$O$ the interesting object of study.

## 3. System architecture

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). Key law: the LLM lives only in the
**MCP client (orchestrator)**; the two **FastMCP servers** (cop :8001, thief :8002 →
public cloud URLs) expose tools only: `handshake, send_message, receive_message,
report_position, verify_state, get_game_config`, all bearer-token protected.

`TODO(evidence)`: deployment diagram with real cloud URLs.

## 4. Orchestration challenges & how we addressed them

`TODO(final)` — the mandated deep analysis:
1. **Protocol-less communication** — coordinating via free prose with no agreed schema.
2. **Linguistic ambiguity** — belief-grid updates from hedged/deceptive messages;
   quantified by belief-accuracy-vs-vision-radius experiments (sanity stage 3).
3. **Mutual understanding assurance** — turn verification, repair round-trips on
   unparseable LLM output, heuristic fallback guaranteeing liveness.

## 5. Experiments & results

- Sanity ladder 2×2 → 5×5: `TODO(evidence)` tables.
- Belief accuracy vs vision radius: `TODO(evidence)` plot.
- Q-learning learning curves (if enabled): `TODO(evidence)` plot.
- Full-series outcomes & score totals: `TODO(evidence)`.

## 6. Proofs of autonomous operation

- GUI screenshots (agents + barriers, live): `artifacts/screenshots/` `TODO(evidence)`
- CLI logs vs **cloud** MCP servers: `artifacts/logs/` `TODO(evidence)`
- Security: 401-without-token capture: `artifacts/security/` `TODO(evidence)`
- Report email (JSON-only body) as received: `TODO(evidence)`

## 7. Reproduce

```powershell
uv sync
# terminals 1+2
uv run python -m src.servers.cop_server
uv run python -m src.servers.thief_server
# terminal 3 — full autonomous series + GUI + report (draft mode by default)
uv run python -m src.orchestrator --config config.json
uv run pytest
```

Secrets required (never in repo): `ANTHROPIC_API_KEY`, `MCP_COP_TOKEN`, `MCP_THIEF_TOKEN`,
`GOOGLE_CREDENTIALS_PATH`, `GOOGLE_TOKEN_PATH` — see [`docs/ENVIRONMENT.md`](docs/ENVIRONMENT.md).

## 8. Team — moamteam

| Student | ID |
|---|---|
| Mohammad Yosef | [REDACTED] |
| Amear Abu Farekh | [REDACTED] |

`TODO(final)` — contribution split.
