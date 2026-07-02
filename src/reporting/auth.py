"""Google OAuth credential flow — identical to the course guide (§19).

credentials.json / token.json live OUTSIDE the repo; paths come from env vars
named in config (report.credentials_path_env / report.token_path_env).
Delete token.json to force a fresh browser consent (guide §22.3).
"""
from __future__ import annotations

import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from src.common.config import Config


class GoogleAuthError(Exception):
    pass


def _path_from_env(env_name: str, what: str) -> Path:
    value = os.environ.get(env_name)
    if not value:
        raise GoogleAuthError(
            f"env var {env_name} not set — it must point to your {what} "
            "(see docs/ENVIRONMENT.md §4-5; files live outside the repo)"
        )
    return Path(value)


def get_credentials(config: Config) -> Credentials:
    scopes = config.report.gmail_scopes
    creds_file = _path_from_env(config.report.credentials_path_env, "credentials.json")
    token_file = _path_from_env(config.report.token_path_env, "token.json")

    creds: Credentials | None = None
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not creds_file.exists():
                raise GoogleAuthError(
                    f"{creds_file} missing — download the OAuth Desktop client JSON "
                    "from Google Auth Platform (docs/ENVIRONMENT.md §5, step 5)"
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_file), scopes)
            creds = flow.run_local_server(port=0)
        token_file.write_text(creds.to_json(), encoding="utf-8")
    return creds
