# AegisMed Retrospective Clinical Validation Protocol

**Status: `BLOCKED: external` — requires IRB approval and a hospital data
access agreement. Nothing in this protocol has been executed. No patient
data has been accessed, and no validation result exists. Any number quoted
from the Phase 3 benchmark (`data/benchmarks/results/demat_research_benchmark.json`)
is synthetic-case evidence, not clinical validation.**

**Version:** 1.0 (draft for IRB review) · **Date:** 2026-10-25 ·
**Sponsor/investigator:** Arham Saghir (B.Tech candidate) with a named
faculty PI and a licensed clinical co-investigator to be confirmed by the
reviewing institution before submission.

## 1. Objective

Estimate, on real retrospective encounters, the diagnostic accuracy,
calibration, and triage behaviour of the AegisMed multi-agent pipeline
(DEMAT active triage + evidential arbitration), and quantify its
decision impact relative to a single-pass (no active questioning)
baseline of the same system.

Primary question: *does AegisMed's active-triage pipeline identify the
final discharged diagnosis in the top-k of its differential more often
than its own single-pass arm, on real clinical encounters?*

## 2. Design

Retrospective, single-centre, paired within-encounter evaluation. Each
eligible encounter is run through both arms of the pipeline:

- **Arm A (DEMAT, index):** the full multi-agent pipeline with entropy-
  driven follow-up questioning (the Phase 3 two-arm design).
- **Arm B (single-pass, comparator):** the same agents without DEMAT
  refinement — the internal ablation, not an external comparator.

Both arms receive the identical de-identified encounter extract. The
encounter is the unit of analysis; arms are compared with McNemar's test
on paired concordance (`scripts/benchmark/metrics.py::compute_mcnemar_test`).

## 3. Cohort selection

### Inclusion criteria
1. Adult encounter (age ≥ 18 at visit).
2. Presenting complaint documented in structured triage text or free text.
3. A final diagnosis coded in the EHR (ICD-10) at discharge or end of visit.
4. Encounter date within the retrieval window approved by the data
   governance office.

### Exclusion criteria
1. Encounters with an unusable presenting narrative (e.g., administrative
   visits, lab-only reviews).
2. Final diagnosis outside the system's 15-class disease universe — these
   are retained for a documented "out-of-scope" subgroup analysis but
   excluded from the primary endpoint.
3. Encounters whose de-identified extract cannot be produced without
   residual identifiers (per §7).
4. Imaging subset only: no interpretable chest radiograph in the archive.

### Strata
- Presenting severity (ESI 2–5 if available),
- imaging vs non-imaging encounters,
- out-of-scope final diagnoses.

## 4. Endpoints

| # | Endpoint | Metric (implemented in `scripts/benchmark/metrics.py`) | Estimand |
|---|---|---|---|
| E1 | Top-1 diagnostic accuracy | `compute_top_k(k=1)` | Proportion, both arms, paired difference |
| E2 | Top-3 diagnostic accuracy | `compute_top_k(k=3)` | Proportion, both arms |
| E3 | Calibration | `compute_ece`, `compute_brier_score` | ECE with 10 equal-mass bins; Brier over the disease universe |
| E4 | Triage efficiency | Entropy of the differential after each DEMAT question | Mean entropy reduction per question; questions-to-threshold |
| E5 | Safety (exploratory) | High-severity under-triage rate | Proportion of encounters adjudicated emergent whose triage severity was not "high" |
| E6 | Decision impact (exploratory) | Management concordance | Proportion of encounters where the top differential's standard management is concordant with the discharge plan, per a blinded chart rubric |

E1–E3 are pre-specified primaries for the accuracy claim; E4 mirrors the
entropy-collapse endpoint of the Phase 3 benchmark; E5–E6 are exploratory
hypothesis-generating endpoints and are labelled as such in any output.

## 5. Sample size and power

The paired primary comparison (E1, Arm A vs Arm B) is powered with
McNemar's test. Phase 3 synthetic-benchmark evidence observed a 5-point
paired difference (98.0% vs 93.0% top-1, n=200, p=0.0339) with a
discordant-pair proportion near 9%. To detect a 5-point paired difference
assuming a conservative 12% discordant rate at α=0.05 (two-sided) and
80% power requires approximately 350 eligible paired encounters.

Target: **500 screened → ≥ 350 analysable encounters**, plus a target of
**≥ 100 imaging encounters** for the vision-arm subgroup (estimates only;
the vision subgroup is not powered for inference). If accrual falls short
of 350 analysable encounters, the primary analysis proceeds as a
precision estimate (Wilson 95% CI) and is reported as under-powered, not
as a failed replication.

## 6. Analysis plan

1. Lock this protocol and the extraction script before data access.
2. Run both arms on every eligible encounter with the pipeline pinned to
   the release commit; model weights and the vector store are versioned
   and hash-recorded.
3. Primary analysis: paired top-1 (E1) with McNemar's test; exact
   binomial Wilson CIs for all proportions.
4. Subgroups per §3 strata, reported with CIs, no multiplicity adjustment
   (exploratory), flagged accordingly.
5. Missing/errored pipeline runs are reported as failures (denominator
   retains them); no imputation of diagnoses.
6. All results are published with the run configuration, code commit,
   and model hashes regardless of direction or significance.

## 7. Data protection and de-identification

- Extracts are de-identified to **HIPAA Safe Harbor** (all 18 identifier
  classes removed): names, MRN replaced by a study pseudonym via a
  key held only by the hospital's honest broker, dates shifted by a
  per-patient random offset preserving intervals, ages > 89 banded to
  "90+", free text scrubbed with a second-pass NLP identifier sweep.
- The research copy contains no direct identifiers; re-identification is
  technically infeasible for the research team.
- Transport and storage: hospital-controlled export over the institution's
  approved channel; at-rest encryption; no data leaves institutional
  custody for the cloud LLM path — synthesis runs on the rule-based
  fallback for the validation runs (no third-party LLM processing).
- Retention: extracts destroyed within 90 days of study closure; analysis
  artefacts (aggregate metrics, no case-level data) retained in the
  repository.

## 8. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Algorithmic drift across the cohort period | Pipeline pinned to one commit + hashed weights; cohort period recorded |
| Automation bias in later prospective use | This study is retrospective and blinded-chart-review based; no clinical deployment decision rests on it |
| Re-identification via rare free text | Two-pass scrubbing + honest-broker key custody; residual-risk statement in the IRB submission |
| Silent model degradation (unreadable weights) | Deployment refuses to serve without staged weights (`docker/entrypoint.sh`); validation runs log weight hashes |

## 9. Blocked-item register

| Item | Status |
|---|---|
| IRB approval (retrospective chart review category) | `BLOCKED: user action` — submission templates in `clinical/IRB_SUBMISSION_TEMPLATES.md` |
| Hospital data access agreement / honest broker | `BLOCKED: user action` |
| Faculty PI + licensed clinical co-investigator signatures | `BLOCKED: user action` |
| Validation harness execution | `BLOCKED` on the above — interface design only, see `clinical/VALIDATION_HARNESS_DESIGN.md` |
