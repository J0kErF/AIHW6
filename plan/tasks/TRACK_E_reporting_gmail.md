# TRACK E — Reporting & Gmail Automation

> Read first: `docs/PRD_reporting_gmail.md`, `docs/REPORTING_SPEC.md` (frozen),
> `docs/ENVIRONMENT.md` §5 (Google setup). You own `src/reporting/` + the out-of-repo
> secrets setup. **No start gate** — schema is frozen; build against fixture `Totals`.

## Mission
Exact-schema JSON reports + fully automated Gmail delivery (OAuth client + token), with a
draft-mode safety net.

## Tasks
- [x] E1. **Google Cloud one-time setup** (follow ENVIRONMENT §5 / course guide):
       project `moamteam_hw6` → enable **Gmail API** + **Google Calendar API** →
       Auth Platform: External, contacts → Data access scopes `gmail.modify` + `calendar` →
       Desktop OAuth client → download `credentials.json` → secrets dir OUTSIDE repo →
       add both members as Test users.
- [x] E2. `reporting/auth.py` — course-guide credential flow (token cache, refresh, browser
       fallback); paths from env/config; helpful error for guide-§22 pitfalls.
- [x] E3. `reporting/models.py` — pydantic models for Internal + Bonus reports, mirroring
       REPORTING_SPEC byte-for-byte (keys, nesting, types).
- [x] E4. `reporting/builder.py` — `SubGameRecord[] + Totals + config identity → report`;
       **validity guard: exactly 6 valid sub-games or raise**.
- [x] E5. `reporting/gmail_sender.py` — send via `users().messages().send`; body =
       `json.dumps(report, ensure_ascii=False, indent=2)` ONLY; subject+recipient from
       config; `dry_run=true` → create **draft** instead (course-video pattern).
- [x] E6. Smoke script: `uv run python -m src.reporting.smoke` → OAuth flow → draft with
       fixture report → manual visual check in Gmail (pure JSON, nothing else).
- [~] E7. (deferred to final graded run) One real send to our own address; only then flip recipient config to
       `rmisegal+uoh26b@gmail.com` (leave `dry_run=true` until final submission run).
- [ ] E8. Bonus path: builder for Inter-Group JSON + reconcile helper (byte-diff two
       payloads; refuse send unless identical & `mutual_agreement=true`).
- [x] E9. `.gitignore` audit: `.env`, `*credentials*.json`, `*token*.json` excluded; add
       `docs/` note where secrets live.

## Definition of Done
Draft e2e verified visually; schema tests green; guard tested; orchestrator can call
`send_report(totals)` with zero interaction (token cached); secrets never in git status.
