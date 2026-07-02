# RUNBOOK — Cloud Deployment (Track F)

> Goal: two public HTTPS URLs (cop, thief), token-protected, reachable from the open
> internet. Everything below is prepared; the ONLY human step is creating the platform
> account (one browser signup) — after that each command is copy-paste.

## 0. What's already prepared

- `deploy/Dockerfile` — single image, role via `MCP_ROLE=cop|thief`, honors PaaS `PORT`.
- `deploy/entrypoint.py` — role/port from env; binds 0.0.0.0.
- `render.yaml` (repo root) — Render.com blueprint deploying BOTH services from one repo.
- Servers are stateless per-session and transport-agnostic — no code change needed.

## 1. Recommended path: Render.com (free tier, Docker, zero CLI)

1. **Human step:** create account at render.com (GitHub login is fastest) — 2 minutes.
2. Push this repo to GitHub (user provides URL at submission; see AGENT_MEMORY ground truth).
3. Render dashboard → New → **Blueprint** → select the repo. `render.yaml` creates:
   - `hw6-cop-mcp`  (env `MCP_ROLE=cop`)
   - `hw6-thief-mcp` (env `MCP_ROLE=thief`)
4. In each service → Environment → set the token secret:
   - cop:   `MCP_COP_TOKEN=<strong random>`
   - thief: `MCP_THIEF_TOKEN=<strong random>`
   Generate with: `python -c "import secrets;print(secrets.token_urlsafe(24))"`
5. Copy the two public URLs, append `/mcp`, and update `config.json`:
   ```json
   "cop_url":  "https://hw6-cop-mcp.onrender.com/mcp",
   "thief_url": "https://hw6-thief-mcp.onrender.com/mcp"
   ```
6. Put the same tokens in local `.env` (`MCP_COP_TOKEN=`, `MCP_THIEF_TOKEN=`).

## 2. Verify (evidence for README — save outputs to artifacts/security/)

```powershell
# 401 without token (auth proof) — handshake with wrong token must fail
uv run python -c "import asyncio;from src.servers.client import GameMcpClient;asyncio.run((lambda: (lambda c: c)(None))())"  # see scripts below
uv run python scripts/cloud_verify.py            # runs: tool list, bad-token, 50-msg test
```

`scripts/cloud_verify.py` (prepared) runs the full acceptance battery against the URLs in
config and writes `artifacts/security/cloud_verify_<ts>.txt`.

## 3. Cloud E2E (the graded run)

```powershell
uv run python -m src.orchestrator --no-email     # hybrid: local client -> cloud servers
# final submission run (after E1 Google setup, dry_run=false):
uv run python -m src.orchestrator
```

## 4. Rules of engagement (spec §6)

- Verify from an OPEN network (phone hotspot), never only from a university/corporate net.
- Rotate a token to revoke access: change the env var on the platform → redeploy (1 click).
- Never expose Ollama/API keys; client is outbound-only (Approach 3 hybrid).

## 5. Fallbacks

| Option | When | Note |
|---|---|---|
| Fly.io (`fly launch` per role) | Render free tier too slow/cold | needs CC on file |
| Railway | same | similar blueprint flow |
| ngrok + Traffic Policy (Basic Auth) | zero-account demo from this PC | machine must stay on; policy file in spec §7.2 |

## 6. Cold-start warning (Render free tier)

Free services sleep after idle; first handshake may take ~50 s. Our client retries and
`turn_timeout_s=180` absorbs it. For the graded run, hit each URL once to warm it.
