# Master Synthesis — What It Takes to Make AegisMed Public-Grade

*Distilled from 11 scope dossiers (this directory), ~500 sourced claims, and
live code verification. Written 2026-10-27.*

---

## 1. The honest accuracy picture

**The best published field baselines are far lower than intuition suggests.**

| Measurement | Result | Source |
|---|---|---|
| 23 commercial checkers, 45 vignettes, top-1 | **34%** (top-20 58%; appropriate triage 57%) | Semigran, BMJ 2015 |
| 36 checkers, 48 vignettes, top-1 | **36%** (40% over-escalation vs 10% under-triage) | Hill, MJA 2020 |
| 12 tools, top-1 | **37.7%** (advice safety 82.6%) | Ceney, PLOS ONE 2021 |
| 48 checkers, systematic review | top-1 **19–37.9%**, triage 48.8–90.1% | Wallace, npj Digit Med 2022 |
| Best-in-class single tool | Ada: top-3 **70.5%**, condition coverage 99% | Gilbert, BMJ Open 2020 |
| LLM era, hardest external benchmarks | o3: **60%** HealthBench (Hard: 32%); GPT-4: **62.5%** DxBench with inquiry; best agentic scaffold: **35.1%** (o3-mini+MDAgents, MedicalAgentsBench); AMIE: **29.2%** top-1 on NEJM CPC | 2025–2026 (see 04, 06) |
| LLM vs physicians on static vignettes | LLM alone **92%** vs physicians 74–76% — but static vignettes ≠ sequential dialogue | Goh, JAMA 2024 |

**Why AegisMed's 98% top-1 cannot be published:** the benchmark cases are
generated from its own 15-disease KB and `simulate_patient_answer()` answers
follow-ups using the same KB's likelihoods — the oracle is the system under
test. AgentClinic (arXiv:2405.07960) showed that moving from static MCQ to a
sequential, question-asking format can collapse accuracy "to below a tenth of
the original accuracy." AegisMed's live negation failure ("no fever, no cough,
no chest pain" → all three extracted as present) demonstrates the same gap at
stage one. **Realistic expectation after fixes: somewhere in the 30–60% top-1
band on external vignettes — matching the honest field frontier, not 98%.**

**Sample-size math:** a credible ±5pp claim at p≈0.7 needs **n≈323** external
vignettes (±3pp → ~700). The current 200 self-generated cases fail both tests
(circularity and power).

## 2. The ten findings that should drive everything

1. **Failure to *ask* is the field's dominant failure mode** — commercial
   checkers asked only **36.9%** of relevant red-flag questions vs **71.8%**
   for PCPs (Ada itself: 26.6%) while still leading on triage sensitivity.
   (08, Sutaria BMC HSR 2025)
2. **Under-triage of emergencies is field-wide** — AI triage sensitivity
   58.3% vs nurses 73.8% (EUSEM 2025); ChatGPT Health under-triaged **51.6%**
   of gold-standard emergencies (Nature Medicine, Feb 2026). (08, 02)
3. **Negation/assertion comprehension is solved research AegisMed lacks** —
   i2b2-2010 best assertion classifier F=0.936; NegBERT scope F1 up to 95.7;
   ALBERT 0.991 vs NegEx 0.921 head-to-head. (03)
4. **The d4data NER checkpoint publishes zero metrics** (66M params, 30-minute
   training, ~200 noisy case reports) and must not ship unmeasured. (03)
5. **LLM verbalized confidence is clinically uninformative** (right vs wrong:
   76.1% vs 74.4% confidence; r=−0.40) and AegisMed's ECE 0.245 is far outside
   acceptable range. Conformal prediction is the shippable fix — but must be
   applied **before** multi-agent agreement blending (unanimous-but-wrong
   peers collapse coverage 90%→74%). (05)
6. **The 2026 consumer architecture consensus: LLM conversation over a
   deterministic certified triage core with guideline-grounded RAG** — the
   Kopka 2025 RCT showed Ada lifted laypeople's triage accuracy 53.2%→64.5%
   while ChatGPT alone did nothing. (01)
7. **Guideline-grounded generation is measured, not optional** — Almanac +18%
   over vanilla ChatGPT; 31% of ungrounded citations completely fabricated;
   hybrid (BM25+dense) retrieval consistently beats dense-only. (10, 04)
8. **The terminology layer is free in India** — SNOMED CT (member country,
   free Affiliate License), ICD-11 (explicitly licenses CDS + AI training),
   RxNorm (public domain), MedlinePlus Connect (free patient-education API
   keyed by ICD-10/RxNorm). ABDM's FHIR R4 IG + M1/M2/M3 certification is the
   national on-ramp. **But WHO guideline text is CC BY-NC-SA — the current
   RAG corpus embeds it, a latent non-commercial clause.** (09)
9. **India's regulatory posture is strict** — CDSCO's SaMD guidance lists
   "triages patients … suggests likely diagnosis" as regulated software
   (Class B–C; consumer use in serious situations escalates toward C/D;
   MD-3→MD-5, ~180 days). Telemedicine Guidelines 2020 clause 2.8: AI cannot
   counsel or prescribe. DPDP Rules 2025: full compliance **13 May 2027**,
   penalties to ₹250 crore, verifiable parental consent for <18. In the US, a
   consumer symptom checker cannot use the clinician-facing CDS exemption; EU
   MDR Rule 11 → Class IIa (Ada IIa Dec 2022, Infermedica IIb Sep 2025). (07)
10. **Patent reality:** entropy/information-gain question selection is a
    standard ML building block — unpatentable in the abstract; the granted
    claim shape wraps it in system boundaries. Direct recent prior art exists
    (JAMIA 2026 orchestrator–specialist headache CDSS; WO2023095069A1). The
    defensible surface: the deterministic bounded-bank mechanism +
    **conformal-before-agreement** calibration + measured safety-band
    contract + ABDM/FHIR integration. Run a CPC G16H50/20 professional search
    before any PCT decision. (11)

## 3. What "highly advanced, public-grade" concretely means here

The evidence converges on one architecture and one evidence standard:

**Architecture:** free-text in → terminology-grounded extraction (with
assertion/negation handling) → DEMAT triage over a SNOMED/ICD-11-grounded KB
(hundreds of conditions, versioned) with **measured red-flag question
coverage** → conformal-calibrated output bands (emergency/urgent/routine/
self-care/out-of-scope) → LLM narrative **strictly bounded by the deterministic
core and citations** (schema-constrained, never overriding triage) → action-
first escalation UI → every failure visibly degraded, never fabricated.

**Evidence standard:** external vignette evaluation (DxBench protocol,
n≥323) reporting top-1/top-3, **emergency-case sensitivity**, red-flag
question-ask coverage, and calibration (ECE) — each with CIs. Publish the
safety metrics before the accuracy metrics.

## 4. Release verdict

As of today, AegisMed is **not releasable to the public** — not primarily
because of accuracy, but because of four hard blockers: (1) comprehension
failures that corrupt the pipeline at stage one (negation), (2) a frontend
that fabricates diagnoses on API error, (3) no out-of-scope refusal, (4) no
regulatory/consent posture (DPDP deadline 13 May 2027 is ~6.5 months out).
None of these is research-hard; all are engineering + process work. The
breakthrough opportunities (§2 items 1, 2, 5) are what would make the release
*advanced* rather than merely safe.

## 5. Reading order

`12_GAP_ANALYSIS.md` (component-by-component) → `13_ROADMAP.md` (sequenced
plan with acceptance gates) → the individual dossiers for sources.
