# Spec: `w0-assertion-nlp`

**Module id:** `w0-assertion-nlp` · **Wave:** 0 · **Owner:** clinical NLP
**Closes gaps:** 1, 2 · **Depends on:** — · **Blocks:** `w1-external-eval`
**Status:** not started

## Objective

**The system comprehends what the patient says, including what they deny.**

Today the symptom extractor is a set of regexes over body-system categories
with no notion of assertion. The live probe case:

```
"no fever, no cough, no chest pain"
```

extracts **fever, cough, and chest pain as present**. Every downstream
consumer inherits that error: DEMAT's initial belief, the risk models, the
retrieval query, and the severity assessment. This is the single largest
correctness defect in the system, and it is the stage-one failure the
research identifies.

The second, quieter defect: `TextPreprocessor.normalize_symptoms()` performs
a blind `str.replace` over a polarity map. The mapping `"no appetite" →
"decreased appetite"` fires on any occurrence, so "no appetite" becomes
"decreased appetite" — *creating* a symptom the patient denied. And
`STOP_WORDS` contains `"without"`, so "without fever" is silently reduced to
"fever" at the keyword stage.

**User story:** *As a patient, when I tell the system I do not have a symptom,
the system does not tell me I have it.*

## In scope

- `src/agents/nlp/agent.py` — assertion/negation layer; subject attribution
  (self / family / other / hypothetical); structured output carrying
  polarity.
- `src/data/preprocessing/text_preprocessor.py` — replace the blind polarity
  map with assertion-aware normalization; remove negation cues from
  `STOP_WORDS`.
- A new golden test harness and a 200-case authored test set.
- Optional: a distilled NegBERT checkpoint behind the same interface, gated
  by a settings flag and never required for the gate to pass.

## Out of scope

- Clinical entity linking and UMLS/SNOMED normalization — `w1-kb-v2`.
- Multilingual negation (Hinglish) — deferred; the dataset does not exist
  yet, see `FUTURE_IMPROVEMENTS.md`.
- Vision findings.
- The question bank's likelihood tables — `w2-ask-coverage`.

## Current state (verified)

`src/agents/nlp/agent.py`:

- `_extract_symptoms(text) -> list[dict]` at `:127` — iterates
  `SYMPTOM_PATTERNS` (9 body-system categories), `re.findall` over each, and
  returns `{"symptom": match, "category": category}`. No polarity, no
  subject, no span offsets.
- `SYMPTOM_PATTERNS` at `:26+` — category-keyed regex strings.
- `BODY_SYSTEMS` at `:39+` plus compiled `BODY_SYSTEM_PATTERNS` (added on
  the P0 branch) — word-boundary matching so "ear" cannot match inside
  "heart".
- `_try_load_biobert()` at `:63` — optional `dmis-lab/biobert-v1.1` token
  classification, off by default, falls back to pattern matching.

`src/data/preprocessing/text_preprocessor.py`:

- `normalize_symptoms(text)` at `:130` — iterates `SYMPTOM_CANONICAL` sorted
  by descending variant length and calls `text_lower.replace(variant,
  canonical)` unconditionally.
- `STOP_WORDS` at `:104+` — includes `"without"` alongside ordinary
  function words.
- `extract_keywords(text)` at `:139` — `clean` → `expand_abbreviations` →
  `normalize_symptoms` → regex word filter → stop-word removal.

`tests/unit/test_nlp_agent.py` — 70 lines, 10 tests, all positive-polarity.
There is no negation test anywhere in the suite.

## Requirements

**R1 — Negation is detected before symptom matching.** An assertion layer
must run before or during pattern matching and attach a polarity to every
extracted finding.

**R2 — The live probe case flips.** `"no fever, no cough, no chest pain"`
must yield zero present symptoms for fever, cough, and chest pain.

**R3 — Negation scope is local, not global.** A negation cue applies to the
clause it governs — the symptom phrase it precedes, or the symptom it
follows within the same clause — and must not cancel unrelated symptoms in a
later clause. `"no fever but I have a bad cough"` must yield fever absent,
cough present.

**R4 — Pre-negation cues and hedging are handled.** Cues include `no`,
`not`, `without`, `denies`, `never`, `free of`, `no history of`, `haven't`,
`doesn't`, `deny`, `denying`, `negative for`. Hedged or hypothetical mentions
("if I had a fever", "my mother had chest pain") must not be treated as
present self-reported symptoms.

**R5 — Subject attribution.** Every finding is attributed to a subject:
`self`, `family`, `other`, or `hypothetical`. Family-history findings are
excluded from the triage input but retained in the output for context. The
system already accepts `family_history` as a structured field, so this
alignment is natural.

**R6 — The polarity map is assertion-aware.** `normalize_symptoms()` must not
blindly rewrite "no appetite" into "decreased appetite". When a variant is
inside a negated scope, the normalized form must preserve the negation.

**R7 — Negation cues are removed from `STOP_WORDS`.** `"without"` and other
negation markers must not be discarded as noise before the assertion layer
sees them.

**R8 — The output contract is explicit and stable.** Each extracted symptom
becomes:

```python
{
    "symptom": "fever",
    "category": "constitutional",
    "polarity": "present" | "absent" | "hypothetical",
    "subject": "self" | "family" | "other" | "hypothetical",
    "certainty": "explicit" | "hedged",
    "span": (start, end),
}
```

`polarity`, `subject`, `certainty`, and `span` are additions to the existing
dict, not replacements — existing consumers that read `symptom` and
`category` keep working. Consumers that need "present and self-reported"
filter on `polarity == "present" and subject == "self"`.

**R9 — Downstream consumers filter correctly.** `compute_initial_belief()`
in `src/core/demat.py` and the rule-based synthesis in
`src/agents/rule_based_synthesis.py` must consume only present,
self-reported symptoms.

**R10 — The extractor has a deterministic default and an optional learned
path.** The rule-based assertion layer must be the default and must satisfy
the gate on its own. A distilled NegBERT path may be added behind a settings
flag (`enable_negation_model`, default off) and must improve, not replace,
the deterministic path.

## The golden harness — the release gate

`tests/unit/test_assertion_golden.py` with a 200-case set in
`tests/fixtures/assertion_golden.json`. Cases must be authored, not
generated, and must cover:

| Category | Cases | Example |
|---|---|---|
| Simple negation | 30 | "no fever" |
| Negation with conjunction | 20 | "no fever but a persistent cough" |
| Negation scope boundary | 20 | "no fever, I do have chest pain" |
| Pre-negation (symptom then cue) | 15 | "fever, no" |
| Hedged | 20 | "maybe a slight fever", "if I had a fever" |
| Family attribution | 25 | "my mother has diabetes" |
| Third-party attribution | 15 | "my brother has asthma" |
| Lay-language variants | 30 | "I am not running a temperature" |
| Multi-symptom mixed polarity | 25 | "no cough but shortness of breath" |
| Double negation | 5 | "not without a fever" |
| No-negation control | 20 | "I have a fever" |

**Gate:** ≥95% correct on polarity AND subject across all cases, with 100%
correct on the control set and on the live probe case. The golden set is
versioned and is the regression fence for every later change to the
extractor.

**Scoring.** A case is correct only if polarity and subject both match. A
case where the symptom is missed entirely counts as incorrect on polarity
(absent when it should be present).

## Acceptance criteria

- [ ] `"no fever, no cough, no chest pain"` yields zero present symptoms for
      all three, verified in a test.
- [ ] The golden harness reaches ≥95% overall, ≥100% on controls, ≥100% on
      the live probe case.
- [ ] `"no fever but I have a bad cough"` yields fever absent, cough present.
- [ ] `"my mother has diabetes"` attributes diabetes to `family`, and it does
      not appear in the triage belief.
- [ ] `"not without a fever"` is handled as a positive assertion (per the
      double-negation cases) — the outcome is recorded in the golden set with
      its reasoning, and the rule is documented.
- [ ] `normalize_symptoms("no appetite")` does not produce "decreased
      appetite" as a present symptom.
- [ ] `"without"` is no longer in `STOP_WORDS`.
- [ ] `compute_initial_belief()` reflects the filtered symptom set — verified
      by a test that asserts the belief for the probe case differs from the
      belief for the un-negated text.
- [ ] The full backend suite is green with no previously-passing test removed.
- [ ] No patient text appears in any log emitted by this module.

## Files in scope

| File | Change |
|---|---|
| `src/agents/nlp/agent.py` | Assertion layer; subject attribution; new output fields |
| `src/data/preprocessing/text_preprocessor.py` | Assertion-aware normalization; `STOP_WORDS` fix |
| `src/agents/nlp/assertion.py` | **NEW** — cue tables, scope resolver, polarity rules |
| `src/core/demat.py` | Filter to present + self in `compute_initial_belief` |
| `src/agents/rule_based_synthesis.py` | Same filter |
| `tests/unit/test_assertion_golden.py` | **NEW** — the gate |
| `tests/fixtures/assertion_golden.json` | **NEW** — 200 authored cases |
| `tests/unit/test_nlp_agent.py` | Extend for polarity and subject |
| `tests/unit/test_preprocessing.py` | Extend for the polarity-map fix |

## Design notes

**Rule-based first.** The research reports NegEx/ConText F = 0.936 and NegBERT
95.7% on i2b2 — but i2b2 is clinical text, and the target here is lay patient
language, where the failure mode is different. A rule-based scope resolver
covering the cue inventory above is predictable, inspectable, fast, has no
model dependency, and is what makes the golden set debuggable. A distilled
transformer can be added later behind a flag.

**Scope resolution.** A practical approach: split the text into clauses on
conjunctions and punctuation, then within each clause find negation cues and
the symptom spans they govern. Cue direction matters — a pre-verb negation
("no fever") and a post-verb one ("fever: no") are both common in patient
speech and both must be handled. Record the rule that decided each case in
the golden set so a failure points at a specific rule.

**Preserve the existing regex work.** The P0 branch fixed real bugs in
`SYMPTOM_PATTERNS` (`dizzin ess` → `dizziness`, `wheez[eio]+ing` →
`wheez(?:e|ing)`) and added word-boundary body-system matching. Keep all of
it. The assertion layer composes with the patterns; it does not replace them.

## Boundaries

- **Always:** keep the deterministic path as the default; preserve the P0
  branch's regex fixes; preserve the `{"symptom", "category"}` keys; keep
  patient text out of logs.
- **Ask first:** adding a model checkpoint to the repository or downloading
  one at runtime (size, licensing, and availability all need checking);
  changing the question bank's likelihood tables.
- **Never:** silently drop findings that the extractor cannot classify — an
  unresolved finding must be surfaced, not discarded; make the learned path
  mandatory; widen the scope of a negation cue across clause boundaries
  without an explicit test.

## Success criteria

The golden harness is ≥95%, the live probe case flips, and every downstream
consumer of the symptom list sees only present, self-reported symptoms.

## Open questions

1. **Double negation.** "not without a fever" is genuinely ambiguous in lay
   speech. The golden set will fix a convention (recommended: treat as a
   positive assertion, with the reasoning recorded) but it is a judgement
   call worth a clinical opinion.
2. **Speculative conditionals.** "If I had a fever I would..." — is this
   `hypothetical` or `absent`? Recommended: `hypothetical`, excluded from
   triage, and counted separately so the coverage metric can report it.
3. **Golden-set authorship.** 200 cases is a few hours of careful work for one
   person. Should a clinical advisor review them before the gate is
   considered authoritative? Recommended yes, even informally.
