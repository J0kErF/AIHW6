"""Autonomous Gmail delivery of the JSON report (Track E).

dry_run=true (config) -> Gmail DRAFT (course-video pattern, safe rehearsal).
dry_run=false          -> real send to config.report.recipient.
Body is the pure JSON document — no greeting, no signature (spec §9).
"""
from __future__ import annotations

import base64
from email.message import EmailMessage

from googleapiclient.discovery import build

from src.common.config import Config
from src.reporting.auth import get_credentials
from src.reporting.builder import report_body
from src.reporting.models import InternalReport


def _raw_message(body: str, recipient: str, subject: str) -> dict:
    msg = EmailMessage()
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)
    return {"raw": base64.urlsafe_b64encode(msg.as_bytes()).decode()}


def send_report(report: InternalReport, config: Config) -> dict:
    """Returns {"mode": "draft"|"sent", "id": ...}. Called by the cop-side pipeline."""
    body = report_body(report)
    creds = get_credentials(config)
    service = build("gmail", "v1", credentials=creds)
    raw = _raw_message(body, config.report.recipient, config.report.subject)
    if config.report.dry_run:
        draft = (
            service.users().drafts().create(userId="me", body={"message": raw}).execute()
        )
        return {"mode": "draft", "id": draft["id"]}
    sent = service.users().messages().send(userId="me", body=raw).execute()
    return {"mode": "sent", "id": sent["id"]}
