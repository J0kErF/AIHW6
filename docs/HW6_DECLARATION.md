# HW6 Declaration — Dual AI Agent Conversation via MCP Servers

> **Course:** Orchestration of AI Agents — Dr. Yoram Segal, University of Haifa
> **Assignment:** ex06 (Lesson L09, published 19-06-2026, v1.0)
> **Source spec:** `../../ex06-Dual AI agent race via MCP servers.pdf`
> **Team:** moamteam · **Timezone:** Asia/Jerusalem

---

## 1. What the assignment IS

Build a **complete, end-to-end game pipeline** in which two independent AI agents —
**Cop** and **Thief** — play a dynamic pursuit game ("cops and robbers") on a 2D grid,
**fully autonomously**, from handshake to the final automated summary email.

The system must make the two agents:

1. **Decipher** each other's messages written in **free natural language** (no rigid protocol,
   no raw coordinates exchanged as the protocol).
2. **Infer** the opponent's likely position from **partial observation**.
3. **Translate** those inferences into **physical moves** on the grid.

> **The central success metric is the communication + orchestration capability of the
> agent pair — NOT the game strategy or who wins.**

Each team must run a valid series of games between its own Cop and Thief, managed over
its **two MCP servers**, with **zero manual intervention** — from game start to the
automated JSON report email.

## 2. What the assignment is NOT

- NOT a competition about winning the game (strategy quality is secondary).
- NOT a reinforcement-learning course requirement — **Q-Learning is optional/recommended only**.
- NOT allowed: hard-coded game parameters (absolute prohibition — everything in `config.json`).
- NOT allowed: agents exchanging raw numeric positions as their protocol — messages are free text.
- NOT allowed: free text in the report email body — **JSON only**.

## 3. The grounds (rules of the world)

See `GAME_RULES.md` for the full normative rules. Summary:

| Item | Value (default, configurable) |
|---|---|
| Board | 2D grid, default **5×5**, dynamic via config (generic architecture) |
| Movement | 8 directions incl. diagonals; turn-based; **Thief moves first** |
| Sub-game | One chase round, max **25 moves** |
| Game | Series of **6 sub-games**, results accumulated & reported together |
| Cop win | Cop lands exactly on Thief's square (capture) |
| Thief win | Thief survives 25 moves without capture |
| Barriers | Cop only; instead of moving, drops a barrier **on his current square**; blocks Thief AND Cop; max **5** per sub-game |
| Scoring | Cop wins: Cop 20 / Thief 5 · Thief wins: Thief 10 / Cop 5 |
| Score range | Max team score in a full game: 90 (3×20 as cop + 3×10 as thief); minimum 30 |

The game is formally a **Dec-POMDP** (Decentralized Partially Observable Markov Decision
Process): ⟨n, S, {Aᵢ}, P, R, {Ωᵢ}, O, γ⟩ — this modeling is a **mandatory section of the
scientific README**.

## 4. The environment

Declared normative environment for this project (details: `ENVIRONMENT.md`):

- **OS:** Windows 11 Pro, PowerShell; POSIX via Git Bash where needed.
- **Python:** ≥ 3.11, managed with **uv** (virtual env + `pyproject.toml`).
- **MCP:** two independent **FastMCP** servers — `cop_server` (port **8001**) and
  `thief_server` (port **8002**) on localhost first; cloud later.
- **LLM access — Approach 1 (recommended):** public cloud API (Anthropic / OpenAI / Gemini)
  called by the **MCP client (orchestrator)**. Approach 3 (hybrid: local client + LLM,
  cloud MCP servers, outbound HTTPS only) is our safe local-dev fallback.
  The LLM is **never hosted inside the MCP server** — server exposes tools only.
- **Cloud stage:** deploy the two MCP servers to a public cloud (e.g. Prefect Cloud or
  similar), with **token-based auth** (revocable), two public URLs (one per agent), no
  corporate firewall in the path.
- **Email:** Gmail API via Google API Client (OAuth Desktop client + token), sender is
  our free Gmail account; report goes to **`rmisegal+uoh26b@gmail.com`**.

## 5. Mandatory deliverables

1. **Public GitHub repo** with all source code.
2. **`README.md` scientific report** at repo root (high scientific level):
   - Formal Dec-POMDP modeling with the tuple and the state/observation spaces.
   - Deep analysis of orchestration challenges: free-language communication without a
     predefined protocol, handling linguistic ambiguity, methods for ensuring mutual understanding.
   - Visualization & hard proofs: learning curves (if Q-Table used), **GUI screenshots**
     showing real-time agent movement + barriers, **CLI logs** proving valid communication
     against the **cloud** MCP servers.
3. **Central config file** (`config.json`) — all parameters, zero hard-coding.
4. **Automated report email**: after 6 valid sub-games, the **Cop agent** automatically sends
   a single email whose body is **only** the internal-game JSON (schema: `REPORTING_SPEC.md`).
   Sub-games ended by technical failure are void and must be re-run to complete the quota of 6.

## 6. Bonus (up to 10 points toward final project) — ⛔ WAIVED for this team (window closed; kept for reference)

Inter-group competition, **within one week of assignment publication**:

- Two groups play a full two-sided cloud game: 6 sub-games —
  first 3: our Cop vs their Thief; last 3: their Cop vs our Thief.
- Each group sends a **separate** report email with **exactly the same results**
  (full mutual agreement on the JSON data). `mutual_agreement: true`.
- Winner of a series: 10 pts, loser: 7 pts, absolute tie: 5 pts each.
- Final bonus = **average** over all valid series; playing multiple groups is encouraged.
- Report mismatch or no agreement ⇒ **0 points for both** for that series.

## 7. Recommended development order (from the spec, Table 4)

1. Game logic & rules (grid, moves, barriers, capture).
2. Basic MCP infrastructure — two separate servers, mutual location verification.
3. Full local run (localhost, separate ports, complete pipeline).
4. Decision mechanism (heuristic / distance-based / Q-Table).
5. Natural-language integration — replace any rigid protocol with free-text messages.
6. GUI — real-time visualization of agents + barriers.
7. Cloud deployment (tokens, tunneling, cyber hygiene).
8. Gmail API — automated JSON report after 6 sub-games.

## 8. Sanity-check ladder (mandatory practice, from the spec, Table 2)

| Stage | Grid | Purpose | Complexity |
|---|---|---|---|
| 1 | 2×2 | algorithmic sanity, base pipeline integration, message-passing validation | very low |
| 2 | 3×3 / 3×2 | coordination convergence, hyper-parameter calibration, failure identification | medium |
| 3 | 4×4 / 4×3 | effect of observation ambiguity; initial distance vs vision radius | high |
| 4 | 5×5 | final test run, graph generation, full game analysis | maximal |

## 9. Key insights to honor (spec §14)

- **Infrastructure before gameplay** — the value is the orchestration, not the game result.
- **Free language, not a rigid protocol** — agents are independent; internal implementation
  of the other side must not matter.
- **Client/Server separation** — the LLM lives with the client (orchestrator); MCP servers expose tools only.
- **Local → cloud gradually** — localhost ports → cloud deploy → inter-group competition.
- **Security & automation** — tokens (OAuth, ngrok traffic policy) instead of passwords; Gmail API for autonomous reporting.
- **Soft skills** — teamwork, uncertainty and deadline management (Prisoner's-Dilemma-inspired bonus).
