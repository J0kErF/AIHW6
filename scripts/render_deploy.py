"""Fully automated Render deployment via REST API (Track F, zero-dashboard).

Needs ONE secret in .env: RENDER_API_KEY (dashboard -> Account Settings -> API Keys).
Then this script, idempotently:
  1. finds the owner + existing services (by name) or creates both web services
     from github.com/J0kErF/AIHW6 (Docker, deploy/Dockerfile, free plan);
  2. generates strong bearer tokens, sets them as env vars on the services AND
     writes them to local .env (MCP_COP_TOKEN / MCP_THIEF_TOKEN);
  3. waits for the deploys to go live;
  4. writes the two public URLs (with /mcp path) into config.json;
  5. prints next commands (verify battery + cloud E2E).

Run: uv run python scripts/render_deploy.py
"""
from __future__ import annotations

import json
import os
import re
import secrets
import sys
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

API = "https://api.render.com/v1"
REPO = "https://github.com/J0kErF/AIHW6"
SERVICES = {
    "cop": {"name": "hw6-cop-mcp", "role": "cop", "token_env": "MCP_COP_TOKEN"},
    "thief": {"name": "hw6-thief-mcp", "role": "thief", "token_env": "MCP_THIEF_TOKEN"},
}


def die(msg: str) -> None:
    print(f"ERROR: {msg}")
    sys.exit(1)


def main() -> None:
    load_dotenv(ROOT / ".env")
    key = os.environ.get("RENDER_API_KEY")
    if not key:
        die(
            "RENDER_API_KEY not set. Dashboard -> Account Settings -> API Keys -> "
            "Create, then add RENDER_API_KEY=rnd_... to aihw6/.env and rerun."
        )
    client = httpx.Client(
        base_url=API, headers={"Authorization": f"Bearer {key}"}, timeout=30
    )

    owners = client.get("/owners", params={"limit": 20}).json()
    if not owners:
        die("no Render owners visible with this key")
    owner_id = owners[0]["owner"]["id"]
    print(f"owner: {owner_id}")

    existing = {
        s["service"]["name"]: s["service"]
        for s in client.get("/services", params={"limit": 50}).json()
    }

    urls: dict[str, str] = {}
    tokens: dict[str, str] = {}
    for role, spec in SERVICES.items():
        token = os.environ.get(spec["token_env"]) or secrets.token_urlsafe(24)
        tokens[spec["token_env"]] = token
        env_vars = [
            {"key": "MCP_ROLE", "value": role},
            {"key": spec["token_env"], "value": token},
        ]
        if spec["name"] in existing:
            svc = existing[spec["name"]]
            print(f"{spec['name']}: exists ({svc['id']}) — updating env vars")
            client.put(
                f"/services/{svc['id']}/env-vars",
                json=[{"key": v["key"], "value": v["value"]} for v in env_vars],
            )
            client.post(f"/services/{svc['id']}/deploys", json={})
        else:
            print(f"{spec['name']}: creating...")
            resp = client.post(
                "/services",
                json={
                    "type": "web_service",
                    "name": spec["name"],
                    "ownerId": owner_id,
                    "repo": REPO,
                    "branch": "main",
                    "autoDeploy": "yes",
                    "envVars": env_vars,
                    "serviceDetails": {
                        "env": "docker",
                        "plan": "free",
                        "envSpecificDetails": {"dockerfilePath": "./deploy/Dockerfile"},
                    },
                },
            )
            if resp.status_code >= 300:
                die(f"create failed {resp.status_code}: {resp.text}")
            svc = resp.json()["service"]
        urls[role] = svc["serviceDetails"].get("url") or f"https://{spec['name']}.onrender.com"

    # wait for live deploys
    for role, spec in SERVICES.items():
        svc_id = (existing.get(spec["name"]) or {}).get("id")
        if not svc_id:
            svc_id = {
                s["service"]["name"]: s["service"]["id"]
                for s in client.get("/services", params={"limit": 50}).json()
            }[spec["name"]]
        print(f"waiting for {spec['name']} deploy...", end="", flush=True)
        for _ in range(60):  # up to ~10 min
            deploys = client.get(f"/services/{svc_id}/deploys", params={"limit": 1}).json()
            status = deploys[0]["deploy"]["status"] if deploys else "unknown"
            if status == "live":
                print(" live")
                break
            if status in ("build_failed", "update_failed", "canceled"):
                die(f"{spec['name']} deploy status: {status} — check dashboard logs")
            print(".", end="", flush=True)
            time.sleep(10)
        else:
            die(f"{spec['name']} did not go live in time")

    # persist: .env tokens + config.json URLs
    env_path = ROOT / ".env"
    env_text = env_path.read_text(encoding="utf-8") if env_path.exists() else ""
    for k, v in tokens.items():
        if re.search(rf"^{k}=", env_text, re.M):
            env_text = re.sub(rf"^{k}=.*$", f"{k}={v}", env_text, flags=re.M)
        else:
            env_text += f"\n{k}={v}"
    env_path.write_text(env_text.strip() + "\n", encoding="utf-8")

    cfg_path = ROOT / "config.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    cfg["mcp"]["cop_url"] = urls["cop"].rstrip("/") + "/mcp"
    cfg["mcp"]["thief_url"] = urls["thief"].rstrip("/") + "/mcp"
    cfg_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")

    print("\nDONE:")
    print(f"  cop:   {cfg['mcp']['cop_url']}")
    print(f"  thief: {cfg['mcp']['thief_url']}")
    print("tokens written to .env; config.json updated. Next:")
    print("  uv run python scripts/cloud_verify.py")
    print("  uv run python -m src.orchestrator --no-email")


if __name__ == "__main__":
    main()
