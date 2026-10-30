# Final Submission Checklist

> **Status accuracy note (publication-truth phase A, 2026-10-31):** earlier
> revisions of this checklist cited 100% and 98% benchmark "accuracy" figures.
> Those numbers came from a self-generated harness whose cases derive from the
> system's own knowledge base — the oracle is the system under test — and the
> 98% presentation was formally retired (see
> [`data/benchmarks/RETIREMENT.md`](data/benchmarks/RETIREMENT.md)). The
> earlier 100% figure came from a superseded demo-matching script and must
> never be cited. **The project currently has no defensible clinical-accuracy
> number**; establishing one on external doctor–patient vignette benchmarks is
> the next milestone.

## Accuracy Situation (read this first)

- The maintained evaluation artifact is the **self-generated regression
  harness** ([`scripts/benchmark/demat_benchmark.py`](scripts/benchmark/demat_benchmark.py)):
  it verifies triage *mechanism* properties (entropy reduction, information-gain
  ranking, stopping rule, determinism). Its outcome-level numbers are
  internal-consistency measurements, **not accuracy**.
- Clinical accuracy (top-1/top-3 with confidence intervals), calibration, and
  red-flag ask-coverage will be measured on external vignette benchmarks
  (DxBench protocol; `gretelai/symptom_to_diagnosis`) before any submission.
- The paper (`paper/phase3-paper/main.tex` + `main_humanized.tex`) has been
  re-scoped to the mechanism contribution with unimplemented layers labeled as
  proposed extensions. Do not reintroduce accuracy framing without external data.

## Completed Tasks

### Evaluation Artifact ✅
- Self-generated regression harness maintained and labeled (banner on every
  run; provenance block in `data/benchmark_cases.json`)
- Retirement record for the circular accuracy claim:
  [`data/benchmarks/RETIREMENT.md`](data/benchmarks/RETIREMENT.md)
- Guard test (`tests/unit/test_retired_claims_guard.py`) fails the suite if
  the retired claim reappears unlabeled

### Paper Re-Scoping ✅ (publication-truth phase A)
- Circular accuracy claims removed from abstract, results, analysis, and
  conclusion in both drafts
- Unimplemented layers (EN-SCAF Dempster-Shafer arbitration, knowledge-graph
  pruning, conformal synthesis) labeled as **proposed designs** with their
  implementation status stated in-line
- Mechanism contribution restated: entropy-driven active triage, with the
  field's ask-coverage deficit as the motivating evidence
- Both drafts compile clean (tectonic, 0 errors)

### Test Suite ✅
- Full backend suite green (`python -m pytest -q`); frontend Vitest suite
  introduced in PR #8; CI gates every PR (`.github/workflows/ci.yml`)

## Phase 3 Deliverables: Patent Filing & Conference Submission Packages

### Provisional Patent Package (Indian Patent Office / USPTO)
- **Status:** Package assembled; **claim re-scoping is PENDING** — the
  research program identified the current entropy-triage claims as likely
  prior art; the brief to counsel must be re-scoped to the defensible contract
  (deterministic bounded-bank triage + conformal-before-agreement + a safety
  band the LLM cannot widen) **before** the provisional filing (D0).
- **Detailed Checklist:** See [`patent/FILING_CHECKLIST.md`](patent/FILING_CHECKLIST.md)
- **Specification Draft (DOCX):** [`patent/specification/provisional_patent_specification.docx`](patent/specification/provisional_patent_specification.docx)
- **Specification Source (MD):** [`patent/specification/provisional_patent_specification.md`](patent/specification/provisional_patent_specification.md)
- **Drawings (300 DPI, FIGS. 1–5):** [`patent/figures/`](patent/figures/)
- **Counsel Brief & Search Strings:** [`patent/PATENT_AGENT_BRIEF.md`](patent/PATENT_AGENT_BRIEF.md)
- **Claim Traceability Matrix:** [`patent/PATENT_PORTFOLIO_SUMMARY.md`](patent/PATENT_PORTFOLIO_SUMMARY.md)
- **Next User Action:** Have the patent agent re-scope the claims per the
  brief update, then execute Form 1/2, pay statutory fee, and receive the
  official application number.

### Conference Submission Package (ACM CHIL / MICCAI)
- **Status:** Manuscript re-scoped and compiled (tectonic, 0 errors);
  `BLOCKED: user action` for OpenReview upload (after patent priority is
  secured **and** external evaluation numbers exist — see accuracy note above).
- **Detailed Checklist:** See [`paper/SUBMISSION_CHECKLIST.md`](paper/SUBMISSION_CHECKLIST.md)
- **Compiled Manuscript (PDF):** [`paper/phase3-paper/main.pdf`](paper/phase3-paper/main.pdf)
- **LaTeX Source & Figures:** [`paper/phase3-paper/`](paper/phase3-paper/)
- **Reproducibility Harness:** [`scripts/benchmark/demat_benchmark.py`](scripts/benchmark/demat_benchmark.py) (seed: 42, cases: 200 — regression harness, not an accuracy benchmark)
- **Committed Results:** [`data/benchmarks/results/demat_research_benchmark.json`](data/benchmarks/results/demat_research_benchmark.json)
- **Next User Action:** After the external evaluation lands and the patent
  application number exists, anonymize author headers in `main.tex`, compile
  the blinded submission PDF, and upload to OpenReview.

---

## Remaining Tasks (Academic Thesis & Presentation)

### Demo & Presentation Polish
- [ ] Update presentation slides with the **mechanism** framing (no accuracy
      claims; see `data/benchmarks/RETIREMENT.md`)
- [ ] Capture 5 required screenshots (see `screenshots/README.md`)
-   1. Diagnosis page with results
-   2. Vision page with pneumonia case
-   3. Chat page with conversation
-   4. History page with saved records
-   5. PDF report export
- [ ] Insert screenshots into thesis Appendix D
- [ ] Practice demo script (12-15 minutes)

### Personal Information (Thesis)
- [ ] Replace `[Your Name]` with your name
- [ ] Replace `[Your Roll Number]` with your roll number
- [ ] Replace `[Supervisor Name]` with supervisor's name
- [ ] Replace `[Supervisor Designation]` with supervisor's title
- [ ] Replace `[University/College Name]` with your university
- [ ] Replace `[relevant field]` with supervisor's expertise
- [ ] Replace `[Year]` with submission year
- [ ] Replace `[GitHub Repository URL]` with your repo URL

## Key Files to Review
- `docs/thesis.md` - Main thesis document (accuracy sections need the same re-scoping)
- `docs/demo_script.md` - Demo script (complete)
- `docs/presentation.pptx` - Presentation (needs mechanism-framing update)
- `frontend/src/app/diagnosis/page.tsx` - Diagnosis page (Next.js App Router)
- `scripts/benchmark/demat_benchmark.py` - Self-generated regression harness
- `screenshots/README.md` - Screenshot instructions

## Demo Commands
```bash
# Backend (FastAPI, port 8000)
venv/bin/python -m uvicorn src.api.main:app --port 8000

# Frontend (Next.js, port 3000)
cd frontend && npm run dev

# Regression harness (internal-consistency only — NOT an accuracy benchmark)
venv/bin/python scripts/benchmark/demat_benchmark.py

# Full test suite (see root SPEC.md for the canonical /build and /test gates)
venv/bin/python -m pytest -q
cd frontend && npm run test
```
