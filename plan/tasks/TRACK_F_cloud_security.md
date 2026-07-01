# TRACK F — Cloud Deployment, Security & Bonus Ops

> Read first: `docs/PRD_cloud_security.md`, `docs/ARCHITECTURE.md` §6–7.
> You own `deploy/` + cloud runbook. **Start gate: SP-3** (local E2E green). Before that,
> do the paper/setup tasks (F1–F3) in parallel.

## Mission
Two public, token-protected HTTPS MCP URLs; security evidence; cloud E2E; bonus-round
operations with another team.

## Tasks (pre-gate, parallel)
- [ ] F1. Choose platform + create account: try **Prefect Cloud** (spec's example) first;
       fallbacks: Render → Fly.io → Railway; document choice + constraints in
       `docs/RUNBOOK_cloud.md` (you create it).
- [ ] F2. Token scheme: generate strong bearer tokens per role; storage (.env/platform
       secrets); rotation=revoke drill written down.
- [ ] F3. Draft `deploy/` scripts/Dockerfile (uv-based image) targeting the chosen platform;
       confirm Track B code has no localhost assumptions.

## Tasks (post SP-3)
- [ ] F4. Deploy cop + thief servers → record `cop_mcp_url`, `thief_mcp_url` in config.
- [ ] F5. Security proofs: curl without token → 401 (save output); with token → 200;
       rotate token → old 401. Archive to `artifacts/security/`.
- [ ] F6. External-network verification (phone hotspot): tool list + 50-message test
       against both URLs. (Spec warning: never validate only from a corporate/university net.)
- [ ] F7. Cloud E2E: orchestrator local (hybrid Approach 3, outbound-only) → full 6-sub-game
       series vs cloud URLs → archive CLI logs (`artifacts/logs/cloud_run_*.jsonl`) — README evidence.
- ~~F8. Bonus ops~~ — **WAIVED** (bonus window closed for students, 2026-07-02). Keep the
       interop posture anyway (stable tool names, token exchange procedure documented).
- [ ] F9. Teardown/cost check + how-to-redeploy notes in the runbook.

## Definition of Done
Public URLs live + secured + evidenced; cloud series completed & logged; runbook lets any
teammate redeploy in <30 min. (Bonus already waived — see TASK_BOARD contract log.)
