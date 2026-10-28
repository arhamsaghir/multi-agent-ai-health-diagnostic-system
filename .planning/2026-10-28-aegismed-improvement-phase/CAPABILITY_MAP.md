# Capability Map: AegisMed Improvement Phase

**Created:** 2026-10-28 · **Status:** proposed — awaiting review
**Source:** `docs/research/public_release/12_GAP_ANALYSIS.md` (16 gaps),
`docs/research/public_release/13_ROADMAP.md` (4 gated waves)

This map is the index of what exists. Specs, plans, and downstream commands
select work by **module id**, never by guessing a filename. Module ids are
kebab-case, chosen once, and never renamed mid-initiative.

The request bundles several independently testable capabilities, so this phase
decomposes before specifying: each row below can be built, verified, and
merged on its own without rewriting the others' requirements.

## Modules

| Module id | Responsibility | Depends on | Wave | Gaps closed |
|---|---|---|---|---|
| `w0-truthful-frontend` | No code path renders a diagnosis without a backend response; explicit error and escalation states | — | 0 | 11 |
| `w0-assertion-nlp` | Negation/assertion handling, subject attribution, polarity fix in the NLP stage | — | 0 | 1, 2 |
| `w0-red-flag-engine` | Structured tiered red-flag engine replacing keyword matching; out-of-scope refusal | — | 0 | 5 |
| `w0-benchmark-honesty` | Retire the circular benchmark as an accuracy claim; keep it as a regression smoke test | — | 0 | 7 (partial) |
| `publication-truth` | Remove the 98% circular claim from the paper, patent spec, and docs; re-scope claims to what the code can defend | `w0-benchmark-honesty` | 0–1 | 7, 16 (partial) |
| `w1-external-eval` | External vignette harness with bootstrap CIs; emergency sensitivity, ask-coverage, ECE on held-out data | `w0-assertion-nlp`, `w0-red-flag-engine` | 1 | 7 |
| `w1-conformal` | Split-conformal (APS/RAPS) bands over triage outputs, calibrated **before** agreement blending | `w1-external-eval` | 1 | 6 |
| `w1-kb-v2` | ICD-11/SNOMED-coded knowledge base, 150 conditions, clinician-reviewed red flags, PD-source citations | — | 1 | 3, 4 |
| `w2-hybrid-rag` | BM25 + FAISS hybrid retrieval with RRF; per-claim citation enforcement; PD-licensed corpus | `w1-kb-v2` | 2 | 8 |
| `w2-schema-synthesis` | Schema-constrained generation; labeled degradation on failure; LLM cannot widen the triage band | `w1-conformal` | 2 | 9 |
| `w2-orchestration` | Verification/critic node before delivery; adaptive solo-vs-team depth | `w0-red-flag-engine`, `w2-hybrid-rag` | 2 | 10 |
| `w2-ask-coverage` | Instrument and publish red-flag ask-coverage as the measured differentiator | `w0-red-flag-engine`, `w1-kb-v2` | 2 | 4 |
| `w3-dpdp` | Consent flows, verifiable parental consent, encryption at rest, audit trail, retention, export/delete | `w3-engineering` | 3 | 13 |
| `w3-regulatory` | CDSCO SaMD classification support; product-language audit ("assessment/triage", not "diagnosis"); app-store compliance | `w0-truthful-frontend` | 3 | 12 |
| `w3-abdm` | Map FHIR R4 output to the NRCeS ABDM IG; M1 sandbox milestone | `w1-kb-v2`, `w3-dpdp` | 3 | 12 (partial) |
| `w3-patent` | Professional prior-art search; re-scope claims to the defensible contract | `publication-truth`, `w1-conformal` | 3 | 16 |
| `w3-engineering` | CI on every PR; split `diagnosis.py`; frontend test suite; local LLM fallback benchmark | — | 3 | 15 |

## Build order

```
Wave 0 ────────────────────────────────────────────────────────────
  w0-benchmark-honesty ──┐
  w0-truthful-frontend ──┼──► publication-truth (phase A: retract claims)
  w0-assertion-nlp ──────┤
  w0-red-flag-engine ────┘

Wave 1 ────────────────────────────────────────────────────────────
  w1-kb-v2 ──────────────────────────────────┐
  w0-assertion-nlp + w0-red-flag-engine ───► ├──► w1-external-eval ──► w1-conformal
                                             │                            │
                                             └────────────────────────────┘
                                                          │
                                                          ▼
                                              publication-truth (phase B: replace numbers)

Wave 2 ────────────────────────────────────────────────────────────
  w1-kb-v2 ──► w2-hybrid-rag ──┐
  w0-red-flag-engine ───────────┼──► w2-orchestration
  w1-conformal ──► w2-schema-synthesis ─┘

  w0-red-flag-engine + w1-kb-v2 ──► w2-ask-coverage

Wave 3 ────────────────────────────────────────────────────────────
  w3-engineering ──► w3-dpdp ──┐
  w1-kb-v2 + w3-dpdp ──────────┼──► w3-abdm
  w0-truthful-frontend ────────┴──► w3-regulatory
  publication-truth + w1-conformal ──► w3-patent
```

## Dependency rationale

**Why `publication-truth` starts before Wave 1.** The 98% figure is in the
paper's abstract, the results table, the analysis, and the conclusion. It is
also a load-bearing input to the patent filing decision. Retracting it is a
small edit; doing it after new numbers exist risks re-litigating the same
sentence. The module has two phases: **A** retract and re-scope the claims
(needs only `w0-benchmark-honesty`), **B** insert replacement numbers measured
by `w1-external-eval` and `w1-conformal`.

**Why `w1-conformal` depends on `w1-external-eval`.** Calibration requires a
held-out calibration set. Calibrating on the same self-generated cases that
produced the 98% number would launder the circularity rather than fix it. The
research is explicit that conformance breaks under exactly AegisMed's
architecture — agreement blending must be conformalized *before* blending, and
the guarantee only means something on external data.

**Why `w1-kb-v2` has no upstream dependency.** KB v2 is content work with a
code component, and it is the input to three later modules (`w2-hybrid-rag`
corpus, `w2-ask-coverage` red-flag criteria, `w3-abdm` coding). Starting it
early unblocks the most downstream work in the phase.

**Why `w3-engineering` depends on nothing but gates everything.** CI, the
`diagnosis.py` split, the frontend test suite, and the local LLM fallback are
independently testable and can start at any time. The roadmap schedules them
in Wave 3 because they are hardening, but **the CI portion should be pulled
forward into Wave 0** — see the deviation note below.

**Why `w2-orchestration` waits for both `w0-red-flag-engine` and
`w2-hybrid-rag`.** The critic node checks three things: red-flag presence
(needs the structured engine), citation coverage (needs enforced citations),
and severity consistency (needs the conformal band). Building it before any of
those means building it twice.

## Deliberate deviations from the research roadmap

| Deviation | Rationale |
|---|---|
| CI moved from Wave 3 into Wave 0 | The roadmap calls CI "a regression fence." A fence built in Wave 3 protects none of Waves 0–2. Split `w3-engineering` into `w3-engineering` (deferred) and a Wave-0 `ci-foundation` task (immediate). |
| `publication-truth` added as its own module | It is not in the roadmap at all, but it gates the patent filing and the paper submission, and it is a release-gate item ("no self-referential numbers anywhere in docs"). The roadmap's own release gate implies it. |
| `w0-benchmark-honesty` separated from `w1-external-eval` | Retiring a bad claim and building a good measurement are independently shippable. The first is a few hours; the second is weeks. Bundling them would delay the retraction. |
| `w3-abdm` added as a module | The roadmap lists ABDM only as a Wave 3 bullet with no acceptance gate. It has a concrete external milestone (M1 sandbox) and deserves its own spec. |
| `w2-schema-synthesis` split out from `w2-hybrid-rag` | Gap analysis treats them as separate rows (8 and 9) with different consumers. Citation enforcement is a retrieval concern; schema-constrained generation is a synthesis concern. |
| `w3-regulatory` separated from `w3-dpdp` | One is a code change with a compliance gate; the other is a legal engagement with a classification gate. Different owners, different clocks, different evidence. |

## Waves and their gates

| Wave | Goal | Gate (all must hold to advance) |
|---|---|---|
| 0 | Stop the bleeding | No code path renders a diagnosis without a backend response; the live negation probe case flips; 100% emergency-flagging on the gold adversarial set; out-of-scope refusal works; no self-referential number remains in the paper |
| 1 | Measure honestly | External top-1/top-3 with bootstrap CIs published in-repo; empirical conformal coverage within ±2pp of nominal on external data; every KB condition carries an ICD-11 code and ≥1 PD-source citation |
| 2 | Become advanced | Every recommendation carries a source ID; the LLM provably cannot widen the triage band; the critic node blocks unsafe deliveries; ask-coverage is measured and above the 36.9% field benchmark |
| 3 | Make it lawful and durable | DPDP consent and security controls implemented; counsel sign-off recorded; ABDM M1 milestone reached; patent claims re-scoped and prior-art search filed; CI green on every PR |

Wave gates are **not** "all tasks checked off." A wave advances when its gate
is satisfied by evidence, and the evidence is linked from
`PROGRESS_TRACKER.md`.

## Module ownership

Single-owner-per-module. Every module has one accountable owner and optional
contributors.

| Module id | Owner | Accountable for |
|---|---|---|
| `w0-truthful-frontend` | frontend | No fabricated output path |
| `w0-assertion-nlp` | clinical NLP | Comprehension correctness |
| `w0-red-flag-engine` | safety | Escalation correctness |
| `w0-benchmark-honesty` | evaluation | Measurement honesty |
| `publication-truth` | principal investigator | What the project claims |
| `w1-external-eval` | evaluation | External numbers |
| `w1-conformal` | uncertainty | Coverage guarantees |
| `w1-kb-v2` | clinical content | Knowledge base quality |
| `w2-hybrid-rag` | retrieval | Grounding |
| `w2-schema-synthesis` | synthesis | Output contract |
| `w2-orchestration` | architecture | Delivery safety |
| `w2-ask-coverage` | evaluation | The measured differentiator |
| `w3-dpdp` | compliance | Lawful data handling |
| `w3-regulatory` | regulatory | Classification and positioning |
| `w3-abdm` | interoperability | National integration |
| `w3-patent` | IP | Defensible claims |
| `w3-engineering` | platform | Regression fence |

## Open questions for this map

1. **`publication-truth` phase A scope.** Retracting the 98% claim from the
   paper means either removing the accuracy result entirely or restating the
   contribution as the *triage mechanism* rather than its accuracy. The second
   is stronger and is what the research's "one-paragraph strategy" implies, but
   it is a rewrite of the paper's thesis, not a number edit. **Decision
   needed from the principal investigator before execution.**
2. **KB v2 authoring capacity.** 150 clinician-reviewed conditions with
   red-flag criteria and citations is clinical-content work, not engineering.
   Whether that is done in-house, with a clinical advisor, or by recruiting
   reviewers changes the Wave 1 critical path by weeks. **Decision needed.**
3. **`w1-external-eval` scoring model.** DxBench supplies three candidate
   diseases per case. Whether AegisMed is scored open-ended (the harder, more
   honest setting at 44.2% best-model accuracy) or in the 3-candidate setting
   (62.5%) changes the headline number substantially. The recommendation is to
   report **both**, with the open-ended number as the headline.
4. **CI provider.** GitHub Actions is the default assumption. The repo has no
   `.github/workflows/` directory today, so this is a greenfield choice.
