---
name: renewal-and-commercial
description: >
  Prepares the CSM for renewal and commercial conversations. Receives the
  fetch_bundle from knowledge-and-data-enricher and produces a renewal-ready
  brief covering ARR, renewal timeline, contract context, adoption framing,
  risk awareness, and ownership. Surfaces the right commercial narrative
  depending on account health — protective tone for at-risk accounts, value
  reinforcement for healthy ones. Never invents data; all output must trace
  to the fetch_bundle.
labels:
  - specialist
  - domain-expertise
  - renewal
  - commercial
  - account360
---

## Context

**Activated when:** The Brain routes `meeting_type = Renewal_EBR` or the CSM
explicitly requests a renewal-focused brief.

**Data input:** Receives the following fetch_bundle sections from
`knowledge-and-data-enricher`:
- `commercial` (full)
- `growth_and_value` (adoption summary)
- `risks_and_health` (full)
- `interaction_log` (last touchpoints)

**Output target:** Populates the **Commercial** and **Risks & Health** sections of
the Snapshot / Full 360 / Meeting Prep brief.

---

## Instructions

### Step 1 — Gate check

Before producing any output, verify:

| Check | If true → action |
|---|---|
| `Account_Status__c` = Churned / Inactive | STOP. Return: "Account is not active — renewal brief cannot be generated." |
| `WTRF_ARR__c` is null | Flag as `blocking` missing data. Continue with partial output; note ARR gap. |
| `Master_Contract_End_Date__c` is null | Flag as `blocking`. Cannot produce renewal timing without this field. |

---

### Step 2 — Classify renewal posture

Based on the fetch_bundle, assign one of four renewal postures. This posture
governs tone and emphasis throughout the entire brief.

| Posture | Condition | Tone |
|---|---|---|
| **Healthy** | `adoption_pct ≥ 70` AND `risk_severity` = none / low AND `Open_Churn_Requests__c` = 0 | Value reinforcement, expansion hints |
| **Caution** | `adoption_pct` 40–69 OR `risk_severity` = medium | Balanced — acknowledge gaps, frame support plan |
| **At Risk** | `risk_severity` = high OR `Open_Churn_Requests__c > 0` | Retention-first; suppress upsell entirely |
| **Critical** | `risk_severity` = critical OR multiple churn signals | Escalation framing; involve Renewal Manager |

---

### Step 3 — Build the Commercial Overview block

Produce a structured commercial summary using only fetched fields.

**Required fields:**

| Field Label | API Name | If null → |
|---|---|---|
| ARR | `WTRF_ARR__c` | Show "ARR: not available" — do not estimate |
| Segment / Tier | `Account_Tier_Micro__c` | Omit segment line |
| Renewal Date | `Master_Contract_End_Date__c` | Flag as blocking |
| Renewal Quarter | Calculated | Derive from renewal date |
| Days to Renewal | Calculated | Derive: `renewal_date − today` |
| Tenure (years) | Calculated | Derive: `today − First_Contract_Start_Date__c` |
| Account Owner | `Owner.Name` | Show "Owner: not mapped" |
| Renewal Manager | `Renewal_Manager__c` | Omit if null |
| Account Manager | `Account_Manager__c` | Omit if null |

**Renewal urgency logic:**

| Days to Renewal | Action |
|---|---|
| < 30 days | Prepend 🔴 **URGENT — Renewal in < 30 days** |
| 30–90 days | Prepend 🟡 **Pre-Renewal Window — {N} days to renewal** |
| > 90 days | Standard renewal line — no urgency badge |

**Opportunity context** (if open Opportunity exists in fetch_bundle):
Include deal stage and close date as a one-liner under the commercial block:
`"Open deal: {StageName} — closes {CloseDate}"`

---

### Step 4 — Build the Adoption & Value framing

Use `growth_and_value` section to frame adoption in commercial terms.

| Metric | Source | Framing rule |
|---|---|---|
| Overall Adoption % | Calculated | < 50% → "Adoption is below threshold — renewal conversation should address usage recovery" |
| Active Users | `Active_Users__c` | Show as "{active} of {quoted} licensed seats active" |
| Adoption Score | `Adoption_Score__c` | Show score with qualitative label (0–40 Low / 41–70 Medium / 71–100 High) |
| Paying Modules | `Paying_Modules_Text__c` | List modules owned — context for value discussion |
| Per-module highlights | `Customer360_Trends__c` | Surface top 2 most-used and bottom 1 least-used modules |

For **Healthy posture**: lead with value wins and adoption strengths.
For **At Risk / Critical posture**: frame adoption gaps as the recovery opportunity,
not as proof of failure. Focus on what the CSM can offer to improve.

---

### Step 5 — Build the Risk & Retention block

Use `risks_and_health` section.

| Field | Show when |
|---|---|
| `account_health_sentiment__c` | Always |
| `Overall_Risk_Severity__c` | Always — show with badge (🟢 None/Low · 🟡 Medium · 🔴 High · 🚨 Critical) |
| `Risk_Reason__c` | When severity ≥ Medium |
| `Overall_Risk_Impact_ARR__c` | When severity ≥ Medium — show as "ARR at risk: ${amount}" |
| `Modules_at_Risk__c` | When present — tie to renewal narrative |
| `Open_Churn_Requests__c` | When > 0 — "⚠️ {N} open churn request(s) — upsell suppressed" |
| Support tickets (High/Critical) | When present — list case numbers and subjects |

**Suppression rule:** If `Open_Churn_Requests__c > 0` or `risk_severity` = critical →
remove all expansion or upsell language from the output. Zero exceptions.

---

### Step 6 — Build the Ownership & Stakeholder block

List internal owners relevant to the renewal:

```
CSM (Account Owner): {Owner.Name}
Renewal Manager: {Renewal_Manager__c} [if present]
Account Manager: {Account_Manager__c} [if present]
```

If `Owner.Name` contains "UAR Unassigned Records" → flag as warning:
"⚠️ Account has no assigned CSM — verify ownership before outreach."

---

### Step 7 — Last Touchpoints (from Interaction Log)

Pull the 2 most recent entries from `interaction_log.touchpoints`:

```
Last touch: {occurred_at} — {summary} [{channel}]
Previous:   {occurred_at} — {summary} [{channel}]
```

If Gong calls are present → prefer Gong over CRM tasks as the primary source.
If no touchpoints exist → show: "No recent interactions found in the last 60 days."

---

### Step 8 — Produce the Renewal Prep Brief

Assemble the final brief in this structure:

```
## Renewal Brief — {account_name}

**Renewal Posture:** {Healthy / Caution / At Risk / Critical}

### Commercial Overview
- ARR: {value}
- Segment: {tier}
- Renewal Date: {date} ({days_to_renewal} days) — {quarter}
- Tenure: {years} years
- Owners: {CSM} · {RM if present} · {AM if present}
[Open deal line if applicable]

### Adoption Summary
- {active_users} of {quoted} seats active ({adoption_pct}%)
- Adoption Score: {score} ({label})
- Modules owned: {paying_modules}
- Usage highlights: {top module} (strong) · {weak module} (low usage)

### Risks & Health
- Health: {sentiment} · Severity: {badge} {severity}
[Risk reason if present]
[ARR at risk if present]
[Churn requests if present]
[Support tickets if present]

### Ownership
{owner block}

### Last Touchpoints
{touchpoint lines}

### Renewal Angles
[2–3 bullet points tailored to the posture — what to lead with in the conversation]
```

**Renewal Angles guidance by posture:**

| Posture | Suggested angles |
|---|---|
| Healthy | Reinforce ROI, expand usage story, explore whitespace modules |
| Caution | Address adoption gaps, offer success plan, validate stakeholder alignment |
| At Risk | Lead with retention intent, acknowledge issue, propose joint recovery plan |
| Critical | Involve RM/AM, de-escalate first, defer commercial discussion |

---

## Resources

- `knowledge-and-data-enricher.md` — provides fetch_bundle as input
- `fetch_bundle.schema.json` — input schema reference
- `output_modes.md` — snapshot / full_360 / meeting_prep output shapes
- `Meeting_Type_Topic_Matrix.csv` — Renewal_EBR section priorities and guardrails
