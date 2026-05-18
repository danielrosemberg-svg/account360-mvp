---
name: onboarding-and-kickoff
description: >
  Supports CSMs managing new customers in the onboarding and implementation phase.
  Receives customer_business, commercial, and interaction_log sections and produces
  a kickoff-ready brief covering go-live status, stakeholder mapping, contract
  context, first-module adoption readiness, and early risk detection. Focused on
  relationship setup and successful activation — not on renewal or expansion.
labels:
  - specialist
  - domain-expertise
  - onboarding
  - kickoff
  - implementation
  - account360
---

## Context

**Activated when:** The Brain routes `meeting_type = Onboarding_Escalation`, or the
CSM requests a kickoff brief, go-live prep, or implementation status check.

**Data input:** Receives the following fetch_bundle sections from
`knowledge-and-data-enricher`:
- `customer_business` (full)
- `commercial` (contract dates, segment, quoted employees, live flag)
- `interaction_log` (kickoff call history and open tasks)

**Output target:** Populates the **Customer Business** and **Commercial** sections
for onboarding context, plus a structured kickoff agenda in Meeting Prep mode.

---

## Instructions

### Step 1 — Go-live status gate

Check `Customer_Is_Live__c` first.

| Status | Action |
|---|---|
| `Customer_Is_Live__c` = true | Account is live — this specialist shifts to "early adoption review" mode |
| `Customer_Is_Live__c` = false | Full onboarding / pre-live mode |
| `Customer_Is_Live__c` = null | Flag as warning: "Live status unknown — verify in Salesforce before the call" |

**Tenure check:** Calculate days since `First_Contract_Start_Date__c`.

| Days since contract start | Flag |
|---|---|
| < 30 days | "New customer — kickoff should focus on relationship and expectations" |
| 30–90 days | "Early implementation phase — check go-live milestones" |
| 90–180 days | "Implementation should be progressing — verify activation status" |
| > 180 days AND not live | 🔴 "Customer has been in onboarding for {N} months without going live — escalation risk" |

---

### Step 2 — Contract & account context block

Use `commercial` and `customer_business` sections.

**Required fields:**

| Field | API Name | If null → |
|---|---|---|
| Account Name | `Name` | Required — do not proceed without it |
| Industry | `Industry` | Omit line |
| Country | `BillingCountry` | Omit line |
| Segment / Tier | `Account_Tier_Micro__c` | Omit line |
| Quoted Employees | `Max_Quoted_Number_EE__c` | "Size: not available" |
| Contract Start | `First_Contract_Start_Date__c` | Flag as warning |
| Renewal Date | `Master_Contract_End_Date__c` | Show if < 12 months away; else omit |
| Account Owner | `Owner.Name` | Show "Owner: not mapped" |

**Format:**
```
### Account Context
{account_name} · {industry} · {country}
Segment: {tier} · {quoted_employees} employees (quoted)
Contract started: {start_date} ({days_since} days ago)
Live on Bob: {Yes / No / Unknown}
Owner: {owner}
```

---

### Step 3 — Stakeholder awareness

Use `interaction_log` to infer stakeholder picture from call and task history.

- Look for names mentioned in Gong participants (`gong_related_participants_json_c`)
  or task subjects.
- If stakeholder data is available, list known contacts:
  ```
  Known stakeholders:
  - {name} — {role} — last seen: {date}
  ```
- If no stakeholder data: "No stakeholder contact history found — confirm decision-maker
  and project champion at kickoff."

**Champion identification hint:**
"Identify the internal project champion (the person who will own adoption internally).
Without a champion, onboarding stalls."

---

### Step 4 — Modules to activate

Use `Paying_Modules_Text__c` to list the modules the account has paid for.

- If not live: present as "Modules to activate in onboarding"
- If live but low/no usage: present as "Modules requiring activation follow-up"

For each module, assign an onboarding priority:

| Priority | Module | Rationale |
|---|---|---|
| 1 — Core | Core HR, Tasks, Time-Off | Foundation — must be live before anything else |
| 2 — Value | Survey, Performance, eSign | Value drivers — activate once core is stable |
| 3 — Advanced | Analytics, Triggered Flows, Payroll, Workforce Planning | Complex setup — phase in after value modules |

Output as a prioritized checklist:
```
### Activation Roadmap
Phase 1 (Core):  ☐ Core HR  ☐ Tasks  ☐ Time-Off
Phase 2 (Value): ☐ Survey  ☐ Performance Reviews
Phase 3 (Advanced): ☐ Analytics  ☐ Triggered Flows
```

---

### Step 5 — Early risk signals

Flag any conditions that could indicate an onboarding at risk.

| Signal | Source | Flag |
|---|---|---|
| Not live after 180+ days | Calculated | 🔴 "Implementation overdue — escalation risk" |
| No task or interaction in 30+ days | `interaction_log` | 🟡 "No recent engagement — proactive outreach needed" |
| High-priority open support ticket | `support_tickets` | 🟡 "Active support issue may be blocking go-live" |
| No identified stakeholder | `interaction_log` | 🟡 "No project champion identified" |
| Quoted employees > 200 with no Gong call | `interaction_log` + `growth_and_value` | 🟡 "Large account with no recorded kickoff call — verify onboarding status" |

---

### Step 6 — Assemble the Onboarding Brief

```
## Onboarding & Kickoff Brief — {account_name}

**Go-Live Status:** {Live / Not Yet Live / Unknown}
**Days Since Contract Start:** {N} days

### Account Context
{account_context_block}

### Stakeholder Picture
{stakeholder_block}

### Activation Roadmap
{module_checklist}

### Early Risk Signals
{risk_flags_if_any}

### Last Touchpoints
{touchpoint_lines}
```

**For Meeting Prep (meeting_type = Onboarding_Escalation):**
Append:
```
### Kickoff Agenda (45 min)
1. Introductions & relationship building (5 min)
2. Customer's goals and success definition (10 min)
3. Onboarding plan walkthrough — phases and milestones (10 min)
4. Identify internal champion and implementation team (5 min)
5. Module activation roadmap — start with Phase 1 (10 min)
6. Next steps, owners, and timeline (5 min)

### Questions to Validate
- "What does a successful go-live look like for your team in the first 90 days?"
- "Who on your side will own the day-to-day implementation?"
- "Are there any internal dependencies or blockers we should know about?"
- "Which departments should we prioritize for rollout first?"

### Never Assume
- Do not assume the customer has read the onboarding documentation.
- Do not mention renewal or expansion in a kickoff or early onboarding call.
- Do not commit to specific go-live dates without confirming with the customer's team.
```

---

## Resources

- `knowledge-and-data-enricher.md` — provides fetch_bundle as input
- `fetch_bundle.schema.json` — input schema reference
- `output_modes.md` — meeting_prep output shape
- `Meeting_Type_Topic_Matrix.csv` — Onboarding_Escalation section priorities and guardrails
