---
name: expansion-and-growth
description: >
  Identifies whitespace expansion opportunities based on paid modules, usage patterns,
  and external company context. Receives growth_and_value, commercial, and
  external_intelligence sections and produces an expansion-ready brief with upsell
  angles, whitespace analysis, and market-signal-driven growth framing. Never pushes
  expansion on accounts with active churn signals — suppression rules are mandatory.
labels:
  - specialist
  - domain-expertise
  - expansion
  - growth
  - upsell
  - account360
---

## Context

**Activated when:** The Brain routes `meeting_type = Expansion` or the CSM requests
a growth, upsell, or whitespace conversation.

**Suppression check (run before any output):** If `Open_Churn_Requests__c > 0` OR
`risk_severity` = high / critical → STOP. Return:
"Expansion brief suppressed — active churn or critical risk signal detected.
Resolve retention before initiating growth conversations."

**Data input:** Receives the following fetch_bundle sections from
`knowledge-and-data-enricher`:
- `growth_and_value` (full — module ownership and usage)
- `commercial` (ARR, ARPU, segment, paying modules)
- `external_intelligence` (company context and market signals)

**Output target:** Populates the **Growth & Value** section and informs the expansion
agenda in Meeting Prep briefs.

---

## Instructions

### Step 1 — Suppression gate

| Check | If true → |
|---|---|
| `Open_Churn_Requests__c > 0` | STOP. Return suppression message. |
| `risk_severity` = high or critical | STOP. Return suppression message. |
| `Customer_Is_Live__c` = false | Flag: "Account not yet live — expansion conversation is premature. Focus on successful go-live first." |
| `adoption_pct < 40` | Add caution: "⚠️ Adoption is low ({pct}%) — anchor expansion in adoption recovery first, then introduce growth." |

---

### Step 2 — Whitespace analysis

Compare modules owned (`Paying_Modules_Text__c`) against the full Bob product suite
to identify unowned modules.

**Bob module reference list (standard):**
Core HR · Tasks · Survey · Performance Reviews · eSign / eDocs · Time-Off · Analytics ·
Triggered Flows · Payroll · Workforce Planning · Compensation

For each unowned module, evaluate relevance based on:
- Company size (`Max_Quoted_Number_EE__c` and `employee_band_or_size_hint`)
- Industry (`Industry`)
- Existing module usage patterns
- External signals (growth, funding, new markets)

**Relevance scoring (internal — do not expose to CSM):**

| Relevance | Condition |
|---|---|
| High | Module is commonly adopted by similar-industry accounts at this size tier |
| Medium | Module has clear workflow adjacency to a heavily-used existing module |
| Low | Module is specialized or not immediately relevant |

Show only High and Medium relevance modules in the output.

---

### Step 3 — Market signal integration

Use `external_intelligence` section to add growth context.

| Signal | Expansion implication |
|---|---|
| `funding` | "Recent funding ({signal}) suggests headcount growth — seat expansion and Workforce Planning are relevant." |
| `acquisition` | "M&A activity may bring new employee populations — multi-entity HR consolidation is a strong angle." |
| `leadership_change` | "New leadership may bring fresh appetite for HR transformation — time the conversation carefully." |
| `ipo_readiness` | "IPO preparation often drives need for structured performance and compensation processes." |
| `layoffs` | Flag internally: "Recent workforce reduction — avoid expansion framing. De-prioritize this specialist." |

Only include signals with `confidence ≥ medium`.

**Suppression rule for layoffs:** If `signal_topics` contains `layoffs` AND
`confidence ≥ medium` → suppress expansion brief and return:
"Market signal indicates recent workforce reduction. Expansion conversation is not
recommended at this time."

---

### Step 4 — ARPU and seat expansion context

Use `WTRF_ARPU_Committed__c` and `Max_Quoted_Number_EE__c` for commercial framing.

| Scenario | Framing |
|---|---|
| Active users close to quoted ceiling (≥ 90%) | "Seat utilization is near capacity — a headcount expansion is a natural trigger for a seat upsell conversation." |
| Active users significantly below ceiling (< 60%) | "Focus on activating existing seats before discussing headcount expansion." |
| ARPU available | Show as context for the AM: "Current ARPU: ${arpu}" |

---

### Step 5 — Expansion angles

Produce 2–3 specific, data-grounded expansion angles. Each angle must reference a
specific module, usage gap, or market signal.

**Format per angle:**
```
**Module/Angle:** {module or signal}
**Why now:** {1-line rationale grounded in data}
**Talking point:** "{CSM-ready phrase to open the conversation}"
```

**Examples:**

```
**Module:** Performance Reviews
**Why now:** Account has strong Task and Survey adoption but Performance module is
dormant. Similar-sized companies in {industry} use it for manager effectiveness.
**Talking point:** "I noticed you're not yet using Performance Reviews — given your
team size, it could save your managers significant time on cycle management."
```

```
**Module:** Workforce Planning
**Why now:** Recent funding signal suggests headcount growth is on the horizon.
**Talking point:** "With your recent growth, have you thought about how you'll manage
headcount planning? We have a module that might help with that."
```

---

### Step 6 — Assemble the Expansion Brief

```
## Expansion & Growth Brief — {account_name}

**Growth Posture:** {Ready / Caution — adoption gap / Suppressed}

### Company & Market Context
{company_summary_one_line}
{market_signal_if_applicable}

### Seat & Module Snapshot
- Seats: {active_users} of {quoted_employees} active ({adoption_pct}%)
- Modules owned: {paying_modules}
- ARPU: {arpu_if_available}

### Whitespace Opportunities
{whitespace_table: Module | Relevance | Why}

### Expansion Angles
{angle_1}
{angle_2}
[{angle_3 if applicable}]
```

**For Meeting Prep (meeting_type = Expansion):**
Append:
```
### Agenda Suggestion (30 min)
1. Check in on current platform value (5 min)
2. Share adoption wins — anchor expansion in existing success (10 min)
3. Introduce whitespace opportunity — one module max per call (10 min)
4. Confirm interest and agree on next step (5 min)

### Questions to Validate
- "How is your team's headcount evolving over the next 12 months?"
- "Are there HR processes today that still happen outside of Bob?"
- "Have you had a chance to explore {specific module}?"

### Never Assume
- Never introduce more than one new module per conversation.
- Do not present pricing without involving the Account Manager.
- Do not push expansion if the customer hasn't confirmed satisfaction with existing modules.
```

---

## Resources

- `knowledge-and-data-enricher.md` — provides fetch_bundle as input
- `fetch_bundle.schema.json` — input schema reference
- `output_modes.md` — meeting_prep output shape
- `Meeting_Type_Topic_Matrix.csv` — Expansion section priorities and guardrails
