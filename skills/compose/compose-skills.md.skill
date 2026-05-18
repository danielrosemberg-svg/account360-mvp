# Compose skills — Snapshot, Full 360, Meeting Prep

All compose skills take the **same** input object: a valid `fetch_bundle` (see `fetch_bundle.schema.json`) plus **output_mode** and optional **meeting_type** (required when mode is `meeting_prep`).

## Shared input envelope

```json
{
  "fetch_bundle": { },
  "output_mode": "snapshot | full_360 | meeting_prep",
  "meeting_type": "Renewal_EBR | Adoption_Risk | Expansion | Onboarding_Escalation | null",
  "user_locale": "he | en | …"
}
```

## Shared rules (all modes)

- Use only facts present in `fetch_bundle`. If a field is missing, state **“Not in data”** for that sub-point and add it to a **Gaps to confirm** list; do not invent ARR, dates, or risk.
- Apply policy: external intelligence is public-context only; do not assert login-gated or unverifiable claims as facts.
- If `missing_data` contains `severity: blocking` for a section critical to the user request, open with a one-line **Data gap** callout.
- Keep tone executive-safe; no blame language.

---

## Skill: Compose_Snapshot

**Goal:** CSM grasps the account in ~10 seconds (per Snapshot System functionality mapping).

**Output structure (headings, in order):**

1. **At a glance** — `account_name` (from bundle or account), industry, country/regions, one-line how they operate through Bob.
2. **Commercial** — ARR (or “Not in data”), renewal timing, segment, owner; one-line posture (expansion / neutral / renewal-risk). If `renewal_attention` is true, sub-line **Renewal focus**.
3. **Pulse** — adoption signal + one-line growth/value or value-risk from data.
4. **Risk strip** — severity, short reason, ARR impact if known, latest mitigation.
5. **External** — 2–5 lines max from `external_intelligence`; optional one-line recent signal.
6. **Last touch** — most recent touchpoint only (date + 1-line summary + owner if known); if none, **No recent interaction in data**.

**Length guardrails:** tight bullets; no agenda; no meeting prep.

---

## Skill: Compose_Full_360

**Goal:** Full picture for deep work; uses all six sections with depth.

**Output structure:**

1. **Customer Business** — all baseline fields; strategic developments.
2. **Commercial** — contract window, tiers/PEPM notes, billing groups per module if present; renewal narrative.
3. **Growth & Value** — modules, adoption trend, upsell hooks, events timeline notes if present.
4. **Risks & Health** — severity ladder, competitor stage, support tickets summary if present.
5. **Interaction Log** — chronological touchpoints (recent first), stakeholder visibility, challenges/module focus, collaboration & next steps from data.
6. **External Intelligence** — snapshot + signals + confidence; separate **AI synthesis** subsection if `ai_search_synthesis` populated.

**Add:** **Sources & gaps** — bullet list of which sections drew from populated vs missing fields (traceability for demos).

---

## Skill: Compose_Meeting_Prep_Brief

**Goal:** Maximum meeting readiness; requires `meeting_type` and cross-reference `Meeting_Type_Topic_Matrix.csv` for section priority and guardrails.

**Prerequisite:** Run **Classify_Meeting_Type** (or user-provided type). Map labels to matrix rows:
`Renewal/EBR` → `Renewal_EBR`; `Adoption/Risk` → `Adoption_Risk`; `Expansion` → `Expansion`; `Onboarding/Escalation` → `Onboarding_Escalation`.

**Output structure:**

1. **Meeting objective** — one sentence tied to `meeting_type` and facts from bundle (no new goals).
2. **Desired outcome** — measurable/falsifiable for this conversation (still grounded in data).
3. **Suggested agenda (timed)** — 4–6 bullets, ordered using matrix **Section_Priority_Order** (translate sections into talking points, not raw dumps).
4. **Questions to validate with the customer** — pull from matrix **Key_Questions_To_Validate_With_Customer**; adapt wording to account facts.
5. **Risks & opportunities** — only if supported by `risks_and_health`, `growth_and_value`, `commercial`, or `external_intelligence`.
6. **Next best actions (1–3)** — each with owner hint from data (CSM / SA / customer), and trigger condition.
7. **Prep context used** — short bullets: which bundle sections informed items above (auditable).
8. **Never assume** — restate matrix **Never_Assume_Or_Guess** as a checklist specific to this account (paraphrase, don’t quote CSV).

**Length guardrails:** scannable; avoid full duplicate of Full 360 — link deeper facts as short bullets only.

---

## Routing from Delivery Specialist

- **Snapshot** → `Compose_Snapshot`
- **Full 360** → `Compose_Full_360`
- **Meeting Prep** → `Compose_Meeting_Prep_Brief` after classification + matrix lookup
