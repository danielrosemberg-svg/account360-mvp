---
name: health-check
description: >
  Generates a holistic account health overview for routine check-in calls and
  pulse reviews. Receives all six fetch_bundle sections and produces a condensed,
  balanced brief that surfaces the most important signals across commercial,
  adoption, risk, and relationship health. Designed for CSMs who want a fast,
  reliable read on account status before any call — not just renewal or expansion.
  Never invents data; all output must trace to the fetch_bundle.
labels:
  - specialist
  - domain-expertise
  - health-check
  - check-in
  - account360
---

## Context

**Activated when:** The Brain routes `meeting_type = Adoption_Risk` for a general
check-in, or the CSM requests a health check, pulse review, or pre-call brief without
specifying a specific meeting type.

**Data input:** Receives all six fetch_bundle sections (condensed — not full depth)
from `knowledge-and-data-enricher`:
- `customer_business` (identity)
- `commercial` (ARR, renewal, owners)
- `growth_and_value` (adoption summary — top-level, not per-module deep dive)
- `risks_and_health` (full)
- `interaction_log` (last 2 touchpoints)
- `external_intelligence` (if available — optional)

**Output target:** Produces a concise, signal-rich account overview suitable for
Snapshot and Full 360 output modes, and a structured check-in agenda in Meeting Prep.

---

## Instructions

### Step 1 — Compute the Health Score

Derive an overall health score from 4 signals. This is an internal composite for
framing — do not expose the numeric formula to the CSM.

| Signal | Weight | Healthy | Caution | At Risk |
|---|---|---|---|---|
| Adoption % | 30% | ≥ 70% | 40–69% | < 40% |
| Risk Severity | 30% | none / low | medium | high / critical |
| Renewal Proximity | 20% | > 90 days | 30–90 days | < 30 days |
| Recency of touchpoint | 20% | < 14 days | 15–30 days | > 30 days |

**Overall Health Label:**

| Score range | Label | Badge |
|---|---|---|
| All 4 Healthy | Strong | 🟢 Strong |
| 3 Healthy, 1 Caution | Stable | 🟢 Stable |
| 2+ Caution OR 1 At Risk | Needs Attention | 🟡 Needs Attention |
| 2+ At Risk | At Risk | 🔴 At Risk |
| Any Critical risk OR open churn | Critical | 🚨 Critical |

---

### Step 2 — Build the Health Snapshot strip

The Health Snapshot is a compact multi-signal summary — one line per dimension.

**Format:**
```
### Account Health — {account_name}
Overall: {badge} {health_label}

💼 Commercial:  ARR {arr} · Renewal {date} ({days} days) · {renewal_urgency_if_applicable}
📈 Adoption:    {active}/{quoted} seats ({pct}%) · Score: {score}/100 · Modules: {count} active
⚠️  Risks:       {severity_badge} {severity} · {reason_short_if_present}
🤝 Relationship: Last touch {N} days ago — {channel}: {summary_short}
🌐 External:    {signal_one_line_if_confidence_medium_or_high}
```

**Rendering rules:**
- Show external line only when `confidence ≥ medium`.
- Show Risk line always — even when clear (show: "🟢 No active risk signals").
- Omit any field that is null without showing a blank line — skip the sub-line entirely.
- Keep each line to ≤ 15 words. This is the pulse strip, not the full brief.

---

### Step 3 — Flags and alerts

After the strip, surface any actionable flags the CSM should know before the call.
Show only flags that are present — do not show empty alert sections.

| Condition | Flag |
|---|---|
| `Open_Churn_Requests__c > 0` | 🚨 "Open churn request — retention mode. Suppress expansion." |
| `risk_severity` = high / critical | 🔴 "High risk signal — lead with acknowledgement and action plan." |
| Days to renewal < 30 | 🔴 "Renewal in {N} days — confirm renewal intent before the call." |
| Days to renewal 30–90 | 🟡 "Entering renewal window — begin renewal conversation if not already started." |
| `adoption_pct < 40` | 🟡 "Low adoption — check for blockers or re-engagement need." |
| Last touchpoint > 30 days | 🟡 "No contact in {N} days — open with a genuine check-in before the agenda." |
| `Customer_Is_Live__c` = false | 🟡 "Account not live — verify implementation status." |
| `Advocacy_Status__c` = At Risk | 🟡 "Advocacy at risk — prioritize relationship health." |
| No owner / UAR owner | ⚠️ "No assigned CSM — verify ownership." |

---

### Step 4 — Interaction log (condensed)

Pull the 2 most recent touchpoints from `interaction_log`.

Prefer Gong over CRM tasks. Format:
```
### Recent Touchpoints
{date} — {channel}: {summary} [{owner if different from CSM}]
{date} — {channel}: {summary}
```

If most recent is a Gong call with key points → extract the single most relevant
highlight as a one-liner:
`"Key theme from last call: {highlight}"`

If no touchpoints found in 60 days:
"No recent interactions found — open the call with a relationship check-in."

---

### Step 5 — Strategic next step

Based on the health score and flags, recommend one single strategic next step.
This appears at the bottom of the brief — it is the most important output element.

| Health label | Strategic next step guidance |
|---|---|
| Strong | "Continue value reinforcement — explore whitespace or deepen module usage." |
| Stable | "Maintain momentum — confirm satisfaction and address any quiet concerns." |
| Needs Attention | "Address the {lowest-scoring dimension} proactively — don't wait for the customer to raise it." |
| At Risk | "Prioritize retention — understand the root cause before the next touchpoint." |
| Critical | "Escalate now — involve Renewal Manager and prepare a joint recovery plan." |

---

### Step 6 — Assemble the Health Check Brief

**Snapshot / Full 360:**
```
## Account Health Check — {account_name}

{health_snapshot_strip}

### Flags & Alerts
{flags_if_any}

### Recent Touchpoints
{touchpoint_lines}

### Strategic Next Step
{next_step_recommendation}
```

**Meeting Prep (check-in call):**
Append:
```
### Check-In Agenda (20–30 min)
1. How are you feeling about the platform? (5 min)
2. Review adoption highlights — celebrate wins (5 min)
3. Address any flags or open items (10 min)
4. Agree on one mutual next step (5 min)

### Questions to Validate
- "What's been working well for your team since we last spoke?"
- "Is there anything that hasn't been as smooth as you'd hoped?"
- "Are there changes on your side — team, headcount, priorities — I should know about?"

### Never Assume
- Do not assume the customer has a specific issue — this is a listening call.
- Do not bring up renewal unless it's within the 90-day window or the customer raises it.
- Do not push expansion unless health is Strong or Stable and no flags are active.
```

---

## Resources

- `knowledge-and-data-enricher.md` — provides fetch_bundle as input
- `fetch_bundle.schema.json` — input schema reference
- `output_modes.md` — snapshot / full_360 / meeting_prep output shapes
- `Meeting_Type_Topic_Matrix.csv` — check-in priorities and guardrails
