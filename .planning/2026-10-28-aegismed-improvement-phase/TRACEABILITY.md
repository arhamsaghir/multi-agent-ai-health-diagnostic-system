# Traceability Matrix

**Created:** 2026-10-28 · **Status:** live — update on every task completion
**Authority:** `docs/research/public_release/12_GAP_ANALYSIS.md` (16 gaps)

Every gap the research identified maps to a module, a task, a verification
command, and a gate. Nothing in the gap analysis may be dropped silently; a
gap is closed only when its test passes and its evidence is linked.

**Status key:** `not started` · `in progress` · `blocked` · `verified` ·
`deferred` (with a reason and a re-entry condition)

## Gap-to-module map

| Gap | Component | Module id | Spec | Primary test | Status |
|---|---|---|---|---|---|
| 1 | `src/agents/nlp/agent.py` — no negation | `w0-assertion-nlp` | `specs/SPEC-w0-assertion-nlp.md` | `tests/unit/test_assertion_golden.py` | not started |
| 2 | `src/data/preprocessing/text_preprocessor.py` — blind polarity map | `w0-assertion-nlp` | `specs/SPEC-w0-assertion-nlp.md` | `tests/unit/test_preprocessing.py` | not started |
| 3 | `src/core/disease_kb.py` — 15 conditions, string keys | `w1-kb-v2` | `specs/SPEC-w1-kb-v2.md` | `tests/unit/test_kb_v2.py` | not started |
| 4 | `src/core/demat.py`, `question_bank.py` — no ask-coverage metric | `w2-ask-coverage` | `specs/SPEC-w2-ask-coverage.md` | `tests/unit/test_ask_coverage.py` | not started |
| 5 | `src/api/routes/chat.py` — 12 keyword strings | `w0-red-flag-engine` | `specs/SPEC-w0-red-flag-engine.md` | `tests/safety/test_red_flag_adversarial.py` | not started |
| 6 | `src/agents/confidence_scorer.py` — ECE 0.245, blend before calibration | `w1-conformal` | `specs/SPEC-w1-conformal.md` | `tests/unit/test_conformal.py` | not started |
| 7 | `scripts/benchmark/` — circular, oracle = system under test | `w0-benchmark-honesty` + `w1-external-eval` | both specs | `tests/unit/test_demat_benchmark.py` (demoted) + `scripts/benchmark/external_eval.py` | w0-benchmark-honesty + publication-truth phase A: implemented, PRs pending · w1-external-eval: not started |
| 8 | `src/agents/rag/agent.py` — dense-only FAISS, WHO NC text | `w2-hybrid-rag` | `specs/SPEC-w2-hybrid-rag.md` | `tests/unit/test_rag_agent.py` | not started |
| 9 | `src/agents/synthesis/agent.py` — free-form JSON parse | `w2-schema-synthesis` | `specs/SPEC-w2-schema-synthesis.md` | `tests/unit/test_synthesis_fallback.py` | not started |
| 10 | `src/agents/orchestrator/agent.py` — no verification node | `w2-orchestration` | `specs/SPEC-w2-orchestration.md` | `tests/unit/test_orchestrator_critic.py` | not started |
| 11 | `frontend/src/lib/api.ts` — fabricates demo diagnoses | `w0-truthful-frontend` | `specs/SPEC-w0-truthful-frontend.md` | `frontend/src/lib/api.test.ts` | not started |
| 12 | Product-wide — no regulatory posture | `w3-regulatory` + `w3-abdm` | both specs | `tests/unit/test_product_language.py` | not started |
| 13 | `src/data/database/` — SQLite, plaintext at rest | `w3-dpdp` | `specs/SPEC-w3-dpdp.md` | `tests/unit/test_dpdp_controls.py` | not started |
| 14 | `src/llm/openrouter_client.py` — 503-prone, off-box PHI path | `w3-engineering` | `specs/SPEC-w3-engineering.md` | `tests/unit/test_local_fallback.py` | not started |
| 15 | CI, tests — zero CI, zero frontend tests, `diagnosis.py` 5 domains | `w3-engineering` (+ `ci-foundation` in Wave 0) | `specs/SPEC-w3-engineering.md` | CI run green | not started |
| 16 | `patent/` — claims cover prior art | `publication-truth` + `w3-patent` | both specs | `patent/CLAIMS_TRACEABILITY.md` | not started |

## Release blockers

The gap analysis names gaps 1, 5, 7, and 11 as the release blockers. Their
closure is the Wave 0 gate.

| Blocker | Module | Task ids | Gate criterion | Evidence link |
|---|---|---|---|---|
| Negation (gap 1) | `w0-assertion-nlp` | `W0-AL-01`…`W0-AL-05` | Golden harness ≥95%; live probe flips | _pending_ |
| Red flags (gap 5) | `w0-red-flag-engine` | `W0-RF-01`…`W0-RF-06` | 100% emergency-flagging; refusal works | _pending_ |
| Circular eval (gap 7) | `w0-benchmark-honesty` + `w1-external-eval` | `W0-BH-01`…`W0-BH-04`, `W1-EE-01`…`W1-EE-07` | No self-referential number in any doc; external numbers published with CIs | _pending_ |
| Fabricated output (gap 11) | `w0-truthful-frontend` | `W0-TF-01`…`W0-TF-05` | No code path renders a diagnosis without a backend response | _pending_ |

## Advanced differentiators

Gaps 3, 4, and 6 are the "advanced" differentiators — they are what makes the
system genuinely better rather than merely honest.

| Differentiator | Module | Task ids | Gate criterion | Evidence link |
|---|---|---|---|---|
| Coded KB (gap 3) | `w1-kb-v2` | `W1-KB-01`…`W1-KB-07` | Every condition has an ICD-11 code + ≥1 PD citation | _pending_ |
| Ask-coverage (gap 4) | `w2-ask-coverage` | `W2-AC-01`…`W2-AC-05` | Measured and above 36.9% | _pending_ |
| Calibration (gap 6) | `w1-conformal` | `W1-CF-01`…`W1-CF-06` | Coverage within ±2pp of nominal on external data | _pending_ |

## Hardening

| Item | Module | Task ids | Gate criterion | Evidence link |
|---|---|---|---|---|
| RAG (gap 8) | `w2-hybrid-rag` | `W2-HR-01`…`W2-HR-06` | Every recommendation carries a source ID; no NC-licensed corpus | _pending_ |
| Synthesis (gap 9) | `w2-schema-synthesis` | `W2-SS-01`…`W2-SS-05` | Schema-constrained; labeled degradation; band cannot be widened | _pending_ |
| Orchestration (gap 10) | `w2-orchestration` | `W2-OR-01`…`W2-OR-05` | Critic blocks unsafe deliveries; adaptive depth works | _pending_ |
| Regulatory (gap 12) | `w3-regulatory`, `w3-abdm` | `W3-RG-01`…`W3-RG-05`, `W3-AB-01`…`W3-AB-04` | Counsel sign-off; ABDM M1 milestone | _pending_ |
| Data layer (gap 13) | `w3-dpdp` | `W3-DP-01`…`W3-DP-08` | Consent + security controls implemented and tested | _pending_ |
| LLM dependency (gap 14) | `w3-engineering` | `W3-EN-04` | Local fallback benchmarked; off-box PHI path closed | _pending_ |
| Engineering (gap 15) | `w3-engineering` | `W3-EN-01`…`W3-EN-05` | CI green on every PR; frontend suite exists | _pending_ |
| Patent (gap 16) | `publication-truth`, `w3-patent` | `PT-01`…`PT-05`, `W3-PT-01`…`W3-PT-04` | Claims re-scoped; prior-art search filed | _pending_ |

## Claim-level traceability for the retired numbers

These are the specific claims that must not survive anywhere in the project.

| Claim | Where it appears today | Action | Task |
|---|---|---|---|
| "98.0% Top-1 diagnostic accuracy" | `paper/phase3-paper/main.tex:41` (abstract), `:228` (results table), `:250` (analysis), `:300` (conclusion) | Retract or restate | `PT-01` |
| "+5.0% gain, p = 0.0339" | `main.tex:41`, `:69`, `:250` | Retract — the comparison is against a circular baseline | `PT-01` |
| "100.0% Top-3 differential coverage" | `main.tex:41`, `:228`, `:250`, `:300` | Retract | `PT-01` |
| "ECE decreased by 55.7%" | `main.tex:41`, `:234`, `:253` | Retract — ECE 0.2451 is measured on circular cases | `PT-01` |
| "Brier score improved by 62.1%" | `main.tex:41`, `:253` | Retract | `PT-01` |
| "53.7% reduction in Shannon diagnostic entropy" | `main.tex:41`, `:250`, `:300` | **Retain with care** — entropy reduction is a mechanism property, not an accuracy claim, but it is measured on circular cases and must be re-framed as such or re-measured | `PT-02` |
| "98% top-1" in repo docs | `README.md`, `docs/test_report.md` | Verify and correct | `W0-BH-03` |
| Accuracy claims in the patent spec | `patent/specification/provisional_patent_specification.md` | Re-scope | `W3-PT-02` |

## Change log

| Date | Change | By |
|---|---|---|
| 2026-10-28 | Initial matrix created from `12_GAP_ANALYSIS.md` | planning |
