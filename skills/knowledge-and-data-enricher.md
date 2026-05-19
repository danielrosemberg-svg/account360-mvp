---
name: knowledge-and-data-enricher
description: >
  Loads knowledge at startup and fetches domain-specific data after routing.
  Provides each specialist with the exact data slice it needs: account baseline,
  commercial fields, adoption metrics (Account + Customer360_Trends__c),
  risk indicators, opportunity context, support tickets (Case object), interaction
  log (Task), and Gong call context (Gong__Gong_Call__c). Also fetches external
  intelligence via Tavily for EBR and Expansion specialists. Ensures no agent
  invents information — everything must be sourced through this skill.
  All Salesforce data is fetched via the Salesforce SOQL MCP tool only.
  No direct Gong or Zendesk API calls.
labels:
  - data-fetch
  - knowledge-base
  - salesforce
  - gong
  - tavily
  - enrichment
  - account360
---

## Context

This skill has three execution phases with different triggers:

**Phase A — Static Knowledge Load (at session start, once per session):**
Load the knowledge files into agent context at the start of every Account 360
session. Do NOT reload between requests in the same session. Available to
The Brain, all Specialists, and all Compose skills throughout the session.

**Phase B — Domain Enrichment (after routing, per specialist):**
After `account360-intake-classifier` routes to one or more specialists, each
specialist calls this skill to fetch only the data its domain requires.
Specialists can run in parallel when the routing packet includes multiple domains.

**Phase C — Gong Context Fetch + External Intelligence (at compose time):**
Gong call data is fetched from Salesforce (`Gong__Gong_Call__c`) for specialists
that require interaction context. External intelligence (Tavily) is fetched in
parallel with Phase B for EBR / QBR & Executive and Expansion & Growth specialists.

---

## Instructions

### Phase A: Static Knowledge Load

Load the following files into agent context at session start. These are attached
as ChatGPT Knowledge files — no MCP tool calls needed.

| Source | Content | Loaded Into |
|---|---|---|
| `output_modes.md` | Definitions for snapshot / full_360 / meeting_prep, disambiguation rules, and default logic | The Brain, all Specialists, all Compose skills |
| `Meeting_Type_Topic_Matrix.csv` | Per-meeting-type section priorities, key validation questions, never-assume guardrails | The Brain, Compose_Meeting_Prep_Brief |
| `fetch_bundle.schema.json` | Canonical output schema — required sections, field types, missing_data structure | All Specialists (for self-validation before emitting output) |
| `Account360_data_points_mapped.xlsx` | Full field mapping: which specialist uses which SF field, API names, logic conditions | Reference only — do not re-read per request |

---

### Phase B: Domain Enrichment (per specialist, after routing)

Each specialist calls this skill with its domain. Fetch only the fields relevant
to that domain — do not over-fetch. Replace `'{ACCOUNT_ID}'` with the
`salesforce_account_id` from the routing packet in every SOQL query.

---

#### The Brain — Account Gate Check

**Salesforce — Account** (identity gate, runs before any specialist)

SOQL:
```sql
SELECT Id, Name, Account_Status__c, OwnerId, Owner.Name, Owner.Email
FROM Account
WHERE Id = '{ACCOUNT_ID}'
```

| Field Label | API Name | Used in |
|---|---|---|
| Account Name | `Name` | Identity confirmation + routing copy |
| Account Status | `Account_Status__c` | Hard gate — Churned/Inactive → EXIT |
| Account Owner (CSM) | `OwnerId → Owner.Name` | Output routing + Slack DM personalization |
| CSM Email | `Owner.Email` | Slack Drafter delivery target |

**Gate rule:** If `Account_Status__c` = Churned or Inactive → stop pipeline,
return message to CSM: "This account is not active — please verify the Account ID."

---

#### Renewals & Commercial Specialist

**Salesforce — Account (commercial fields)**

SOQL:
```sql
SELECT
    WTRF_ARR__c, Account_Tier_Micro__c,
    Master_Contract_End_Date__c, First_Contract_Start_Date__c,
    OwnerId, Owner.Name, Renewal_Manager__c, Account_Manager__c,
    Customer_Is_Live__c, Max_Quoted_Number_EE__c,
    Active_Users__c, Adoption_Score__c, Paying_Modules_Text__c,
    account_health_sentiment__c, Overall_Risk_Severity__c,
    Risk_Reason__c, Overall_Risk_Impact_ARR__c, Modules_at_Risk__c,
    Open_Churn_Requests__c
FROM Account
WHERE Id = '{ACCOUNT_ID}'
```

| Field Label | API Name | Used in Use Cases |
|---|---|---|
| ARR | `WTRF_ARR__c` | RN-01, RN-02, RN-03, RN-04, RN-05 |
| Segment / Tier | `Account_Tier_Micro__c` | RN-05 (tone calibration) |
| Renewal Date | `Master_Contract_End_Date__c` | RN-01, RN-05 (urgency flag) |
| Contract Start | `First_Contract_Start_Date__c` | RN-05 (tenure calc) |
| Account Owner (CSM) | `OwnerId → Owner.Name` | RN-05 (ownership block) |
| Renewal Manager | `Renewal_Manager__c` | RN-05, RS-05 |
| Account Manager | `Account_Manager__c` | RN-05 |
| Live on Bob? | `Customer_Is_Live__c` | RN-02 (suppress adoption if false) |
| Employees (quoted) | `Max_Quoted_Number_EE__c` | RN-02 (adoption % denominator) |
| Active Users | `Active_Users__c` | RN-02 (adoption % numerator) |
| Adoption Score | `Adoption_Score__c` | RN-02 (health framing) |
| Paying Modules | `Paying_Modules_Text__c` | RN-02, RN-05 |
| Account Health Sentiment | `account_health_sentiment__c` | RN-01, RN-03 |
| Risk Severity | `Overall_Risk_Severity__c` | RN-01, RN-03 |
| Risk Reason | `Risk_Reason__c` | RN-03 |
| Risk ARR Impact | `Overall_Risk_Impact_ARR__c` | RN-03 |
| Modules at Risk | `Modules_at_Risk__c` | RN-03 |
| Open Churn Requests | `Open_Churn_Requests__c` | RN-01 (churn suppression) |

**Salesforce — Opportunity** (most recent open deal)

SOQL:
```sql
SELECT Id, Name, StageName, CloseDate, Amount
FROM Opportunity
WHERE AccountId = '{ACCOUNT_ID}'
  AND IsClosed = false
ORDER BY CloseDate ASC
```

| Field Label | API Name | Used in Use Cases |
|---|---|---|
| Stage | `StageName` | RN-01, RN-05 (deal status context) |
| Close Date | `CloseDate` | RN-05 |
| Amount | `Amount` | RN-01, RN-05 |
| Opportunity Name | `Name` | RN-05 |

**Salesforce — Interaction Log** (Task, last 60 days)

SOQL:
```sql
SELECT Id, Subject, Description, ActivityDate, Owner.Name
FROM Task
WHERE WhatId = '{ACCOUNT_ID}'
  AND ActivityDate >= LAST_N_DAYS:60
ORDER BY ActivityDate DESC
```

| Field Label | API Name | Used in Use Cases |
|---|---|---|
| Subject | `Subject` | RN-04 (last touchpoint context) |
| Description / Notes | `Description` | RN-04 |
| Activity Date | `ActivityDate` | RN-04 (recency flag) |

---

#### Risk & Escalation Specialist

**Salesforce — Account (risk fields)**

SOQL:
```sql
SELECT
    account_health_sentiment__c, Overall_Risk_Severity__c,
    Risk_Reason__c, Overall_Risk_Impact_ARR__c, Modules_at_Risk__c,
    Open_Churn_Requests__c, Total_Customer_Related_Risks__c,
    WTRF_ARR__c, Master_Contract_End_Date__c,
    Renewal_Manager__c, Account_Manager__c
FROM Account
WHERE Id = '{ACCOUNT_ID}'
```

| Field Label | API Name | Used in Use Cases |
|---|---|---|
| Account Health Sentiment | `account_health_sentiment__c` | RS-01, RS-02, RS-04, RS-05 |
| Risk Severity | `Overall_Risk_Severity__c` | RS-01, RS-02, RS-03, RS-04, RS-05 |
| Risk Reason | `Risk_Reason__c` | RS-01, RS-02, RS-04 |
| Risk ARR Impact | `Overall_Risk_Impact_ARR__c` | RS-01, RS-03 |
| Modules at Risk | `Modules_at_Risk__c` | RS-01, RS-03 |
| Open Churn Requests | `Open_Churn_Requests__c` | RS-01, RS-02, RS-05 — triggers churn suppression |
| Total Customer Risks | `Total_Customer_Related_Risks__c` | RS-02, RS-05 |
| ARR | `WTRF_ARR__c` | RS-03 (commercial impact framing) |
| Renewal Date | `Master_Contract_End_Date__c` | RS-01 (renewal proximity risk) |
| Renewal Manager | `Renewal_Manager__c` | RS-05 (escalation protocol) |
| Account Manager | `Account_Manager__c` | RS-05 |

**Salesforce — Case** (high-priority open support tickets)

SOQL:
```sql
SELECT Id, CaseNumber, Subject, Priority, Status
FROM Case
WHERE AccountId = '{ACCOUNT_ID}'
  AND Status != 'Closed'
  AND Priority IN ('High', 'Critical')
ORDER BY CreatedDate DESC
```

| Field Label | API Name | Used in Use Cases |
|---|---|---|
| Case Number | `CaseNumber` | RS-01, RS-02 (escalation reference) |
| Subject | `Subject` | RS-01, RS-02 (issue awareness) |
| Priority | `Priority` | RS-01 (urgency signal) |
| Status | `Status` | RS-02 |

---

#### EBR / QBR & Executive Specialist

**Salesforce — Account (full commercial + adoption + risk)**

SOQL:
```sql
SELECT
    Name, Industry, BillingCountry, Max_Quoted_Number_EE__c,
    WTRF_ARR__c, Account_Tier_Micro__c,
    Master_Contract_End_Date__c, First_Contract_Start_Date__c,
    OwnerId, Owner.Name, Renewal_Manager__c, Account_Manager__c,
    Active_Users__c, Adoption_Score__c, Paying_Modules_Text__c,
    account_health_sentiment__c, Overall_Risk_Severity__c,
    Risk_Reason__c, Overall_Risk_Impact_ARR__c, Modules_at_Risk__c,
    Open_Churn_Requests__c, NPS__c, Advocacy_Status__c
FROM Account
WHERE Id = '{ACCOUNT_ID}'
```

| Field Label | API Name | Used in Use Cases |
|---|---|---|
| Account Name + Industry + Country | `Name`, `Industry`, `BillingCountry` | EBR-01 (company context block) |
| Employees (quoted) | `Max_Quoted_Number_EE__c` | EBR-02 (sizing) |
| ARR | `WTRF_ARR__c` | EBR-01, EBR-02, EBR-03 |
| Segment | `Account_Tier_Micro__c` | EBR-01 (executive tier calibration) |
| Renewal Date | `Master_Contract_End_Date__c` | EBR-03, EBR-01 |
| Contract Start | `First_Contract_Start_Date__c` | EBR-01 (tenure) |
| Owners (CSM, RM, AM) | `OwnerId`, `Renewal_Manager__c`, `Account_Manager__c` | EBR-01 |
| Active Users + Adoption Score | `Active_Users__c`, `Adoption_Score__c` | EBR-02 (ROI narrative) |
| Paying Modules | `Paying_Modules_Text__c` | EBR-02 |
| Health + Risk Severity + Risk Reason | `account_health_sentiment__c`, `Overall_Risk_Severity__c`, `Risk_Reason__c` | EBR-06 |
| Risk ARR Impact + Modules at Risk | `Overall_Risk_Impact_ARR__c`, `Modules_at_Risk__c` | EBR-06 |
| Open Churn Requests | `Open_Churn_Requests__c` | EBR-06 (churn suppression) |
| NPS | `NPS__c` | EBR-05, EBR-06 |
| Advocacy Status | `Advocacy_Status__c` | EBR-05 |

**Salesforce — Customer360_Trends__c** (per-module adoption)

SOQL:
```sql
SELECT Feature__c, Value_Number__c
FROM Customer360_Trends__c
WHERE AccountId = '{ACCOUNT_ID}'
```

| Field Label | API Name | Used in Use Cases |
|---|---|---|
| Per-module usage (Tasks, MAU, Survey, Performance, eSign, Time-Off, Analytics, Flows) | `Feature__c / Value_Number__c` | EBR-02 (top/bottom module highlights for ROI narrative) |

**Salesforce — Opportunity**

SOQL:
```sql
SELECT Id, Name, StageName, CloseDate, Amount
FROM Opportunity
WHERE AccountId = '{ACCOUNT_ID}'
  AND IsClosed = false
ORDER BY CloseDate ASC
```

| Field Label | API Name | Used in Use Cases |
|---|---|---|
| Stage + Close Date + Amount | `StageName`, `CloseDate`, `Amount` | EBR-03 (renewal deal context) |

**External Intelligence — Tavily API** *(Phase C, parallel fetch)*

| Query | Output | Used in Use Cases |
|---|---|---|
| `"{account_name} company overview {industry}"` | `company_snapshot_plain` (2–5 lines) | EBR-01, EBR-04 |
| `"{account_name} company news 2026"` | `recent_signal_one_line` + `signal_topics` | EBR-04 (market context for exec narrative) |

Confidence rule: only include signals with confidence ≥ medium.
If `signal_topics` contains `layoffs` → suppress in output, flag for CSM.

---

#### Adoption & Value Specialist

**Salesforce — Account (adoption fields)**

SOQL:
```sql
SELECT
    Active_Users__c, Max_Quoted_Number_EE__c,
    Paying_Modules_Text__c, Adoption_Score__c,
    Customer_Is_Live__c
FROM Account
WHERE Id = '{ACCOUNT_ID}'
```

| Field Label | API Name | Used in Use Cases |
|---|---|---|
| Active Users | `Active_Users__c` | AV-01, AV-02, AV-06 |
| Employees (quoted) | `Max_Quoted_Number_EE__c` | AV-01 (adoption % denominator) |
| Paying Modules | `Paying_Modules_Text__c` | AV-01, AV-02, AV-03 |
| Adoption Score | `Adoption_Score__c` | AV-01, AV-04, AV-05 |
| Live on Bob? | `Customer_Is_Live__c` | AV-01 (suppress if false) |

**Salesforce — Customer360_Trends__c** (per-module adoption — primary data source)

SOQL:
```sql
SELECT Feature__c, Value_Number__c
FROM Customer360_Trends__c
WHERE AccountId = '{ACCOUNT_ID}'
```

| Field Label | API Name | Used in Use Cases |
|---|---|---|
| Adoption — Tasks | `Feature__c / Value_Number__c` | AV-02, AV-03 |
| Adoption — MAU | `Feature__c / Value_Number__c` | AV-01, AV-02 |
| Adoption — Survey | `Feature__c / Value_Number__c` | AV-02, AV-03 |
| Adoption — Performance Reviews | `Feature__c / Value_Number__c` | AV-02, AV-03 |
| Adoption — eSign & eDocs | `Feature__c / Value_Number__c` | AV-02, AV-03 |
| Adoption — Time-Off Requests | `Feature__c / Value_Number__c` | AV-02, AV-03 |
| Adoption — Analytics | `Feature__c / Value_Number__c` | AV-02, AV-03 |
| Adoption — Triggered Flows | `Feature__c / Value_Number__c` | AV-02, AV-03 |
| Adoption — Employee Reports | `Feature__c / Value_Number__c` | AV-02 |

---

#### Expansion & Growth Specialist

**Salesforce — Account (commercial + adoption)**

SOQL:
```sql
SELECT
    WTRF_ARR__c, WTRF_ARPU_Committed__c, Account_Tier_Micro__c,
    Max_Quoted_Number_EE__c, Active_Users__c,
    Paying_Modules_Text__c, Adoption_Score__c,
    Open_Churn_Requests__c, Overall_Risk_Severity__c,
    Industry, BillingCountry, Customer_Is_Live__c
FROM Account
WHERE Id = '{ACCOUNT_ID}'
```

| Field Label | API Name | Used in Use Cases |
|---|---|---|
| ARR + ARPU | `WTRF_ARR__c`, `WTRF_ARPU_Committed__c` | EX-01, EX-02, EX-05 |
| Segment | `Account_Tier_Micro__c` | EX-01 (tier-based whitespace) |
| Employees (quoted) + Active Users | `Max_Quoted_Number_EE__c`, `Active_Users__c` | EX-02 (seat expansion context) |
| Paying Modules | `Paying_Modules_Text__c` | EX-01 (whitespace analysis) |
| Adoption Score | `Adoption_Score__c` | EX-02 (adoption gate for expansion) |
| Open Churn Requests + Risk Severity | `Open_Churn_Requests__c`, `Overall_Risk_Severity__c` | EX-01 (suppression gate) |
| Industry + Country | `Industry`, `BillingCountry` | EX-04 (market context) |
| Live on Bob? | `Customer_Is_Live__c` | EX-01 (not live → expansion premature) |

**Salesforce — Customer360_Trends__c** (per-module — whitespace detection)

SOQL:
```sql
SELECT Feature__c, Value_Number__c
FROM Customer360_Trends__c
WHERE AccountId = '{ACCOUNT_ID}'
```

| Field Label | API Name | Used in Use Cases |
|---|---|---|
| Per-module usage | `Feature__c / Value_Number__c` | EX-01, EX-02 (identify dormant paid modules + unowned module gaps) |

**Salesforce — Opportunity**

SOQL:
```sql
SELECT Id, Name, StageName, CloseDate, Amount
FROM Opportunity
WHERE AccountId = '{ACCOUNT_ID}'
  AND IsClosed = false
ORDER BY CloseDate ASC
```

| Field Label | API Name | Used in Use Cases |
|---|---|---|
| Stage + Amount | `StageName`, `Amount` | EX-05 (existing deal context for AM) |

**External Intelligence — Tavily API** *(Phase C, parallel fetch)*

| Query | Output | Used in Use Cases |
|---|---|---|
| `"{account_name} company overview"` | `company_snapshot_plain` | EX-04 |
| `"{account_name} company news 2026"` | `recent_signal_one_line` + `signal_topics` | EX-03 (market signal → expansion angle) |

Suppression rule: if `signal_topics` contains `layoffs` AND confidence ≥ medium
→ return suppression message; do not produce expansion brief.

---

#### Onboarding & Kickoff Specialist

**Salesforce — Account (contract + live status)**

SOQL:
```sql
SELECT
    Name, Industry, BillingCountry, Account_Tier_Micro__c,
    Max_Quoted_Number_EE__c, Customer_Is_Live__c,
    First_Contract_Start_Date__c, Master_Contract_End_Date__c,
    OwnerId, Owner.Name, Paying_Modules_Text__c,
    Active_Users__c
FROM Account
WHERE Id = '{ACCOUNT_ID}'
```

| Field Label | API Name | Used in Use Cases |
|---|---|---|
| Account Name + Industry + Country | `Name`, `Industry`, `BillingCountry` | ON-01 (context block) |
| Segment + Employees | `Account_Tier_Micro__c`, `Max_Quoted_Number_EE__c` | ON-01 |
| Live on Bob? | `Customer_Is_Live__c` | ON-01, ON-04 (go-live status gate) |
| Contract Start + Renewal Date | `First_Contract_Start_Date__c`, `Master_Contract_End_Date__c` | ON-01, ON-06 (days since start) |
| Account Owner | `OwnerId → Owner.Name` | ON-01 |
| Paying Modules + Active Users | `Paying_Modules_Text__c`, `Active_Users__c` | ON-03 (activation roadmap) |

**Salesforce — Contact** (primary stakeholder)

SOQL:
```sql
SELECT Id, Name, Title, Email
FROM Contact
WHERE AccountId = '{ACCOUNT_ID}'
ORDER BY CreatedDate ASC
```

| Field Label | API Name | Used in Use Cases |
|---|---|---|
| Contact Name | `Name` | ON-01, ON-05 (stakeholder identification) |
| Contact Title | `Title` | ON-05 (role for champion mapping) |
| Contact Email | `Email` | ON-05 |

**Salesforce — Interaction Log** (Task, last 90 days)

SOQL:
```sql
SELECT Id, Subject, Description, ActivityDate, Owner.Name
FROM Task
WHERE WhatId = '{ACCOUNT_ID}'
  AND ActivityDate >= LAST_N_DAYS:90
ORDER BY ActivityDate DESC
```

| Field Label | API Name | Used in Use Cases |
|---|---|---|
| Subject + Description | `Subject`, `Description` | ON-02 (go-live progress context) |
| Activity Date | `ActivityDate` | ON-02 (days since last contact) |

---

#### Health Check & Check-in Specialist

**Salesforce — Account (full health picture)**

SOQL:
```sql
SELECT
    Name, Industry, BillingCountry, Account_Tier_Micro__c,
    WTRF_ARR__c, Master_Contract_End_Date__c,
    OwnerId, Owner.Name, Max_Quoted_Number_EE__c,
    Active_Users__c, Adoption_Score__c, Paying_Modules_Text__c,
    account_health_sentiment__c, Overall_Risk_Severity__c,
    Risk_Reason__c, Open_Churn_Requests__c,
    Customer_Is_Live__c, NPS__c, Advocacy_Status__c
FROM Account
WHERE Id = '{ACCOUNT_ID}'
```

| Field Label | API Name | Used in Use Cases |
|---|---|---|
| Account Name + Industry | `Name`, `Industry` | HC-01 |
| ARR + Renewal Date | `WTRF_ARR__c`, `Master_Contract_End_Date__c` | HC-01, HC-05 |
| Employees + Active Users | `Max_Quoted_Number_EE__c`, `Active_Users__c` | HC-01, HC-02 |
| Adoption Score + Paying Modules | `Adoption_Score__c`, `Paying_Modules_Text__c` | HC-01, HC-02 |
| Health Sentiment | `account_health_sentiment__c` | HC-01, HC-02, HC-04 |
| Risk Severity + Reason | `Overall_Risk_Severity__c`, `Risk_Reason__c` | HC-01, HC-02, HC-05 |
| Open Churn Requests | `Open_Churn_Requests__c` | HC-02, HC-05 (churn suppression) |
| Live on Bob? | `Customer_Is_Live__c` | HC-01 |
| NPS + Advocacy Status | `NPS__c`, `Advocacy_Status__c` | HC-04 (relationship health) |

**Salesforce — Interaction Log** (Task, last 60 days)

SOQL:
```sql
SELECT Id, Subject, Description, ActivityDate, Owner.Name
FROM Task
WHERE WhatId = '{ACCOUNT_ID}'
  AND ActivityDate >= LAST_N_DAYS:60
ORDER BY ActivityDate DESC
```

| Field Label | API Name | Used in Use Cases |
|---|---|---|
| Subject + Notes | `Subject`, `Description` | HC-03 (recent touchpoint) |
| Activity Date | `ActivityDate` | HC-03 (recency flag — > 30 days → proactive outreach) |

---

### Phase C: Gong Context Fetch

Called for: **Snapshot**, Renewals & Commercial (RN-04), Risk & Escalation (RS-04, RS-05),
EBR / QBR & Executive (EBR-05), Onboarding & Kickoff (ON-02), Health Check (HC-03).

Gong call data is synced into Salesforce — no direct Gong API call is made.

SOQL (try primary field names first; fall back to alternates if query fails):
```sql
SELECT
    Id,
    Gong__Title__c,
    Gong__Call_Key_Points__c,
    Gong__Start_Time__c,
    Gong__Participants__c
FROM Gong__Gong_Call__c
WHERE AccountId = '{ACCOUNT_ID}'
  AND Gong__Start_Time__c >= LAST_N_DAYS:90
ORDER BY Gong__Start_Time__c DESC
```

Alternate field names (older Gong Salesforce package):
```sql
SELECT
    Id,
    gong_title_c,
    Gong__Call_Key_Points__c,
    gong_related_participants_json_c,
    gong_call_start_c
FROM Gong__Gong_Call__c
WHERE AccountId = '{ACCOUNT_ID}'
  AND gong_call_start_c >= LAST_N_DAYS:90
ORDER BY gong_call_start_c DESC
```

| Field Label | API Name (primary) | API Name (alternate) | Purpose |
|---|---|---|---|
| Call Title | `Gong__Title__c` | `gong_title_c` | Call topic for brief |
| Key Points | `Gong__Call_Key_Points__c` | `Gong__Call_Key_Points__c` | Discussion highlights |
| Participants (JSON) | `Gong__Participants__c` | `gong_related_participants_json_c` | Stakeholder map — parse name + title + email domain |
| Call Date | `Gong__Start_Time__c` | `gong_call_start_c` | Recency — last 2 calls for Snapshot |

**Participant parsing rule:**
Parse participants JSON array. For each entry extract `name`, `title`, `email`.
Classify by email domain: `@hibob.io` → HiBob side. All others → Customer side.

Output:
```json
{
  "gong_calls": [
    {
      "title": "Q2 Business Review",
      "date": "2026-05-08",
      "highlights": ["Discussed adoption drop in Performance", "CFO joining renewal call"],
      "participants": [
        { "name": "Jane Cohen", "role": "CHRO", "email": "jane@acme.com" }
      ]
    }
  ]
}
```

If no Gong records exist → return `gong_calls: []`.
Do not block output — fall back to Task interaction log.

**The Data Rule**: This skill may only return field values directly sourced from
Salesforce SOQL results or Tavily. It must never generate, estimate, or assume
a field value. If a field returns null → log in `missing_data` and leave empty.
Never substitute a plausible-sounding value.

---

## Resources

- **Salesforce SOQL MCP Tool**: All structured CRM data. Objects used: `Account`,
  `Contact`, `Opportunity`, `Task`, `Case`, `Customer360_Trends__c`,
  `Gong__Gong_Call__c` (Phase 2 — Gong Salesforce package required).
  No direct Gong or Zendesk API calls.
- **Tavily API**: External intelligence for EBR / QBR & Executive and
  Expansion & Growth specialists. Requires `TAVILY_API_KEY`.
  Public sources only — no login-gated content.
- **`output_modes.md`**: Load as ChatGPT Knowledge. Defines snapshot / full_360 /
  meeting_prep intents and deliverable shapes.
- **`Meeting_Type_Topic_Matrix.csv`**: Load as ChatGPT Knowledge. Section priorities,
  key questions, never-assume guardrails per meeting type.
- **`fetch_bundle.schema.json`**: Load as ChatGPT Knowledge. Canonical output schema
  for self-validation before emitting the brief.
- **`Account360_data_points_mapped.xlsx`**: Load as ChatGPT Knowledge. Full field
  mapping reference — specialist → SF object → API name → condition.
- **Output consumed by**: all 7 Domain Specialists (Phase B),
  Compose_Snapshot, Compose_Full_360, Compose_Meeting_Prep_Brief, Slack Drafter.
- **Static knowledge consumed by**: The Brain, all Specialists, all Compose skills (Phase A).
