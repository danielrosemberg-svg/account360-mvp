---
name: slack-drafter
description: >
  Formats and delivers the assembled Account 360 brief as a Slack message.
  Receives the composed output (Snapshot, Full 360, or Meeting Prep) and
  transforms it into a Slack-optimized format using Slack markdown — bold,
  bullets, dividers, and emoji signals. Applies strict length constraints per
  output mode to keep messages actionable and scannable. Routes the final message
  to the correct Slack channel or thread. Never adds information not present in
  the composed brief — this skill is a formatter and delivery mechanism only.
labels:
  - skill
  - slack
  - delivery
  - formatter
  - account360
---

## Context

**Activated when:** The Delivery Specialist routes to `slack_draft` in the pipeline,
or the CSM explicitly requests a Slack-ready output.

**Input:** The fully composed brief from one of:
- `Compose_Snapshot` → short-form Slack message
- `Compose_Full_360` → detailed Slack thread
- `Compose_Meeting_Prep_Brief` → structured pre-call Slack message

**Output:** A Slack-formatted string ready to post via the Slack API or copy-paste.

**Delivery targets (in priority order):**
1. DM to the requesting CSM (default)
2. Dedicated `#account-360` channel (if configured)
3. Existing account thread (if thread_ts is provided)

---

## Instructions

### Step 1 — Detect output mode and select template

Read `output_mode` from the routing packet.

| Output Mode | Slack format | Max length |
|---|---|---|
| `snapshot` | Single message, no thread | ~400 words / ~80 lines |
| `full_360` | Opening message + 2–3 thread replies | ~1200 words total |
| `meeting_prep` | Single structured message with sections | ~600 words |

---

### Step 2 — Slack markdown rules

Apply these formatting rules consistently across all output modes.

| Element | Slack syntax | When to use |
|---|---|---|
| Section heading | `*HEADING*` (bold) | Each major section |
| Sub-label | `_label:_` (italic) | Field labels inline |
| Bullet point | `•` or `-` | Lists of items |
| Risk badge | 🟢 🟡 🔴 🚨 | Health, risk, urgency signals |
| Divider | `---` | Between major sections |
| Inline code | `` `value` `` | API names, IDs (only in Full 360) |
| Mention | `<@USER_ID>` | When tagging CSM or RM is needed |

**Rules:**
- No H1/H2 markdown headers (`#`, `##`) — Slack does not render them.
- No tables — Slack does not render markdown tables. Use bullet lists instead.
- No HTML.
- Emoji signals (🟢 🟡 🔴 🚨) replace text-only risk labels for scannability.
- Keep sentences short — this is a messaging tool, not a document.

---

### Step 3 — Snapshot template

Use for `output_mode = snapshot`. Fits in a single Slack message.

```
*Account 360 Snapshot — {account_name}* 🏢
_{industry} · {country} · {segment}_
---
*💼 Commercial*
• ARR: {arr} · Renewal: {date} ({days} days · {quarter})
• Tenure: {tenure} years · Owner: {csm_name}

*📈 Adoption*
• {active}/{quoted} seats active ({pct}%) · Score: {score}/100
• Modules: {paying_modules_short}

*⚠️ Health & Risks*
• {badge} {risk_severity} — {risk_reason_short if present}
{• Open churn requests: {N} ⚠️ — if applicable}

*🌐 External*
• {company_snapshot_one_line}
{• Signal: {recent_signal_one_line} — if confidence ≥ medium}

*🤝 Last Touch*
• {N} days ago — {channel}: {summary_short}

*→ Next Step:* {strategic_next_step_one_line}
```

**Snapshot length rules:**
- Each section: max 3 bullets.
- Omit any section where ALL fields are null.
- `recent_signal` line: only show when `confidence ≥ medium`.
- Risk section: always show — even if just "🟢 No active risk signals."

---

### Step 4 — Full 360 template

Use for `output_mode = full_360`. Post as an opening message + thread replies.

**Opening message:**
```
*Account 360 Full Brief — {account_name}* 📋
_{industry} · {country} · {segment} · Tenure: {tenure} years_
*Overall Health:* {badge} {health_label}
_Full brief in thread below_ 🧵
```

**Thread reply 1 — Commercial + Customer Business:**
```
*💼 Commercial Overview*
• ARR: {arr} · ARPU: {arpu if available}
• Renewal: {date} ({days} days · {quarter})
• Contract: {start} → {end}
• Segment: {tier} · Employees: {quoted}
• CSM: {owner} · RM: {rm if present} · AM: {am if present}
{• Open deal: {stage} — {amount} — closes {date} — if present}

*🏢 Company Context*
{company_snapshot_plain — 2–3 sentences max}
{• Market signal: {recent_signal_one_line} [{signal_topics}] — if present}
```

**Thread reply 2 — Adoption + Risks:**
```
*📈 Adoption & Value*
• Active: {active}/{quoted} seats ({pct}%) · Score: {score}/100
• Modules owned: {paying_modules}
• Top usage: {top_module} ✅ · Low usage: {low_module} ⚠️
{• Value risk flag: adoption below threshold ⚠️ — if applicable}

*⚠️ Risks & Health*
• Sentiment: {sentiment} · Severity: {badge} {severity}
{• Risk: {risk_reason}}
{• ARR at risk: ${arr_at_risk}}
{• Modules at risk: {modules}}
{• Open churn requests: {N} 🚨}
{• Support tickets: {count} high/critical open cases}
```

**Thread reply 3 — Interaction Log + Next Steps:**
```
*🤝 Recent Touchpoints*
• {date} — {channel}: {summary} [{owner if different}]
• {date} — {channel}: {summary}
{• Key theme from last Gong call: "{highlight}" — if available}

*→ Strategic Next Steps*
1. {next_step_1}
2. {next_step_2}
{3. {next_step_3 if applicable}}
```

---

### Step 5 — Meeting Prep template

Use for `output_mode = meeting_prep`. Single structured message.

```
*🗓 Meeting Prep — {account_name}*
_{meeting_type} · {meeting_date_or_horizon if available}_
---
*🎯 Objective*
{objective_one_line}

*💼 Key Context*
• ARR: {arr} · Renewal: {date} ({days} days)
• Health: {badge} {health_label}
• Adoption: {pct}% · Last touch: {N} days ago

*📋 Suggested Agenda*
{1. agenda_item (N min)}
{2. agenda_item (N min)}
{3. agenda_item (N min)}

*❓ Questions to Validate*
• {question_1}
• {question_2}
• {question_3}

*🚫 Never Assume*
• {guardrail_1}
• {guardrail_2}

*→ Next Best Actions*
1. {nba_1}
2. {nba_2}
```

**Meeting Prep rules:**
- Agenda: max 5 items, include time allocations.
- Questions: max 4 bullets — most important only.
- Never Assume: max 3 bullets — hardest constraints only.
- Do not duplicate information already visible in Key Context.

---

### Step 6 — Language handling

Detect language from `routing_packet.language`.

| Language | Rule |
|---|---|
| `en` | Full English output |
| `he` | Translate all CSM-facing labels and section headings to Hebrew. Keep field values (ARR amounts, dates, account names) in their original language. Emoji signals remain unchanged. |

**Hebrew section headings reference:**

| English | Hebrew |
|---|---|
| Commercial Overview | סקירה מסחרית |
| Adoption & Value | אימוץ וערך |
| Risks & Health | סיכונים ובריאות |
| Company Context | הקשר חברה |
| Recent Touchpoints | אינטראקציות אחרונות |
| Strategic Next Steps | צעדים אסטרטגיים |
| Meeting Prep | הכנה לשיחה |
| Objective | מטרה |
| Suggested Agenda | סדר יום מוצע |
| Questions to Validate | שאלות לאימות |
| Never Assume | לא להניח |
| Next Best Actions | צעדים הבאים |

---

### Step 7 — Delivery routing

**Default:** Format as a string ready for copy-paste or API call.

**Slack API payload (when Slack integration is active):**
```json
{
  "channel": "{channel_id or user_id}",
  "text": "{opening_line}",
  "blocks": [
    {
      "type": "section",
      "text": { "type": "mrkdwn", "text": "{formatted_brief}" }
    }
  ]
}
```

**For Full 360 thread:**
Post the opening message first, capture `ts` (timestamp), then post each thread
reply with `"thread_ts": "{ts}"`.

**Channel routing logic:**

| Condition | Route to |
|---|---|
| CSM requested via DM | DM back to requesting user |
| `#account-360` channel exists in workspace | Post there with CSM @mention |
| Existing thread provided (`thread_ts`) | Reply in thread |
| No channel configured | Return formatted string only (copy-paste mode) |

---

### The Formatter Rule

This skill only formats and delivers — it does not add, infer, or expand on the
content it receives. If a section is missing from the composed brief, omit it from
the Slack message. Never fill gaps with guesses or generic filler text.

---

## Resources

- **Slack API** (optional): Requires `SLACK_BOT_TOKEN` and target channel/user ID.
  If not configured → output formatted string for manual copy-paste.
- **Input**: Composed brief from `Compose_Snapshot`, `Compose_Full_360`, or
  `Compose_Meeting_Prep_Brief`.
- **`output_modes.md`**: Reference for output mode shapes and intent.
- **Consumed by**: CSM (via DM or channel), `#account-360` Slack channel.
