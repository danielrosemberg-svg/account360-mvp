---
name: account360-intake-classifier
description: >
  Parses a CSM Account 360 request, validates minimum identifiers, detects language,
  classifies output mode (Snapshot / Full 360 / Meeting Prep) and meeting type (four-way)
  using Sure / Not Sure judgments, and emits a JSON routing packet that gates downstream
  CRM + Research fetch and Compose steps. Entry point before specialists when building
  the ChatGPT Agent Flow for Account 360.
labels:
  - classification
  - routing
  - brain
  - intent-detection
  - language-detection
  - account360
---

## Context

Run this skill **first** in an Account 360 Agent Flow session **before** parallel CRM Specialist + Research Specialist fetch skills and before any Compose_* skill.

**Triggers**

- CSM provides an Account 360 request with at least a Salesforce Account Id (or equivalent canonical id).
- Manager-triggered prep request includes the same minimum identifiers.

**Do not treat as a fresh intake (skip duplicate classification)**

- Downstream compose or fetch already consumed a routing packet with the same session id (if your orchestration tracks sessions).
- User is only refining formatting — route to Delivery Specialist without re-classifying.

---

## Resources (load as Knowledge in ChatGPT)

- `output_modes.md` — definitions for Snapshot vs Full 360 vs Meeting Prep.
- `Meeting_Type_Topic_Matrix.csv` — meeting-type priorities and guardrails.
- `fetch_bundle.schema.json` — optional skim for field awareness when explaining gaps (do not fabricate data).

**Golden dataset:** Replace placeholders in **Golden examples** below with real anonymized snippets before production testing.

---

## Instructions

### Step 1 — Validate intake / EXIT early

EXIT with `classification_confident: false` when ANY holds:

- `salesforce_account_id` missing or clearly malformed after parse attempt.
- User asks for Meeting Prep but supplies **no** usable intent text **and** no explicit meeting type hint — cannot infer objective.

EXIT payload must still include parsed language if detectable and `potential_ambiguity` explaining the blocker.

### Step 2 — Parse user message

Extract:

- **salesforce_account_id** (required string).
- **account_name** if explicitly mentioned (optional until Salesforce MCP fills it).
- **free_text_context** — goals, timing, stakeholders, risks mentioned by the CSM.
- **explicit_output_mode** if user literally asks for snapshot / full 360 / meeting prep equivalents (map synonyms per `output_modes.md`).
- **explicit_meeting_type** if user names Renewal/EBR, Adoption/Risk, Expansion, Onboarding/Escalation (accept common synonyms).
- **meeting_date_or_horizon** if stated ("tomorrow", ISO date, "next week").

### Step 3 — Detect language

Analyze the **latest user message** primarily; fall back to free-text blocks.

- **Hebrew** when roughly ≥30% of tokens use Hebrew script.
- Otherwise **`en`**.

Output field: `language` is `"he"` or `"en"`.

### Step 4 — Optional Salesforce enrichment (defer if no MCP)

If Salesforce MCP / SOQL is available, fetch the smallest helpful Account header:

`Id, Name, Industry, AnnualRevenue or ARR fields available, Renewal_Date__c (if exists)`

Bind `account_name` when previously unknown. If MCP absent, set `"salesforce_enrichment": "skipped"` and continue without failing.

### Step 5 — Classify output_mode with Sure / Not Sure

For each mode `snapshot`, `full_360`, `meeting_prep` decide **Sure** vs **Not Sure** using holistic judgment + `output_modes.md`.

Rules:

- Explicit user wording matching a mode ⇒ **Sure** for that mode (even if others could apply).
- Without explicit wording, infer from verbs/nouns (prep vs dossier vs quick pulse).
- **At most one** mode should be **Sure** unless user clearly demands contradictory deliverables — if conflict, pick the **more specific** (usually `meeting_prep`) and set `classification_confident: false` with explanation.

Populate:

- `output_mode_sure`: record booleans per mode OR collapse to chosen `output_mode` + `output_mode_confident` boolean.

Recommended collapsed shape:

```json
"output_mode": "snapshot | full_360 | meeting_prep",
"output_mode_confident": true
```

When ambiguous and policy chooses a default per `output_modes.md`, set `output_mode_confident: false`.

### Step 6 — Classify meeting_type (Meeting Prep only)

Run **only if** `output_mode` resolves to `meeting_prep` **or** user forces meeting-type tagging for analytics.

For each logical type (map labels consistently):

| Canonical key       | Acceptable aliases |
|--------------------|--------------------|
| `Renewal_EBR`      | renewal, EBR, executive business review, procurement |
| `Adoption_Risk`    | adoption, usage drop, risk review, health check |
| `Expansion`        | expansion, upsell, cross-sell, new module |
| `Onboarding_Escalation` | onboarding, implementation, go-live, escalation, critical |

Sure / Not Sure:

- **Sure** when the user's language centers on that scenario as the primary reason for the meeting.
- **Not Sure** when hints are weak or contradictory.

If **two or more** types are Sure (multi-intent), populate `meeting_types_sure` as an array and set `multi_meeting_type: true`. Meeting Prep composition should fuse agendas — downstream Compose must receive **per-type asks** analogous to `topic_asks` in the email classifier.

If **none** are Sure:

- Set `meeting_type_confident: false`.
- **Do not** route to `Compose_Meeting_Prep_Brief` until the CSM confirms a type OR supplies richer context.
- Still allow Snapshot/Full360 fetch if those modes were requested instead.

### Step 7 — Routing decision

Translate classification into pipeline keys:

| output_mode   | Include in `routed_to` (baseline) |
|---------------|-------------------------------------|
| snapshot      | `crm_fetch`, `research_fetch`, `compose_snapshot` |
| full_360      | `crm_fetch`, `research_fetch`, `compose_full_360` |
| meeting_prep + confident type | `crm_fetch`, `research_fetch`, `compose_meeting_prep_brief`, `map_meeting_type_to_topics` |

Add `classify_meeting_type` when meeting-type inference was needed.

Parallelism hint: `crm_fetch` and `research_fetch` may run concurrently after packet emission.

### Step 8 — Emit routing packet (JSON)

Always end with a single JSON object. Examples below illustrate shape — extend with nulls as needed.

**Meeting Prep — confident**

```json
{
  "salesforce_account_id": "001XXXXXXXXXXXX",
  "account_name": "Acme Corp",
  "language": "en",
  "user_ask_one_liner": "Prep renewal conversation focusing on executive alignment.",
  "explicit_output_mode": null,
  "output_mode": "meeting_prep",
  "output_mode_confident": true,
  "meeting_types_sure": ["Renewal_EBR"],
  "multi_meeting_type": false,
  "meeting_type_asks": {
    "Renewal_EBR": "CSM needs Renewal/EBR prep with emphasis on exec narratives still open."
  },
  "meeting_type_confident": true,
  "routed_to": [
    "crm_fetch",
    "research_fetch",
    "map_meeting_type_to_topics",
    "compose_meeting_prep_brief"
  ],
  "classification_confident": true,
  "potential_ambiguity": null,
  "salesforce_enrichment": "skipped"
}
```

**Snapshot — explicit**

```json
{
  "salesforce_account_id": "001XXXXXXXXXXXX",
  "account_name": null,
  "language": "he",
  "user_ask_one_liner": "צריך תמונת מצב קצרה לפני שיחה עם ההנהלה.",
  "explicit_output_mode": "snapshot",
  "output_mode": "snapshot",
  "output_mode_confident": true,
  "meeting_types_sure": [],
  "multi_meeting_type": false,
  "meeting_type_asks": {},
  "meeting_type_confident": false,
  "routed_to": ["crm_fetch", "research_fetch", "compose_snapshot"],
  "classification_confident": true,
  "potential_ambiguity": null,
  "salesforce_enrichment": "skipped"
}
```

**EXIT — missing Account Id**

```json
{
  "salesforce_account_id": null,
  "account_name": null,
  "language": "en",
  "user_ask_one_liner": "User asked for meeting prep without supplying an account identifier.",
  "output_mode": null,
  "output_mode_confident": false,
  "meeting_types_sure": [],
  "multi_meeting_type": false,
  "meeting_type_asks": {},
  "meeting_type_confident": false,
  "routed_to": [],
  "classification_confident": false,
  "potential_ambiguity": "Cannot route without Salesforce Account Id.",
  "salesforce_enrichment": "skipped"
}
```

---

## Golden examples (placeholders — replace with anonymized real inputs)

| # | User message (abbrev) | Expected output_mode | Expected meeting_type Sure | Notes |
|---|----------------------|----------------------|----------------------------|-------|
| 1 | Account 001XXX snapshot for tomorrow | snapshot | n/a | Explicit snapshot keyword |
| 2 | Full 360 on 001XXX before QBR | full_360 | n/a | |
| 3 | Prep renewal call Friday 001XXX CFO joins | meeting_prep | Renewal_EBR | |
| 4 | Usage dropped in UK payroll — need customer call | meeting_prep | Adoption_Risk | |
| 5 | Customer wants Surveys + payroll issue same meeting | meeting_prep | multi: Adoption_Risk + Expansion | multi_meeting_type true |
| 6 | "Help" + Id only | meeting_prep or snapshot | none Sure | ambiguous → confident false |

---

## Discovery logging

When `classification_confident` is false, append a short diagnostic describing closest modes/types and why they failed Sure — analogous to the email classifier discovery pipeline.
