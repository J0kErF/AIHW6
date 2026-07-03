# REPORTING_SPEC — Frozen JSON Contracts (spec §9)

> These schemas are copied from the assignment PDF and are **frozen**. The email body
> contains **only** the JSON — no free text, no signature — to allow automatic ingestion.
> Recipient: `rmisegal+uoh26b@gmail.com`. One email per team per game.

## 1. Internal Game Report (our own cop vs our own thief)

```json
{
  "group_name": "moamteam",
  "students": ["Mohammad Yosef", "Amear Abu Farekh"],
  "github_repo": "https://github.com/J0kErF/AIHW6",
  "cop_mcp_url": "https://<cop-public-url>",
  "thief_mcp_url": "https://<thief-public-url>",
  "timezone": "Asia/Jerusalem",
  "sub_games": [],
  "totals": {
    "cop": 0,
    "thief": 0
  }
}
```

### `sub_games[]` entry (our internal convention — engine `SubGameRecord` maps 1:1)

```json
{
  "index": 1,
  "winner": "cop | thief",
  "reason": "capture | move_limit",
  "moves_played": 17,
  "barriers_used": 3,
  "cop_points": 20,
  "thief_points": 5,
  "started_at": "2026-07-02T14:00:00+03:00",
  "ended_at": "2026-07-02T14:03:41+03:00"
}
```

Rules:
- Exactly **6 valid** entries. Technical losses (`Technical Loss`) are void — re-run until
  6 valid sub-games exist; voided runs never appear in `sub_games[]`.
- `totals` = sums of the per-sub-game points (max cop 20×6? No — internal game the same
  pair plays all 6; totals are simple sums of the table in `GAME_RULES.md` §6).

## 2. Inter-Group Bonus Report (cloud competition)

```json
{
  "report_type": "bonus_game",
  "groups": {
    "group_1": "moamteam",
    "group_2": "<other team>"
  },
  "github_repo_group_1": "https://github.com/<us>/<repo>",
  "github_repo_group_2": "https://github.com/<them>/<repo>",
  "mcp_url_group_1_cop": "https://<our-cop-url>",
  "mcp_url_group_1_thief": "https://<our-thief-url>",
  "mcp_url_group_2_cop": "https://<their-cop-url>",
  "mcp_url_group_2_thief": "https://<their-thief-url>",
  "timezone": "Asia/Jerusalem",
  "students_group_1": [],
  "students_group_2": [],
  "sub_games": [],
  "totals_by_group": {
    "moamteam": 0,
    "<other team>": 0
  },
  "bonus_claim": {
    "moamteam": 0,
    "<other team>": 0
  },
  "mutual_agreement": true
}
```

Rules (spec §12):
- Sub-games 1–3: group_1 cop vs group_2 thief; sub-games 4–6: group_2 cop vs group_1 thief.
- **Both groups email separately with EXACTLY the same results** (full mutual agreement).
  Mismatch or disagreement ⇒ bonus voided, 0 for both, for that series.
- `bonus_claim`: winner 10, loser 7, absolute tie 5/5. Final bonus grade = average over
  all valid series played (multiple opponents allowed and encouraged).
- Deadline: within **one week** of assignment publication.

## 3. Email mechanics

- Sender: team Gmail via Gmail API (OAuth Desktop client; scope `gmail.modify`).
- Trigger: cop-side pipeline, automatically, at series completion (N-01 autonomy).
- Subject: `HW6 report — moamteam` (internal) / `HW6 bonus — moamteam vs <other>` (bonus).
- Body: `json.dumps(report, ensure_ascii=False, indent=2)` — nothing else.
