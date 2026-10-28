# AegisMed Public-Release Research Program

Deep literature + landscape research to identify what AegisMed (multi-agent
symptom-based diagnostic support) is missing to become a genuinely advanced,
public-facing diagnostic assistant — and where the breakthrough opportunities
are.

**Commissioned:** 2026-10-27 · **Status: COMPLETE** — all 11 scope dossiers +
master synthesis + gap analysis + roadmap delivered. ~600 sourced claims.

## Context

AegisMed today (verified in-repo, 2026-10-27):

- Symptom understanding: deterministic clinical-pattern extractor; ~9 pattern
  categories; **no negation comprehension** (verified: "no fever, no cough,
  no chest pain" → fever/cough/chest pain extracted as present); optional
  biomedical NER checkpoint, off by default, never evaluated.
- Reasoning: DEMAT entropy-based active triage over a **15-condition**
  knowledge base; 12-question follow-up bank.
- Knowledge: FAISS RAG over 500 passages from 9 guideline sources;
  25/25 top-5 hit rate on a self-referential 25-query eval.
- Risk: 4 GradientBoosting models trained on 500 synthetic records.
- Measured accuracy: 98% top-1 on 200 synthetic cases generated from the same
  15-disease KB (circular); ECE 0.245; **no real-patient evaluation** (IRB
  blocked).
- Stack: FastAPI + Next.js 16, FHIR R4 in/out, SQLite, portal without user
  auth/TLS, PHI-safe logging (fixed 2026-10-27), demo-diagnosis-on-API-error
  path in the frontend.
- Goal: release to the general public as an advanced diagnostic assistant;
  project is patent-oriented (provisional filed path) and paper-oriented
  (CHIL).

## Research questions (scopes)

| # | Scope | Notes file |
|---|---|---|
| S1 | Symptom-checker landscape (Ada, Babylon, Symptomate, K Health, Isabel, Buoy, …

) | `01_symptom_checker_landscape.md` |
| S2 | Public/scientific accuracy evaluations of symptom checkers | `02_public_accuracy_evaluations.md` |
| S3 | Clinical NLP SOTA: negation, entity linking, symptom extraction, multilingual | `03_clinical_nlp_sota.md` |
| S4 | LLM & agentic differential diagnosis SOTA | `04_llm_agentic_diagnosis_sota.md` |
| S5 | Uncertainty, calibration & conformal methods in medical decision support | `05_uncertainty_calibration.md` |
| S6 | Datasets & evaluation protocols for symptom-based diagnosis | `06_datasets_evaluation.md` |
| S7 | Regulatory pathways: FDA CDS/SaMD, EU MDR, India CDSCO, DPDP/HIPAA/GDPR | `07_regulatory_pathways.md` |
| S8 | Safety & escalation design for consumer health AI | `08_safety_escalation_design.md` |
| S9 | Medical knowledge sources & licensing (UMLS, SNOMED, ICD, drug DBs) | `09_knowledge_sources_licensing.md` |
| S10 | Architecture advancements: medical RAG, agentic patterns, privacy-preserving inference | `10_architecture_advancements.md` |
| S11 | Patent / prior-art landscape for symptom triage & agentic diagnosis | `11_patent_prior_art.md` |

## Evidence rules (all notes must comply)

1. Every load-bearing claim carries **≥3 independent sources**; fewer than 3
   is marked `WEAK-EVIDENCE`.
2. Quotes are **verbatim** with URL + publisher + date. Empty fetch = empty
   claim — never fabricate a citation.
3. Numbers (accuracy %, N, p-values, prices, dates) are captured exactly as
   published, with the comparison baseline noted.
4. Unknowns are written as `UNKNOWN — how to find out: …`.
5. Each file ends with **"Implications for AegisMed"** — 5–10 concrete,
   file-level changes for this repo.

## Files

- `README.md` — this protocol
- `00_MASTER_SYNTHESIS.md` — cross-scope synthesis (written last)
- `12_GAP_ANALYSIS.md` — every gap mapped to a concrete AegisMed change
- `13_ROADMAP.md` — prioritized, sequenced plan to public release
