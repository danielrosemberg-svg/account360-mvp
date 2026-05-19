---
name: account360-html-briefs
description: use when a hibob user asks for a customer snapshot, account snapshot, full 360, account 360, customer 360, meeting prep, qbr prep, renewal prep, or customer brief and expects a structured visual output. this skill converts gathered account intelligence into a self-contained aimind x hibob branded html page by default, using a normalized json contract and renderer. trigger for phrases like "snapshot for", "full 360 for", "meeting prep for", "account brief", "visual", "html", or recurring customer-prep workflows.
---

# Account360 HTML Briefs

## Purpose

Use this skill to turn customer intelligence workflows into polished, reusable HTML outputs instead of plain chat-only summaries. It supports three default brief types:

1. `snapshot` — compact account snapshot for quick CSM/RM/AM context.
2. `full360` — deeper customer 360 brief with expanded account, commercial, adoption, support, risk, and interaction sections.
3. `meeting_prep` — meeting-ready prep sheet with objectives, talk tracks, questions, risks, and next actions.

Always produce an HTML artifact unless the user explicitly asks for a different format.

## Operating Rules

- Gather account data from the relevant Account 360 / CRM / internal workflow before rendering.
- Do not invent missing account facts. Use `Not available` for missing values.
- Keep internal-only information marked as internal; do not make the output customer-facing unless the user explicitly asks for a customer-safe version.
- Preserve churn/risk suppression logic from the source workflow. If churn is active, prioritize stabilization and do not include expansion language.
- Keep dates explicit and readable.
- Mirror the user's language where practical. Use `language: "en"` or `language: "he"` in the payload.
- Render using the AiMind x hiBob brand layer: cream/light surfaces, charcoal text, purple headings, and the AiMind action gradient.

## Workflow

### 1. Classify the request

Choose `brief_type` from the user request:

- `snapshot` for “snapshot for Cyberbit”, “account snapshot”, “quick brief”, or “customer snapshot”.
- `full360` for “Full 360”, “Account 360”, “complete customer view”, or broad account reviews.
- `meeting_prep` for “meeting prep”, “QBR prep”, “renewal prep”, “prep me for a call”, or customer-meeting planning.

If the user only says “snapshot” or “Full 360”, use HTML by default.

### 2. Gather and normalize data

After collecting the account data, normalize it into the contract in `references/account_brief_html_contract.json`.

Minimum payload shape:

```json
{
  "language": "en",
  "generated_at": "2026-05-19",
  "brief_type": "snapshot",
  "account": {
    "name": "Cyberbit",
    "meta": ["Israel", "Software General", "SMB - Small"],
    "status": "Customer",
    "team": [
      {"label": "CSM", "value": "Olivia Chevallier"},
      {"label": "RM", "value": "Maria Tsamtsika"},
      {"label": "AM", "value": "Idan Mizrahi"}
    ]
  },
  "kpis": [
    {"label": "ARR", "value": "10,546.8"},
    {"label": "Renewal", "value": "30/04/2027"}
  ],
  "sections": [
    {
      "title": "Commercial",
      "layout": "table",
      "items": [
        {"label": "ARR", "value": "10,546.8"},
        {"label": "Renewal Date", "value": "30/04/2027"}
      ]
    }
  ],
  "key_signals": ["Renewal is not immediate, but recent renewal quote activity exists."],
  "recommended_focus": ["Validate the medium risk reason and align on Talent Package adoption."]
}
```

### 3. Render HTML

Generate a self-contained HTML artifact directly. Do not call any external script or file.

Use the AiMind x HiBob brand layer:
- Background: `#FAF9F6` (cream)
- Text: `#1C1C1E` (charcoal)
- Headings / accents: `#6B46C1` (purple)
- KPI cards: white with subtle shadow
- Risk badges: 🔴 Critical/High — `#DC2626`, 🟠 Medium — `#EA580C`, 🟡 Low — `#CA8A04`, 🟢 No Risk — `#16A34A`
- Action gradient: `linear-gradient(135deg, #6B46C1, #EC4899)`

Structure the HTML with:
- Hero section: account name + brief type + meta tags (country, industry, segment)
- KPI strip: ARR, Renewal Date, Days to Renewal
- Sections as defined by the brief type
- All missing fields show as `Not available`
- Self-contained: no external CSS or JS dependencies

### 4. Verify output

Before sharing, quickly inspect that:

- account name and brief type are visible in the hero area
- KPI cards are populated and not overly long
- alert strips appear only when risk/churn flags require them
- all missing fields display as `Not available`
- the output has sections appropriate for the requested brief type
- the final file is linked to the user as an HTML artifact

## Recommended section patterns

### Snapshot

Use these sections unless the source workflow produces stronger alternatives:

- Commercial
- Risks & Health
- Growth & Value
- Recent Interactions
- External Context
- Key Signals
- Recommended Focus
- Data Gaps, only when useful

### Full 360

Use a deeper structure:

- Account Overview
- Commercial & Renewal
- Health, Risk & Churn
- Product Adoption / Modules
- Support & Open Cases
- Recent Gong / Email / Salesforce Interactions
- External Context
- Opportunity / Expansion Signals, only if not suppressed
- Data Gaps
- Recommended Next Actions

### Meeting Prep

Use a meeting-oriented structure:

- Meeting Objective
- Attendees / Account Team
- Customer Context
- Commercial & Renewal Context
- Health / Risk Watchouts
- Talk Tracks
- Discovery Questions
- Potential Objections
- Recommended Asks
- Follow-up Checklist

## Files

- Renderer: `scripts/render_account_brief.py`
- Contract: `references/account_brief_html_contract.json`
- Output rules and examples: `references/output_rules.md`
