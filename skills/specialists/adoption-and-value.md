---
name: adoption-and-value
description: >
  Analyzes module-level adoption depth and surfaces value realization gaps or wins.
  Receives the growth_and_value and commercial sections of the fetch_bundle and
  produces an adoption-focused brief with per-module breakdown, usage trends,
  at-risk signals, and coaching angles for the CSM. Never invents usage data —
  all output must trace to the fetch_bundle.
labels:
  - specialist
  - domain-expertise
  - adoption
  - value
  - account360
---

## Context

**Activated when:** The Brain routes `meeting_type = Adoption_Risk`, or the CSM
requests an adoption review, usage analysis, or value framing conversation.

**Data input:** Receives the following fetch_bundle sections from
`knowledge-and-data-enricher`:
- `growth_and_value` (primary — full)
- `commercial` (`paying_modules`, `quoted_employees`, `arr`, `segment`)
- `customer_business` (industry and size context)

**Output target:** Populates the **Growth & Value** section of the Snapshot / Full 360
/ Meeting Prep brief.

---

## Instructions

### Step 1 — Adoption health classification

Calculate and classify adoption health based on available data.

```
adoption_pct = round(Active_Users__c / Max_Quoted_Number_EE__c × 100, 1)
```

| Classification | Condition | Framing |
|---|---|---|
| 🟢 **Healthy** | `adoption_pct ≥ 70` AND `Adoption_Score__c ≥ 60` | Value reinforcement — celebrate wins, explore depth |
| 🟡 **Growing** | `adoption_pct` 50–69 OR `Adoption_Score__c` 40–59 | Momentum framing — what's working, where to push next |
| 🟠 **Developing** | `adoption_pct` 30–49 | Recovery framing — identify blockers, offer support plan |
| 🔴 **At Risk** | `adoption_pct < 30` OR `Adoption_Score__c < 30` | Urgent — adoption gap is a churn signal; involve CSM proactively |

Set `value_risk_flag = true` when classification = At Risk.

---

### Step 2 — Overall adoption summary

Produce a one-paragraph adoption overview.

**Required metrics:**

| Field | API Name | If null → |
|---|---|---|
| Active Users | `Active_Users__c` | "Active users: not available" |
| Quoted Employees | `Max_Quoted_Number_EE__c` | Cannot calculate adoption % — flag as warning |
| Adoption % | Calculated | Derive from above |
| Adoption Score | `Adoption_Score__c` | Omit score line |
| Paying Modules | `Paying_Modules_Text__c` | "Modules: not available in Salesforce" |
| Live on Bob? | `Customer_Is_Live__c` | If false → prepend: "⚠️ Account is not yet live — adoption data may not be meaningful" |

**Format:**
```
### Adoption Summary
{active_users} of {quoted_employees} licensed employees are active on Bob
({adoption_pct}% seat utilization).

Adoption Score: {score}/100 ({classification_label})
Modules in use: {paying_modules}
```

---

### Step 3 — Per-module adoption breakdown

Use `Customer360_Trends__c` records (`Feature__c` + `Value_Number__c`).

For each module in the account's `Paying_Modules_Text__c`:

| Module status | Condition | Label |
|---|---|---|
| ✅ Active | `Value_Number__c` > 0 and above threshold | "Active — {value}" |
| ⚠️ Low | `Value_Number__c` > 0 but below threshold | "Low usage — {value}" |
| ❌ Dormant | `Value_Number__c` = 0 or record absent | "Dormant — not in use" |
| — | Module in paying list but no trend record | "No data available" |

**Module thresholds (approximate — adjust per CSM knowledge):**

| Module | Low threshold |
|---|---|
| Tasks | < 20% of active users creating tasks |
| MAU (Monthly Active Users) | < 50% of seat quota |
| Survey | < 1 survey sent in 30 days |
| Performance Reviews | < 50% of employees with an active review cycle |
| eSign / eDocs | < 10 documents signed in 30 days |
| Time-Off Requests | < 30% of employees submitting requests |
| Analytics | < 3 report views in 30 days |
| Triggered Flows | 0 flows triggered in 30 days |

**Output per module:**
```
| Module | Usage | Status |
|---|---|---|
| Tasks | {value} | ✅ Active |
| Survey | {value} | ⚠️ Low |
| Performance | — | ❌ Dormant |
```

Rank modules: active first, then low, then dormant.

---

### Step 4 — Adoption coaching angles

Based on the per-module breakdown, produce 2–3 actionable coaching angles for the CSM.

**Rules:**
- One angle must address the lowest-performing active module.
- If any paying module is dormant → one angle must address activation.
- Do not suggest purchasing new modules (that is the Expansion Specialist's job).
- Frame angles as CSM talking points, not product pitches.

**Examples by scenario:**

| Scenario | Coaching angle |
|---|---|
| Survey module dormant | "Consider hosting a quick workshop on survey best practices — many teams aren't aware of pulse survey templates." |
| Low MAU with high quoted seats | "Are there departments that haven't completed onboarding? A targeted re-engagement session could recover inactive users." |
| Performance Reviews not started | "With {N} employees, a performance cycle could deliver significant manager time savings — help them set up the first template." |
| All modules healthy | "Adoption is strong across all modules — this is a great moment to explore advanced workflows or analytics dashboards." |

---

### Step 5 — Value realization narrative

Produce a short value paragraph for use in customer-facing summaries.

**Healthy / Growing accounts:**
Frame the adoption story as ROI being delivered:
"With {active_users} employees using Bob's core modules, the team is benefiting from
[qualitative value: streamlined workflows / reduced manual HR tasks / unified employee
experience]. {Top module} has seen strong engagement, indicating successful adoption."

**Developing / At Risk accounts:**
Frame as shared opportunity:
"There is significant untapped value in the platform. {dormant_or_low_modules} have
low engagement, which may indicate onboarding gaps or workflow misalignment. A targeted
success plan could help recover this value before renewal."

Do not fabricate specific cost or time savings. Use qualitative framing only.

---

### Step 6 — Assemble the Adoption Brief

```
## Adoption & Value Brief — {account_name}

**Adoption Health:** {badge} {classification}

### Adoption Summary
{adoption_summary_block}

### Module Breakdown
{module_table}

### Value Narrative
{value_paragraph}

### Coaching Angles for the CSM
1. {angle_1}
2. {angle_2}
[3. {angle_3 if applicable}]
```

**For Meeting Prep (meeting_type = Adoption_Risk):**
Append:
```
### Agenda Suggestion (30 min)
1. Check in — how is the team feeling about the platform? (5 min)
2. Walk through adoption data together (10 min)
3. Identify blockers — is it awareness, workflow, or support? (10 min)
4. Agree on a 30-day recovery plan with clear owners (5 min)

### Questions to Validate
- "Which teams are getting the most value from Bob today?"
- "Are there workflows your team does outside of Bob that we could help automate?"
- "Is there anything blocking wider adoption in specific departments?"

### Never Assume
- Do not assume low adoption = dissatisfaction. It may be onboarding gaps.
- Do not push new modules in an adoption recovery conversation.
```

---

## Resources

- `knowledge-and-data-enricher.md` — provides fetch_bundle as input
- `fetch_bundle.schema.json` — input schema reference
- `output_modes.md` — snapshot / full_360 / meeting_prep output shapes
- `Meeting_Type_Topic_Matrix.csv` — Adoption_Risk section priorities and guardrails
