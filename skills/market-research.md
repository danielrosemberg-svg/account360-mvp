---
name: market-research
description: >
  Standalone external intelligence skill. Fetches and synthesizes public market
  signals about a company using the Tavily API. Produces a structured
  external_intelligence block covering company context, recent news signals
  (funding, M&A, layoffs, leadership changes, IPO), and a confidence tier.
  Runs in parallel with the CRM fetch (Phase C of knowledge-and-data-enricher).
  All sources must be public and non-login-gated. Never fabricates signals —
  if no reliable public data is found, returns null and suppresses the section.
labels:
  - skill
  - market-research
  - external-intelligence
  - tavily
  - account360
---

## Context

**Activated when:** `research_fetch` is included in the routing packet's `routed_to`
array — triggered for all output modes (snapshot, full_360, meeting_prep).

**Runs in parallel with:** `knowledge-and-data-enricher` Phase B (CRM fetch).

**Output:** Populates the `external_intelligence` section of the `fetch_bundle`,
which is consumed by:
- EBR / QBR & Executive Specialist (primary consumer)
- Expansion & Growth Specialist (market signal → expansion angle)
- Health Check Specialist (optional context)
- Compose skills (for external strip in Snapshot and Full 360)

**Tool required:** Tavily API (`TAVILY_API_KEY` environment variable).

---

## Instructions

### Step 1 — Prepare search inputs

Extract from the routing packet:
- `account_name` — primary search subject
- `industry` — from `customer_business.industry` if already fetched; else derive from
  account name context
- `country_or_regions` — optional filter hint

Clean the account name before searching:
- Remove legal suffixes: Ltd, Inc, Corp, GmbH, S.A., B.V., etc.
- Remove special characters that would break a search query.
- Example: "Acme Corp, Ltd." → search as `"Acme Corp"`

---

### Step 2 — Company snapshot fetch

**Goal:** 2–5 lines of plain-language public company context. Exec-safe. No
login-gated content.

Tavily query:
```json
{
  "query": "{account_name} company overview {industry}",
  "search_depth": "basic",
  "max_results": 3
}
```

**Extraction rules:**
- Prefer the company's own website or LinkedIn "About" section.
- Extract: what the company does, approximate size/market, key differentiator.
- Do NOT include: financial projections, internal data, employee testimonials,
  review site content (Glassdoor, G2, etc.).
- If Tavily returns no usable result → fall back to Salesforce `Account.Description`
  if available. If that is also null → set `company_snapshot_plain: null`.

**Output field:** `company_snapshot_plain`

---

### Step 3 — Market signals fetch

**Goal:** Detect recent high-signal events that may affect the customer relationship
or create commercial opportunity.

Tavily query:
```json
{
  "query": "{account_name} {funding OR acquisition OR layoffs OR leadership change OR IPO} 2025 OR 2026",
  "search_depth": "basic",
  "max_results": 5
}
```

For each result, evaluate:
1. Does it clearly reference `{account_name}` (not a similarly named company)?
2. Is it from a credible public source (news outlet, press release, official blog)?
3. Is it within a relevant time window?

**Signal classification:**

| Signal Topic | Keywords to detect | Implication for CSM |
|---|---|---|
| `funding` | raised, Series A/B/C, investment, venture, seed round | Growth phase — expansion and headcount likely |
| `acquisition` | acquired, merger, takeover, M&A, merged with | Entity changes — confirm contract continuity |
| `layoffs` | layoffs, redundancies, workforce reduction, let go | Sensitivity required — pause expansion; assess risk |
| `leadership_change` | new CEO, new CHRO, appointed, joins as, named as | Re-establish relationship with new stakeholder |
| `ipo_readiness` | IPO, going public, S-1, listed on, stock market | Performance and compliance processes become priority |
| `other` | Any significant news not fitting above categories | Surface as context; CSM to interpret |

**Confidence assessment per signal:**

| Confidence | Condition |
|---|---|
| `high` | Direct, recent (≤ 90 days), exact company name match, reputable source |
| `medium` | Indirect reference, older (91–180 days), or secondary source |
| `low` | Weak inference, > 180 days old, or unverifiable |
| `unknown` | No signal found or company name too ambiguous to match reliably |

**Include in output:** Only signals with confidence ≥ `medium`.
**Suppress entirely:** When confidence = `low` or `unknown`.

---

### Step 4 — Layoffs suppression gate

If `signal_topics` contains `layoffs` AND confidence ≥ `medium`:

1. Set `layoffs_signal: true` in the output.
2. Notify downstream specialists via the output:
   `"⚠️ Layoffs signal detected — expansion brief suppressed. Approach commercial
   topics with sensitivity."`
3. The Expansion & Growth Specialist must check for this flag before producing output.

---

### Step 5 — Optional AI synthesis (Full 360 only, policy-gated)

When `output_mode = full_360` AND org policy permits AI-augmented web search:

Tavily query (deeper):
```json
{
  "query": "{account_name} business strategy HR technology trends {industry} 2026",
  "search_depth": "advanced",
  "max_results": 5
}
```

Synthesize a 2–3 sentence strategic context paragraph. Do not present as fact —
frame as: "Based on publicly available information..."

Set `ai_search_synthesis` field in output. Otherwise leave null.

---

### Step 6 — Assemble the external_intelligence block

Output structure (maps directly to `fetch_bundle.schema.json`):

```json
{
  "company_snapshot_plain": "Acme Corp is a mid-market logistics technology company headquartered in Amsterdam, serving over 300 enterprise clients across Europe and North America with fleet and supply chain management software.",
  "recent_signal_one_line": "Acme Corp raised a $40M Series C round in March 2026 to accelerate product expansion.",
  "signal_topics": ["funding"],
  "confidence": "high",
  "sources_are_public_only": true,
  "ai_search_synthesis": null
}
```

**Null case (no signal found):**
```json
{
  "company_snapshot_plain": "Acme Corp — no reliable public summary found. Fallback: {sf_description or null}",
  "recent_signal_one_line": null,
  "signal_topics": [],
  "confidence": "unknown",
  "sources_are_public_only": true,
  "ai_search_synthesis": null
}
```

When `recent_signal_one_line` is null → downstream Compose skills must omit the
external signals strip entirely. Do not show "no signals found" to the CSM.

---

### Signal implication lines (for Compose skills)

When a signal is present, append a one-line implication for the CSM brief.
These are suggestions — Compose skills may rephrase.

| Signal | Implication line |
|---|---|
| `funding` | "Recent funding suggests a growth phase — seat expansion and Workforce Planning may be timely." |
| `acquisition` | "M&A activity may affect the account structure — confirm entity mapping and contract continuity." |
| `layoffs` | "Recent workforce reduction detected — approach all commercial topics with sensitivity." |
| `leadership_change` | "New leadership in place — re-establish priorities and re-confirm the internal champion." |
| `ipo_readiness` | "IPO preparation often drives urgency around Performance, Compensation, and Compliance processes." |

---

### The Source Rule

This skill may only return content directly sourced from Tavily search results or
Salesforce `Account.Description`. It must never generate, infer, or hallucinate
company news or market signals. If no public data is found → return null fields.
The confidence field must always reflect the actual quality of evidence found.

---

## Resources

- **Tavily API**: Primary search tool. Requires `TAVILY_API_KEY`. Use `search_depth:
  "basic"` for snapshot/meeting_prep; `"advanced"` for full_360 only.
- **Salesforce `Account.Description`**: Fallback for company snapshot when Tavily
  returns no usable result. Fetched via Salesforce SOQL MCP tool.
- **`fetch_bundle.schema.json`**: Output must validate against the
  `external_intelligence` definition in this schema.
- **Output consumed by**: EBR / QBR & Executive Specialist, Expansion & Growth
  Specialist, Health Check Specialist, all Compose skills.
