# PRD — Cloud Deployment & Security (Track F)

> Owns: deployment scripts/configs, token management, tunnel policies, bonus-round ops.
> Spec §6–§7: local proof first, then public cloud, token auth, firewall awareness.

## 1. Goal

Both MCP servers reachable at two public HTTPS URLs, secured by revocable tokens, with
the orchestrator (and LLM access) staying local (hybrid Approach 3) or using cloud API
(Approach 1). Produce the CLI-log evidence the README requires.

## 2. Functional requirements

1. **Phase L (local)**: 8001/8002 on localhost; full series green — precondition for cloud.
2. **Phase C (cloud)**: deploy `cop_server` + `thief_server` to a public platform
   (candidate order: Prefect Cloud (spec's example) → Render/Fly.io/Railway → ngrok tunnel
   as last resort). Output: `cop_mcp_url`, `thief_mcp_url` (both land in the report JSON).
3. **Auth**: bearer tokens per server; generation + rotation (revoke) procedure documented;
   tokens distributed to the opposing team out-of-band for the bonus.
4. **Network requirements**: URLs publicly reachable; verify from an external network
   (hotspot) — NOT from a corporate/university network that blocks non-standard ports.
5. **If tunneling (ngrok path)**: Traffic Policy with Basic Auth / Authorization header
   (`ollama.yaml`-style policy file), HTTPS enforced; Localtonet alternative documented;
   full Nginx reverse-proxy recipe (SSL termination, htpasswd, Certbot, UFW) documented
   as the "full engineering" option — implement only if needed.
6. **Never expose**: Ollama :11434 raw, API keys, credentials/token files. Outbound-only
   posture for the local client (no inbound ports on our machine).
7. **Bonus operations**: runbook for a cross-team series — exchange URLs+tokens, schedule,
   run 3+3 role-swapped sub-games, reconcile JSON, both send identical reports within the
   one-week bonus window.

## 3. Evidence duties (for README)

- CLI logs of the orchestrator talking to the **cloud** URLs (timestamps, tool calls).
- Screenshot of deployed services + token-auth rejection example (401 without token).

## 4. Acceptance criteria

- [ ] Both public URLs pass the 50-message integration test from an external network.
- [ ] Request without token → 401; with rotated-out token → 401; with valid → 200.
- [ ] Full autonomous cloud series (6 valid sub-games) completes; report email sent.
- [ ] Runbook executed once end-to-end as a rehearsal before contacting another team.
