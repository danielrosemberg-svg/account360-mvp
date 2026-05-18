# Post-Meeting flow — design (implement after real Gong / notes samples)

This document specifies skills **after** the customer conversation so they can be wired in Agent Flow once transcript/summary inputs exist. It pairs with steps 5–6 of the end-to-end Meeting Prep vision (summary/score + adoption & impact tracking).

## Skills

### Ingest_Meeting_Notes_Or_Gong

**Input:**

- `salesforce_account_id` (required)
- `meeting_occurred_at` (ISO date-time, optional)
- `raw_text` (required) — paste from Gong summary, manual notes, or email recap

**Output:**

- `structured_recap`: bullets for decisions, objections, owners, dates mentioned
- `entities`: detected people/companies/modules only when explicitly in text (no CRM merge at this stage unless you add a merge skill)

**Rules:** No hallucinated commitments; flag uncertain extractions as `low_confidence`.

---

### Score_Objectives

**Input:**

- `prep_brief_snapshot` (optional) — the Compose_Meeting_Prep_Brief output used going into the meeting, if available
- `structured_recap` from Ingest

**Output (JSON-friendly):**

```json
{
  "objective_achieved": "yes | partial | no | unknown",
  "prep_context_used_evidence": ["bullet tied to prep vs recap"],
  "risks_identified_in_meeting": [],
  "opportunities_identified_in_meeting": [],
  "follow_up_commitments": [{ "owner": "", "due": "", "text": "" }]
}
```

**Scoring rubric (default):**

- **objective_achieved:** `unknown` if recap lacks outcomes; otherwise compare recap to prep **Desired outcome** when prep exists.
- **prep_context_used_evidence:** quote or paraphrase parallel phrases between prep and recap; empty array if prep missing.

---

### Emit_Outcome_Record

**Input:** Output from Score_Objectives + session metadata (`meeting_type`, `csm_user_id` if available)

**Output:** One CSV-ready row (headers are configurable); suggested columns:

| Column | Description |
|--------|-------------|
| account_id | Salesforce Account Id |
| meeting_date | From ingest |
| meeting_type | Classified type |
| objective_achieved | From score |
| prep_used | yes/no/partial heuristic |
| risks_new | semicolon-separated |
| opportunities_new | semicolon-separated |
| outcome_quality | optional 1–5 once rubric defined |

If no spreadsheet connector: emit Markdown **copy-paste row** plus pipe-separated line for spreadsheets.

---

### Append_Metrics_Row

Thin wrapper: validates column set, appends row template for BI or manual paste.

---

## Recommended Agent Flow wiring

1. User selects **Post-meeting** intent → run Ingest → Score → Emit (copy row).
2. Optionally push **Emit_Outcome_Record** into the same workbook used for adoption metrics (manual phase).

## Dependencies

- Representative Gong/manual samples to tune Ingest and objective scoring prompts.
- Agreed column schema for analytics (organization-specific).
