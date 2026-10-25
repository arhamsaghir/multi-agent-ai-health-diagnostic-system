# AegisMed Retrospective Validation Harness — Interface Design

**Status: `BLOCKED` — design only.** This document fixes the harness
interface so that when IRB approval and the data access agreement exist
(see `VALIDATION_PROTOCOL.md` §9), implementation is mechanical and the
analysis cannot drift from the locked protocol. Nothing here has been
run against patient data.

## Design constraints

1. **Reuse the Phase 3 metric implementations** — `scripts/benchmark/metrics.py`
   (`compute_top_k`, `compute_brier_score`, `compute_ece`,
   `compute_mcnemar_test`). The validation reports numbers produced by
   the same code the synthetic benchmark used, so the two evidence bases
   are directly comparable.
2. **Reuse the two-arm driver** — `scripts/benchmark/demat_benchmark.py::run_benchmark`
   already implements Arm A (DEMAT) vs Arm B (single-pass) with seeded
   reproducibility. The validation harness wraps it instead of
   reimplementing the arm logic; the only new component is the cohort
   source.
3. **No patient data in the repository.** The harness reads a cohort
   file supplied by the hospital's honest broker at runtime; only
   aggregate outputs are written back.

## Interface

```python
# clinical/validation_harness.py  (to be implemented post-approval)

from pathlib import Path
from typing import Iterable, Protocol

class CohortSource(Protocol):
    """Yields de-identified encounters from the honest-broker export."""

    def encounters(self) -> Iterable[dict]:
        """Each record mirrors the benchmark case schema:
        {
          "case_id": "<study pseudonym>",
          "presenting_complaint": str,      # de-identified narrative
          "demographics": {"age_band": "35-44", "gender": "F"},
          "chest_xray_path": str | None,    # study-local path, imaging subset
          "acceptable_conditions": [str],   # ICD-10-mapped disease-universe names
          "in_scope": bool,                 # protocol §3 exclusion applied
          "strata": {"esi": int | None, "imaging": bool}
        }
        """
        ...

def run_validation(
    cohort: CohortSource,
    output_dir: Path,
    *,
    pipeline_commit: str,
    weight_hashes: dict[str, str],
) -> dict:
    """Run both arms per encounter and emit the locked endpoint set.

    Writes ONLY aggregate artefacts into output_dir:
      - validation_results.json   (endpoint estimates + CIs + McNemar)
      - validation_manifest.json  (commit, weight hashes, cohort counts,
                                   run timestamps, config digest)
    Raises if any encounter errored — per protocol §6.5 errors stay in
    the denominator and are reported, never dropped silently.
    """
```

## Endpoint computation mapping

| Protocol endpoint | Harness computation |
|---|---|
| E1/E2 Top-1/Top-3 | `compute_top_k(ranked, acceptable_conditions, k)` per encounter per arm; Wilson CI on the proportion; `compute_mcnemar_test` on the paired hit/miss table for the Arm A − Arm B difference |
| E3 Calibration | `compute_ece(probs, labels, bins=10)` and `compute_brier_score(probs, truth, acceptable)` per arm |
| E4 Triage efficiency | Mean per-encounter entropy trajectory from the DEMAT trace; questions-to-threshold distribution |
| E5 Safety | Rate of adjudicated-emergent encounters whose triage severity ≠ high, with exact binomial CI |
| E6 Decision impact | Post-hoc blinded chart rubric scored outside the harness; the harness only emits the top differential per encounter for the rubric reviewers |

## Verification before first real run

When the harness is implemented (post-approval), it must pass a
**synthetic smoke run** using `data/benchmark_cases.json` shaped into the
`CohortSource` schema, asserting:
- both arms execute end-to-end for every synthetic case,
- the endpoint JSON matches a recomputation via the metrics functions
  (unit test, not a claim about clinical performance),
- the manifest records commit and weight hashes.

The synthetic smoke run is a software check only and must never be
quoted as validation evidence.
