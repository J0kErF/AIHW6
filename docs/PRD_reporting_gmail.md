# PRD — Reporting & Gmail Automation (Track E)

> Owns: `src/reporting/`. Spec §9: after all sub-games the **Cop agent** automatically
> sends ONE email, body = **JSON only**, to `rmisegal+uoh26b@gmail.com`.

## 1. Goal

Turn `SeriesManager.totals()` + per-sub-game records into the exact JSON contract
(`REPORTING_SPEC.md`) and deliver it autonomously via the Gmail API.

## 2. Functional requirements

1. **Report builder**: produces Internal Game JSON (and Bonus JSON for inter-group runs)
   validated against pydantic models mirroring `REPORTING_SPEC.md`. Fields include
   `group_name`, `students`, `github_repo`, `cop_mcp_url`, `thief_mcp_url`,
   `timezone: "Asia/Jerusalem"`, `sub_games[]`, `totals{}`.
2. **Validity guard**: refuses to send unless exactly **6 valid** sub-games are recorded
   (technical losses excluded and re-run upstream).
3. **Gmail sender** (`google-api-python-client`):
   - OAuth Desktop client: `credentials.json` + `token.json` from the external secrets
     folder (paths from config/env — never in repo).
   - Scope: `gmail.modify` (per course guide; also enables send/draft).
   - Auth flow identical to course guide §19: cached token, refresh, browser flow fallback.
   - Body: `json.dumps(report, indent=2)` and NOTHING else (no greeting, no signature).
   - Subject from config (e.g. `HW6 report — moamteam`).
   - Recipient from config: `report.recipient = rmisegal+uoh26b@gmail.com`.
4. **Dry-run mode**: writes the email as a Gmail **draft** (like the course demo) instead
   of sending — used until final submission; flag `report.dry_run`.
5. **Trigger**: called by the orchestrator at series end — the "cop agent sends" is
   satisfied by the cop-side pipeline invoking the sender autonomously.
6. **Bonus flow**: build Inter-Group JSON with both teams' data; require
   `mutual_agreement=true` input before sending; both totals must match the agreed record.

## 3. Acceptance criteria

- [ ] Schema round-trip test: builder output validates against frozen models; example
      payloads in spec reproduce byte-compatible structure (keys & types).
- [ ] Draft-mode e2e test creates a Gmail draft containing pure JSON (manual visual check).
- [ ] Send-mode e2e verified once to a team-owned address before pointing at the grader.
- [ ] Missing/expired token → automatic browser re-auth flow works (guide §22.3 pitfall covered).
- [ ] Sending with ≠ 6 valid sub-games is impossible (raises, logged).
