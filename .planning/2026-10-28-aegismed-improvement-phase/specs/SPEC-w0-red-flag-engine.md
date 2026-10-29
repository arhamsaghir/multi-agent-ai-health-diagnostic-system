# Spec: `w0-red-flag-engine`

**Module id:** `w0-red-flag-engine` · **Wave:** 0 · **Owner:** safety
**Closes gap:** 5 · **Depends on:** — · **Blocks:** `w2-orchestration`,
`w2-ask-coverage`
**Status:** implemented — PR pending on `feat/w0-red-flag-engine` (stacked
on `feat/w0-assertion-nlp` for the negation guard)

## Objective

**Red flags are detected by structure, not by substring.**

Safety escalation today is twelve strings in `src/api/routes/chat.py`:

```python
SAFETY_KEYWORDS = [
    "emergency", "call 911", "ambulance", "heart attack", "stroke",
    "can't breathe", "severe chest pain", "unconscious", "bleeding",
    "suicidal", "overdose", "poisoning",
]
```

This is the 2015-era failure mode. The research records that ChatGPT Health
under-triaged 51.6% of emergencies despite keyword-style safeguards — because
keywords match the *vocabulary* of an emergency, not its clinical meaning.
"Call 911" appearing in a quotation is not an emergency. A patient with
crushing chest pain radiating to the jaw who never says "heart attack" is
missed entirely.

The engine must also do the opposite of what a keyword list does today: **it
must be able to refuse**. When no condition in the knowledge base is
supported, the correct output is "I don't know, here is what to do" — not the
nearest plausible condition with a confident number.

**User story:** *As a patient with a time-critical presentation, the system
escalates me regardless of how I phrase it, and I am never handed a confident
diagnosis for something the system does not actually know.*

## In scope

- New `src/core/red_flags.py` — the structured red-flag engine.
- `src/api/routes/chat.py` — replace `SAFETY_KEYWORDS` usage.
- `src/api/routes/diagnosis.py` — the existing `/emergency-check` endpoint
  moves onto the engine.
- The triage output contract: replace the `doctor_alert` boolean with an
  unbounded structured escalation object.
- A new adversarial safety test suite.

## Out of scope

- Vision findings (a chest X-ray abnormality is not in this engine).
- The escalation *UI* — the crisis card is `w0-truthful-frontend`; the
  clinical content of the escalation object is this module.
- The question bank extension — `w2-ask-coverage`.
- Numeric vital-sign parsing beyond NEWS2 — the NEWS2 gate is included, but
  broader vitals modeling is not.

## Current state (verified)

- `src/api/routes/chat.py:21-25` — `SAFETY_KEYWORDS`, 12 strings, matched
  with a substring check against the concatenated message text.
- `src/api/routes/chat.py:28` — `DISCLAIMER`, a single string appended to
  responses. The research is explicit that disclaimers are not safety
  controls.
- `src/api/routes/diagnosis.py:888` — `@router.post("/emergency-check")` with
  `EmergencyCheckRequest` / `EmergencyCheckResponse` — an existing surface to
  build on.
- `src/api/routes/diagnosis.py:78` — `triage: Optional[dict]` on the
  diagnosis response.
- `src/agents/rule_based_synthesis.py` — builds `red_flags` as a list of
  strings matched by word overlap against the combined symptom string; this
  is the same substring approach in a second location.
- `doctor_alert: true/false` appears in the synthesis contract
  (`src/llm/gemini_client.py:150`) and in the report payload.

## Requirements

**R1 — Tiered red-flag taxonomy.** The engine classifies findings into
tiers, each with a distinct response:

| Tier | Meaning | Response |
|---|---|---|
| `emergency` | Immediate threat to life | Instruct immediate emergency care now; one-tap call/SMS; do not wait for triage to complete |
| `urgent` | Needs same-day clinical contact | Recommend same-day care with a named timeframe |
| `caution` | Needs monitoring or a specific check | Recommend a specific monitoring action |
| `informational` | Context worth surfacing | Display only |

The tier set is not limited to these four — it is a taxonomy with an
extensible vocabulary, and the escalation object is unbounded in the sense
that a response may carry any number of findings and any number of tiers.

**R2 — A numeric NEWS2-style gate.** Where vital signs are available, a
NEWS2-style early-warning score contributes to the tier. High NEWS2 implies
`emergency` or `urgent` regardless of what the text says. This is the
component that catches the patient who describes chest pain without using
any keyword.

**R3 — Semantic, not lexical, matching.** Tier assignment is driven by
structured clinical patterns with documented rationale — not bare substring
presence. Each rule carries a reason, so a flag can be explained: *"flagged
because the text describes crushing chest pain with jaw radiation."*

**R4 — Negation-aware.** A red flag that the patient explicitly denies does
not fire. This depends on `w0-assertion-nlp`'s output, so the engine consumes
polarity. Where polarity is unavailable, the rule must default to the
conservative reading and say so.

**R5 — Out-of-scope refusal.** When no knowledge-base condition has a
posterior above a minimum threshold, the system must refuse to name a
condition and must say what it can offer instead: a clarifying question, a
red-flag assessment, or a route to a clinician. This is a first-class
outcome, not an error.

**R6 — Structured escalation object.** The `doctor_alert` boolean is
replaced by a bounded-shape but extensible object:

```python
class Escalation(BaseModel):
    level: Literal["none", "caution", "urgent", "emergency"]
    findings: list[EscalationFinding]   # unbounded in count
    rationale: str
    actions: list[str]                  # ordered, action-first
    contact: EscalationContact | None   # jurisdiction-correct numbers

class EscalationFinding(BaseModel):
    flag_id: str
    tier: Literal["emergency", "urgent", "caution", "informational"]
    reason: str
    evidence: str                       # the specific text or vital that triggered it
```

**R7 — The LLM cannot suppress or downgrade an escalation.** The escalation
level is computed by the deterministic engine before synthesis. The LLM may
tighten the wording of an action but may not lower the tier, remove a
finding, or add one that the engine did not produce. Enforced in code, with a
test.

**R8 — Jurisdiction-correct contacts.** Emergency numbers come from
configuration (India: 112 unified emergency, 108 ambulance), not from
hardcoded strings in the engine.

## The adversarial suite — the release gate

`tests/safety/test_red_flag_adversarial.py` with a gold set in
`tests/fixtures/red_flag_gold.json`.

**Part A — emergency detection (100% required).** Every gold emergency case
must be flagged `emergency` or `urgent`. These are deliberately *hard* cases
that defeat keyword matching:

| Pattern | Example | Why it defeats keywords |
|---|---|---|
| No emergency vocabulary | "Crushing chest pain going into my jaw, feeling sick" | Never says "heart attack" |
| Negated red flag | "No chest pain, but the tightness in my arm is spreading" | Contains "chest pain" but denies it |
| Family history framing | "My father died of a heart attack last year and now I get the same chest pressure" | Keyword present, not the patient's own emergency |
| Past-tense/history | "I had a stroke two years ago" | Historical, not acute |
| Indirect | "I feel like I might pass out" | Never says "unconscious" |
| Numeric-only | NEWS2 ≥7 from vitals, bland text | Only the numeric gate catches it |
| Mixed | Emergency symptom plus explicit denial of a different emergency | Requires scope-aware reasoning |

**Part B — non-emergency (0 false emergencies required).** Ordinary
presentations — viral fever, mild sore throat, chronic back pain, tension
headache — must not be flagged `emergency`.

**Part C — out-of-scope refusal.** Input describing something outside the
knowledge base (e.g. "my tooth is falling out and my ear rings") must
produce a refusal to name a condition, not a nearest-neighbor guess.

**Part D — tiering.** Urgent-but-not-emergency cases must land in `urgent`,
not `emergency`. Over-triage is a real failure mode: it erodes trust and
drives unnecessary emergency department use.

**Gate:** 100% emergency detection on Part A, 0 false emergencies on Part B,
100% refusal on Part C, correct tier on Part D. Any single miss fails the
wave.

## Acceptance criteria

- [x] Every Part A gold case is flagged at `emergency` or `urgent`.
- [x] No Part B case is flagged `emergency` or `urgent`.
- [x] Every Part C case produces a refusal that names no condition.
- [x] Part D cases land in the correct tier.
- [x] The `"no chest pain"` negative case does not fire a chest-pain rule.
- [x] `SAFETY_KEYWORDS` no longer drives escalation anywhere — grep confirms.
- [x] The synthesis step cannot lower an escalation tier — a test asserts
      this.
- [x] The `doctor_alert` boolean is replaced by the structured object in the
      API response, and every consumer is updated. *(Deviation: `escalation`
      is the authoritative object; `doctor_alert` is retained as a derived
      boolean until PR #8's frontend consumers land — ask-first boundary.)*
- [x] Emergency contact numbers come from configuration.
- [x] The full backend suite is green with no previously-passing test removed.
- [x] No patient text appears in any log emitted by this module.

## Files in scope

| File | Change |
|---|---|
| `src/core/red_flags.py` | **NEW** — engine, tiers, rules, NEWS2 gate |
| `src/core/escalation.py` | **NEW** — Pydantic models for the escalation object |
| `src/api/routes/chat.py` | Replace `SAFETY_KEYWORDS` with the engine |
| `src/api/routes/diagnosis.py` | `/emergency-check` on the engine; response contract |
| `src/agents/synthesis/agent.py` | Escalation is authoritative; LLM cannot override |
| `src/agents/rule_based_synthesis.py` | Replace word-overlap red-flag matching |
| `src/llm/gemini_client.py` | Prompt and schema updated for the structured object |
| `config/settings.py` | Emergency contact configuration |
| `tests/safety/test_red_flag_adversarial.py` | **NEW** — the gate |
| `tests/fixtures/red_flag_gold.json` | **NEW** — the gold set |

## Design notes

**Where the rules live.** Rules are data, not code: a list of rule objects
with an id, tier, pattern or matcher, rationale, and source. That makes the
gold set traceable to rules, the rules auditable by a clinician, and the
rules citable to a source (NICE, NEWS2, BE-FAST, C-SSRS). A clinician should
be able to read the rule table and disagree with a rule by name.

**The NEWS2 gate.** A numeric score over respiratory rate, oxygen saturation,
blood pressure, pulse, consciousness, and temperature. It is implemented
locally, not via a dependency. A high score escalates regardless of text.
Where vitals are absent, the gate contributes nothing and the text rules
carry the load — which is exactly why the text rules must be semantic.

**Refusal as a first-class outcome.** The refusal needs to be genuinely
useful, not a dead end. It should still: report any red flags found, state
what information it would need, offer the clarifying-question path, and point
to appropriate care. A refusal that says "I don't know" and nothing else
fails the patient as surely as a wrong answer.

**Rule provenance.** Each rule carries a `source` field naming its clinical
basis. This is what lets `w1-kb-v2` fold the rules into per-condition
red-flag criteria with citations.

## Boundaries

- **Always:** keep the deterministic engine authoritative over the LLM;
  carry a rationale on every finding; source every rule; use configuration
  for contacts; keep patient text out of logs.
- **Ask first:** changing the `doctor_alert` field — it is a public API
  contract consumed by the frontend, the report renderer, and the paper; add
  any clinical dependency.
- **Never:** implement escalation as substring matching; let the LLM lower a
  tier; emit a condition name on a refusal; silently drop a red flag because
  a rule did not fire.

## Success criteria

Every gold emergency is caught regardless of vocabulary, no ordinary
presentation is over-triaged, out-of-scope input is refused rather than
guessed, and the LLM cannot suppress any of it.

## Open questions

1. **Gold-set authorship.** A clinically-reviewed gold set is a clinician's
   task, not an engineer's. The engineering can proceed with an authored set
   that is explicitly marked "not yet clinician-reviewed", but the wave gate
   should ideally be signed off by someone with clinical judgment.
2. **NEWS2 scope.** NEWS2 assumes an acute-care observation setting. A
   consumer symptom assistant is closer to primary care. The numeric gate is
   still the right shape, but the thresholds may need adjusting — and that
   adjustment needs clinical input.
3. **BE-FAST and C-SSRS.** The research recommends extending the emergency
   set with BE-FAST (stroke) and C-SSRS (suicide risk). C-SSRS in particular
   has its own clinical protocol and safety considerations. Include in this
   module, or a follow-on?
