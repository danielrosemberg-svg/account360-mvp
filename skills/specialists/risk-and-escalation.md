---
name: risk-and-escalation
description: >
  Identifies and frames active risks, escalations, and churn signals for the CSM.
  Receives the fetch_bundle from knowledge-and-data-enricher and produces a
  risk-focused brief covering severity, ARR impact, churn signals, open support
  tickets, and recommended retention actions. Suppresses all commercial or upsell
  language when churn risk is active. Never invents risk data — all output must
  trace to the fetch_bundle.
labels:
  - specialist
  - domain-expertise
  - risk
  - escalation
  - retention
  - account360
---

## Context

**Activated when:** The Brain detects `risk_severity` = High / Critical in the
fetch_bundle, or the CSM explicitly requests a risk or escalation brief, or
`meeting_type = Adoption_Risk`.

**Data input:** Receives the following fetch_bundle sections from
`knowledge-and-data-enricher`:
- `risks_and_health` (full — primary section)
- `commercial` (ARR and renewal date for impact framing)
- `interaction_log` (last touchpoints and Gong context)
- `support_tickets` (high-priority open cases)

**Output target:** Populates the **Risks & Health** section of the Snapshot / Full 360
/ Meeting Prep brief. In Meeting Prep mode, also produces a retention action plan.

---

## Instructions

### Step 1 — Risk level triage

Read `risks_and_health.risk_severity` and assign a triage level immediately.
This governs every subsequent step.

| Triage Level | Condition | Response mode |
|---|---|---|
| 🟢 **Clear** | `risk_severity` = none or null AND `Open_Churn_Requests__c` = 0 | Short reassurance block. No escalation language. |
| 🟡 **Monitor** | `risk_severity` = low or medium | Flag for awareness. Provide context and light action. |
| 🔴 **At Risk** | `risk_severity` = high OR `Open_Churn_Requests__c` > 0 | Full risk brief. Retention framing. Involve RM. |
| 🚨 **Critical** | `risk_severity` = critical OR multiple simultaneous churn signals | Escalation protocol. Immediate action items. Loop in AM + RM. |

**Churn suppression rule:** At triage level At Risk or Critical →
remove ALL upsell, expansion, and new-module language from this brief and any
downstream Compose output for this session.

---

### Step 2 — Build the Risk Profile block

| Field | API Name | Show when | If null → |
|---|---|---|---|
| Health Sentiment | `account_health_sentiment__c` | Always | "Health: not available" |
| Risk Severity | `Overall_Risk_Severity__c` | Always | Show "No active risk recorded" |
| Risk Reason | `Risk_Reason__c` | When severity ≥ medium | Omit line |
| ARR at Risk | `Overall_Risk_Impact_ARR__c` | When present | Omit line |
| Modules at Risk | `Modules_at_Risk__c` | When present | Omit line |
| Open Churn Requests | `Open_Churn_Requests__c` | When > 0 | Omit line |
| Total Customer Risks | `Total_Customer_Related_Risks__c` | When > 0 | Omit line |

**Format:**
```
### Risk Profile
Health Sentiment: {sentiment}
Risk Severity: {badge} {severity}
Risk Reason: {reason}
ARR at Risk: ${amount}
Modules at Risk: {modules}
Open Churn Requests: {count}
```

---

### Step 3 — Renewal proximity risk

Cross-reference `commercial.renewal_date_or_quarter` with the risk level.

| Condition | Flag |
|---|---|
| Risk ≥ High AND days_to_renewal < 90 | 🚨 "High-risk account with renewal in {N} days — immediate retention priority" |
| Risk = Medium AND days_to_renewal < 60 | 🟡 "At-risk account entering renewal window — accelerate recovery plan" |
| Risk ≥ High AND no renewal date | ⚠️ "Renewal date unknown — confirm with SF before scheduling renewal conversation" |

---

### Step 4 — Support escalation signals

Use support tickets from the fetch_bundle (High / Critical priority open cases).

For each ticket:
```
🎫 [{CaseNumber}] {Subject} — {Priority} priority — Status: {Status}
```

If tickets exist AND risk_severity ≥ high:
Add: "Active support escalations are compounding risk — resolve before renewal."

If no tickets: omit this block silently (do not write "no tickets found").

---

### Step 5 — Interaction log review

Pull the 2 most recent touchpoints from `interaction_log`:

- Prefer Gong call records over CRM tasks when both are available.
- Flag if the most recent touchpoint is > 30 days ago:
  "⚠️ No contact in {N} days — proactive outreach recommended."
- If key points from a Gong call mention risk-related themes (churn, escalation,
  dissatisfaction) → surface the relevant highlight as a verbatim quote if available:
  `"[Gong highlight]: {Gong__Call_Key_Points__c}"`

---

### Step 6 — Retention action plan (Meeting Prep mode only)

When `output_mode = meeting_prep`, produce a structured retention action plan.

**Triage: At Risk**
```
### Retention Action Plan
Objective: Prevent churn — demonstrate commitment and recovery path.

Suggested agenda:
1. Acknowledge the risk openly — do not minimize (5 min)
2. Understand root cause — is it product, adoption, support, or commercial? (10 min)
3. Present a joint recovery plan with clear owners and dates (10 min)
4. Confirm renewal intent / next step (5 min)

Questions to validate with customer:
- "What would need to change for you to feel confident about renewal?"
- "Is there a specific module or workflow that isn't working as expected?"
- "Who on your side should be included in the recovery plan?"

Never assume:
- Do not assume the customer wants to churn — risk severity is internal, not declared.
- Do not commit to product timelines or fixes without checking with Product/Support.
```

**Triage: Critical**
```
### Escalation Protocol
This account requires executive and cross-functional involvement before the call.

Pre-call checklist:
☐ Notify Renewal Manager ({Renewal_Manager__c}) — loop in before the call
☐ Review latest support ticket status with Support team
☐ Prepare a retention offer or gesture (with RM / AM approval)
☐ Do NOT discuss upsell, expansion, or new features in this call

Call objective: Stabilize the relationship. Nothing else.
```

---

### Step 7 — Assemble the Risk Brief

```
## Risk & Escalation Brief — {account_name}

**Triage Level:** {badge} {triage_level}

### Risk Profile
{risk_profile_block}

### Renewal Proximity
{renewal_risk_flag if applicable}

### Support Escalations
{ticket_lines if applicable}

### Last Touchpoints
{touchpoint_lines}

[### Retention Action Plan — only in meeting_prep mode]
```

---

## Resources

- `knowledge-and-data-enricher.md` — provides fetch_bundle as input
- `fetch_bundle.schema.json` — input schema reference
- `output_modes.md` — snapshot / full_360 / meeting_prep output shapes
- `Meeting_Type_Topic_Matrix.csv` — Adoption_Risk section priorities and guardrails
