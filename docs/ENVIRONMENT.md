# ENVIRONMENT — Declared Development & Runtime Environment

## 1. Machine & OS

- Windows 11 Pro, PowerShell 5.1 primary (Git Bash available).
- Working directory: `.../ai arcth/aihw6/`.
- Course convention from previous HWs: per-HW project folder with its own virtual env.

## 2. Python toolchain

- **Python ≥ 3.11**, managed by **uv** (as demonstrated in the course video part B).
- Install uv (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
- Project managed by `pyproject.toml`; run with `uv sync` then `uv run <entry>`.
- Core dependencies (initial set):
  - `fastmcp` (MCP servers), `mcp` (client SDK)
  - `anthropic` and/or `openai` / `google-genai` (Approach-1 LLM)
  - `google-api-python-client`, `google-auth-oauthlib`, `google-auth-httplib2` (Gmail)
  - `numpy` (Q-table, belief grid), `pydantic` (schemas), `rich`/`textual` or `pygame`/`tkinter` (GUI — Track D decides)
  - `pytest` (tests)

## 3. Ports & processes (local phase)

| Process | Port | Notes |
|---|---|---|
| Cop MCP server | **8001** | FastMCP, HTTP transport |
| Thief MCP server | **8002** | FastMCP, HTTP transport |
| Orchestrator | — | client only, no inbound port |
| Ollama (only if Approach 2 explored) | 11434 | loopback only — NEVER exposed raw |

## 4. Secrets layout (NEVER in the repo)

```
%USERPROFILE%\secrets\moamteam-google\     # outside the project, per course guidance
├── credentials.json      # OAuth Desktop client (downloaded from Google Cloud Console)
└── token.json            # created on first OAuth run; delete to force re-auth
.env                      # local only, gitignored: LLM API keys, MCP bearer tokens
```

`.gitignore` MUST cover: `.env`, `*credentials*.json`, `*token*.json`, `.venv/`.

## 5. Google Cloud / Gmail API setup (from the course guide + videos)

One-time setup, on the team's free Gmail account:

1. **Google Cloud Console** → Select project → **New project**; name in snake_case
   (e.g. `moamteam_hw6`), lowercase, no spaces.
2. **APIs & Services → Library** → enable **Gmail API**; repeat and enable
   **Google Calendar API** (system requires both enabled per the guide).
3. **Google Auth Platform** (direct link if hidden:
   `https://console.cloud.google.com/auth/platform/overview?project=YOUR_PROJECT_ID`)
   → **Get started**: App name (e.g. `moamteam-hw6-mailer`), user support email = team Gmail,
   **Audience = External** (enables Testing mode + Test users), contact email(s) — add both
   team members, Create.
4. **Data access → Add or remove scopes** → manually add exactly:
   - `https://www.googleapis.com/auth/gmail.modify`
   - `https://www.googleapis.com/auth/calendar`
   → Add to table → Update.
5. **Clients → Create client** → Application type **Desktop app** →
   name e.g. `desktop-client-for-gmail` → Create → **Download JSON** →
   save as `credentials.json` in the **secrets folder outside the project**.
6. **Audience → Test users → Add users**: team Gmail + members' personal Gmails
   (up to 100). Only test users can complete OAuth while app is in Testing mode.
7. First program run opens the browser consent screen → approves → writes `token.json`
   next to `credentials.json`. Token expires periodically — delete it to force re-auth.

Known pitfalls (guide §22): "Access blocked / app isn't verified" is normal in Testing —
continue as a test user; if auth fails, re-check test user, scopes, and both APIs enabled;
if scopes changed, delete `token.json` and re-run.

## 6. LLM access

- **Primary (Approach 1):** cloud API key in `.env` (e.g. `ANTHROPIC_API_KEY`).
  Conversations are short and token consumption is low ⇒ negligible cost; free/basic
  models are acceptable per the spec.
- Model name, temperature, max tokens: **all in `config.json`**, not in code.

## 7. Cloud deployment phase

- Target: public deployment of both MCP servers (e.g. **Prefect Cloud** or similar),
  producing two public HTTPS URLs.
- **Token auth mandatory** (bearer token, revocable). URLs must be reachable from the
  public internet — do NOT test from inside a corporate/university firewall network.
- If tunneling from a local machine instead: **ngrok with a Traffic Policy** (Basic Auth,
  Authorization header) or Localtonet with HTTP Authentication — never a raw tunnel.

## 8. Runbook (once implemented)

```powershell
# terminal 1 + 2 — MCP servers
uv run python -m src.servers.cop_server    # :8001
uv run python -m src.servers.thief_server  # :8002
# terminal 3 — full local game (6 sub-games) + GUI + report
uv run python -m src.orchestrator --config config.json
# tests / sanity ladder
uv run pytest
uv run python -m src.orchestrator --config config.json --grid 2x2 --dry-run
```
