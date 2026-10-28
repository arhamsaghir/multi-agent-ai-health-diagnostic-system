# Roadmap — AegisMed to Public Release

Sequenced from `12_GAP_ANALYSIS.md`. Each wave ends at a gate; do not start a
wave before the previous gate passes. Effort estimates assume the current
codebase and one developer + agents.

## Wave 0 — Stop the bleeding (1–2 weeks) 🔴

*Goal: nothing the system says can be silently wrong.*

1. **Kill the fabricated fallback** — remove `getDemoResults` from the live
   error path in `frontend/src/lib/api.ts`; explicit error states everywhere.
   *Gate: no code path renders a diagnosis without a backend response.*
2. **Assertion/negation layer** in `src/agents/nlp/agent.py` (NegEx/ConText
   port or distilled NegBERT), attribute findings to subject (self/family),
   fix the blind-replace polarity map in `text_preprocessor.py`.
   *Gate: golden harness (`tests/unit/test_nlp_agent.py`) passes ≥95% on a
   200-case negation/lay-language set — the live probe case must flip.*
3. **Structured red-flag engine v0** (`src/core/red_flags.py`): NEWS2-style
   numeric gate + emergency keyword tiers replacing `SAFETY_KEYWORDS`;
   out-of-scope refusal when no KB condition exceeds a minimum posterior.
   *Gate: adversarial suite (ambiguous emergency vignettes) → 100%
   emergency-flagging on the gold set; refusal works on out-of-KB input.*
4. **Retire the circular benchmark** — mark `demat_benchmark.py`
   self-generated cases as invalid for accuracy claims; keep only as a
   regression smoke test.

## Wave 1 — Measure honestly (2–4 weeks) 🔴/🟡

*Goal: real numbers with error bars.*

5. **External vignette harness** — adopt the DxBench protocol (1,148 real
   dialogue cases, 461 diseases) + gretelai/symptom_to_diagnosis for the NLP
   stage; report top-1/top-3, **emergency-case sensitivity**, red-flag
   ask-coverage, ECE — all with bootstrap CIs (n≥323 minimum).
6. **Conformal calibration** — split-conformal (APS/RAPS) over triage outputs,
   calibrated on held-out external vignettes; apply **before** any agreement
   blending; replace the confidence percentage with set size + band.
   *Gate: empirical coverage within ±2pp of nominal on external data.*
7. **KB v2** — ICD-11/SNOMED-coded knowledge base (start 150 conditions:
   top primary-care presentations for India), red-flag criteria per condition
   from NICE/WHO/CDC PD sources; WHO text removed from the corpus.
   *Gate: every condition entry carries ICD-11 code + ≥1 PD-source citation.*

## Wave 2 — Become advanced (4–8 weeks) 🟡

8. **Hybrid RAG + citation enforcement** — BM25+FAISS with RRF
   (`src/agents/rag/agent.py`); synthesis schema-constrained
   (`openrouter_client.py` structured outputs), every recommendation carries a
   source ID; LLM can tighten language but never widen the triage band.
9. **Adaptive depth + verification node** — MDAgents-style solo fast-path when
   DEMAT entropy collapses early; full team when it doesn't; critic node
   checks red-flag presence, citation coverage, severity consistency before
   delivery (LangGraph node in `orchestrator/agent.py`).
10. **Report-quality LLM-judge harness** — HealthBench-style weighted rubric
    (safety, grounding, actionability, calibration) in `scripts/benchmark/`,
    calibrated against a small physician-graded sample.
11. **Measured differentiator: red-flag ask coverage** — DEMAT asks by design;
    the field scores 36.9%. Instrument it, publish it, put it in the paper
    and the patent.

## Wave 3 — Make it lawful and durable (6–10 weeks) 🔴/🟢

12. **DPDP compliance** — consent flows + verifiable parental consent,
    encryption at rest (Postgres + field-level), audit trail, retention
    policy, data-export/delete. *Gate: compliance checklist signed ~Q1 2027
    (statutory deadline 13 May 2027).*
13. **Regulatory counsel engagement (India)** — CDSCO SaMD classification
    under the Oct-2025 MDSW guidance (expect Class B–C); product language
    audit ("assessment/triage", never "diagnosis"; Telemedicine clause 2.8);
    app-store policy compliance.
14. **ABDM sandbox integration** — map existing FHIR R4 output to the NRCeS
    ABDM IG; work through M1 milestone in the sandbox.
15. **Patent actions** — professional prior-art search (CPC G16H50/20 +
    recipe in `11`); re-scope claims to the deterministic bounded-bank +
    conformal-before-agreement + safety-band contract; cite JAMIA 2026
    proactively; check Babylon IP disposition in the USPTO assignment DB.
16. **Engineering hardening** — CI on every PR (pytest, tsc, build); split
    `diagnosis.py` into domain routers; frontend test suite; local LLM
    fallback benchmark (BioMistral/MedGemma-4B quantized on the CPU container).

## Release gate (all must hold)

- [ ] Emergency vignette sensitivity ≥ nurse baseline gap closure plan;
      zero under-triaged gold emergencies on the adversarial suite
- [ ] External top-1/top-3 with CIs published in-repo (no self-referential
      numbers anywhere in docs)
- [ ] Calibration: conformal coverage within tolerance; ECE reported
- [ ] Red-flag ask-coverage measured and above the 36.9% field benchmark
- [ ] Zero fabricated-output paths (frontend + backend)
- [ ] DPDP consent + security controls implemented
- [ ] Counsel sign-off on positioning and classification
- [ ] Patent claims re-scoped + prior-art search filed

## The one-paragraph strategy

The field's honest frontier is 34–62% top-1 with under-triage as its
characteristic failure; the winning 2026 architecture is a deterministic,
certified triage core with an LLM conversation layer on top. AegisMed already
owns the rare part — an entropy-driven engine whose whole purpose is to *ask*
— in a market where the leaders fail at asking (36.9%). Fix comprehension,
measure on external vignettes, calibrate with conformal sets before agreement,
ground every sentence in free terminologies, and wrap the product in India's
consent/ABDM machinery. That combination — measured asking, bounded LLM, and
lawful data plumbing — is both the public release and the defensible patent.
