# Output modes — Snapshot, Full 360, Meeting Prep

Use this file as ChatGPT Knowledge for **account360-intake-classifier** Step 5 (output_mode classification).

## snapshot

- **Intent:** Instant situational awareness before any deep work.
- **User phrases (examples):** "quick snapshot", "10 second view", "TL;DR", "what matters now", "pulse check".
- **Deliverable shape:** Ultra-short sections: identity, commercial line, adoption/risk pulse, risk strip, tiny external note, single last touch.
- **Does not include:** Full agenda, timed meeting plan, or exhaustive history.

## full_360

- **Intent:** Comprehensive account dossier for strategic work.
- **User phrases (examples):** "full 360", "everything you have", "deep dive", "full brief", "complete picture".
- **Deliverable shape:** All six sections expanded (customer business, commercial, growth & value, risks & health, interaction log, external intelligence) plus explicit sources/gaps.
- **Does not include:** Unless asked, avoid turning into a meeting run-of-show; stay analytic narrative.

## meeting_prep

- **Intent:** Prepare the CSM for a live conversation with objectives, agenda, and validation questions.
- **User phrases (examples):** "prep me for the call", "meeting tomorrow", "EBR prep", "renewal conversation", "escalation meeting", "agenda".
- **Deliverable shape:** Objective, desired outcome, timed agenda, customer validation questions, risks/opportunities grounded in data, 1–3 next best actions, prep-context traceability, never-assume checklist (via meeting-type matrix).
- **Requires:** Meeting type classification (Renewal_EBR, Adoption_Risk, Expansion, Onboarding_Escalation) when confident; otherwise escalate for human confirmation.

## Default when ambiguous

- If the user states an account Id but gives **no** mode hint: prefer **`meeting_prep`** when language implies an upcoming interaction within ~14 days; otherwise **`snapshot`** with `classification_confident: false` unless disambiguation is resolved.
- Always record `potential_ambiguity` when defaults fire.
