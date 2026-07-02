# GRADING_RUBRIC — Self-Audit Checklist (target: 98%+)

> Reconstructed from the assignment spec (§3, §11, §13–14) + course submission guidelines
> conventions (config, README, no hardcode, clean repo). We treat every "recommended" in
> the spec as **mandatory for us** — that's where the last points live.

## A. Core pipeline (the heavy weight — spec's stated success metric)

- [x] Fully autonomous end-to-end run: handshake → 6 valid sub-games → auto email. **Zero clicks.**
- [x] Two truly separate MCP servers (processes/URLs), FastMCP, tools only — LLM strictly client-side.
- [x] Free natural-language messaging demonstrably NOT a rigid protocol
      (evidence: varied transcripts, deception example, no coordinates-in-message convention).
- [x] Partial observability actually matters (vision radius < board ⇒ inference visible in logs).
- [x] Mutual location verification tooling present (stage-2 requirement).
- [x] Technical-loss handling: voided + re-run to exactly 6 valid sub-games.

## B. Rules fidelity

- [x] Grid generic (2×2 … 5×5+) — config only; 8-direction movement; thief moves first.
- [x] Capture & 25-move win conditions exact; barrier semantics exact
      (cop-only, current cell, blocks both, max 5).
- [x] Scoring 20/5/10/5 from config; totals math correct (max 90 / min 30 in bonus format).

## C. Configuration & engineering hygiene

- [x] `config.json` holds ALL params incl. the spec's named ones:
      `grid_size, max_moves, num_games, max_barriers, scoring.*`.
- [x] Zero hard-coded parameters (grep-audited). Typed models, tests green.
- [x] Secrets outside repo; `.gitignore` covers env/credentials/token.
- [x] Public GitHub repo, clean commits, runnable instructions.

## D. Cloud & security

- [x] Two public HTTPS URLs; reachable from open internet — hw6-cop-mcp / hw6-thief-mcp
      .onrender.com; full E2E series completed against them (2026-07-02).
- [x] Token auth + documented revoke; wrong-token rejection captured in
      `artifacts/security/cloud_verify_20260702_210304.txt`.
- [x] Approach-1/3 posture: local client outbound-only; no inbound ports; Ollama unused.

## E. Reporting

- [x] Email to `rmisegal+uoh26b@gmail.com`, **JSON-only body**, exact schema keys.
- [x] Sent automatically by cop-side pipeline at series end.
- [x] Gmail API with OAuth client + token (course-guide flow), not SMTP/password.

## F. Scientific README (a full grade component — spec §11)

- [x] Formal Dec-POMDP model: tuple ⟨n, S, {Aᵢ}, P, R, {Ωᵢ}, O, γ⟩ with concrete definitions
      of state space, action sets, transition, reward table, observation spaces, γ.
- [x] Deep orchestration-challenge analysis: free-language protocol-less communication,
      linguistic ambiguity handling, mutual-understanding techniques.
- [x] Visual proofs: GUI screenshots (agents + barriers live), cloud CLI logs,
      learning curves if Q-Learning used.
- [x] High scientific register, English, structured, referenced.

## G. Above-and-beyond (the 98%→100% margin)

- [x] Q-Learning implemented (optional in spec ⇒ differentiator) with learning-curve plot.
- [x] Sanity ladder automated as tests (2×2/3×3/4×4/5×5) with recorded metrics.
- [x] Belief-accuracy analytics + ambiguity experiment (vision radius sweep) in README.
- [x] GUI polish: message feed panel + replay.
- [~] Bonus round — WAIVED (window closed for students); interop posture kept
      (stable tool contract + token exchange procedure documented).

## Known point-loss traps (from spec, explicit)

1. Free text in email body → parsing failure at grader side.
2. Fewer than 6 valid sub-games / counting a technical loss.
3. Hard-coded grid or scores.
4. MCP URLs behind a firewall / not public.
5. LLM baked into the MCP server (architecture violation).
6. Bonus reports not byte-identical between the two teams → 0 for both.
