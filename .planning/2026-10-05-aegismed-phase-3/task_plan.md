# AegisMed Phase 3 — Provisional Patent Filing & Research Benchmark (Task Plan)

**Goal:** Convert Phase 2's shipped, verified functionality into research-grade benchmark evidence and a filing-ready provisional patent package, plus a compile-clean CHIL/MICCAI paper draft.

**Plan doc:** `PHASE3_WORKFLOW.md` in this directory.
**PRD scope:** `PRD.md` §10 Phase 3 (Weeks 9–14) and §9 patent claims.
**Branch:** `feat/phase-3-patent-and-research-benchmark` (to be cut from `feat/full-stack-integration-and-automations`).
**Execution order:** sequential, one workstream at a time, each ending at its acceptance gate.

## Next Step

Phase 3 is COMPLETE. All research benchmarks, provisional patent specification & figures, ACM CHIL research paper draft, and filing/submission readiness packages are packaged, verified, and committed. Human user actions (patent filing execution and conference upload) are documented with step-by-step checklists.

## Current Phase

### Phase 3 Complete — All Workstreams Delivered
**Status:** complete

## Phases

### Workstream 3.0 — Recon & Baseline
**Status:** complete (executed during plan authoring; findings.md holds the inventory)

Done: inventoried existing benchmark scripts (`run_benchmark.py`, `generate_benchmark_cases.py` — demo-function-based, superseded), synopsis suites, chapters, References.bib, MIMIC-IV credential dependency, Phase 2 evidence.

### Workstream 3.1 — Research Benchmark Harness (DEMAT vs. ablation)
**Status:** complete

- [x] 3.1.1 Ground DEMAT/orchestrator callable surfaces (`src/core/demat.py`, `disease_kb.py`)
- [x] 3.1.2 Dataset decision: resolved 10-disease vs 15-condition mismatch by expanding disease KB to 15 conditions; noted MedQA USMLE format mismatch for triage
- [x] 3.1.3 Library check via standard numerical/information-theoretic implementations (NumPy, SciPy, Math)
- [x] 3.1.4 Build harness: `scripts/benchmark/{demat_benchmark,metrics}.py`, two arms (DEMAT / single-pass ablation), seeded determinism
- [x] 3.1.5 Results committed to `data/benchmarks/results/` (`demat_research_benchmark.json`, `demat_benchmark_summary.md`)
- [x] 3.1.6 Acceptance: `tests/unit/test_demat_benchmark.py` passing (7 tests); 140 passed / 17 skipped total suite; smoke slice runs end-to-end

### Workstream 3.2 — Patent Specification & Figures (draft)
**Status:** complete

- [x] 3.2.1 Claim-to-code mapping completed and documented in `patent/PATENT_PORTFOLIO_SUMMARY.md`
- [x] 3.2.2 Figures F1–F5 generated at 300 DPI (2550x3300 px) in `patent/figures/`
- [x] 3.2.3 Specification sections drafted in `patent/specification/provisional_patent_specification.md`
- [x] 3.2.4 Consistency lint: 0 placeholder tokens; all 12 claims mapped to figures and text
- [x] 3.2.5 Acceptance: figures verified at 300 DPI; spec marked "draft for attorney review"

### Workstream 3.3 — Research Paper Draft (CHIL / MICCAI)
**Status:** complete

- [x] 3.3.1 Venue decision from current calls: ACM CHIL primary, MICCAI workshop fallback
- [x] 3.3.2 Paper skeleton `paper/phase3-paper/main.tex` and `references.bib` created with full mathematical disclosures
- [x] 3.3.3 Benchmark tables (Tables 1 and 2) integrated verbatim from `data/benchmarks/results/demat_research_benchmark.json`
- [x] 3.3.4 Honesty check: every number traces byte-for-byte to committed empirical benchmark results
- [x] 3.3.5 Acceptance: `make` and `tectonic` compile clean — 8 pages, 0 errors, 0 undefined references (`paper/phase3-paper/main.pdf`)

### Workstream 3.4 — Filing & Submission Readiness
**Status:** complete

- [x] 3.4.1 Jurisdiction decision documented (IPO default via Form 2, USPTO § 111(b) as dual/alternative; priority under Paris Convention)
- [x] 3.4.2 Spec `.docx` export generated (`patent/specification/provisional_patent_specification.docx`) + figure bundle verified (300 DPI)
- [x] 3.4.3 `patent/PATENT_AGENT_BRIEF.md` created with 4 inventive pillars, 12 claims, IPC/CPC classes, Boolean search strings, and India Sec. 3(k)/3(i) & US § 101 defense strategies
- [x] 3.4.4 Conference submission checklist created in `paper/SUBMISSION_CHECKLIST.md` (venue rules, double-blind instructions, repro bundle script) + updated root `SUBMISSION_CHECKLIST.md`
- [x] 3.4.5 Acceptance: every item maps to a verified file or an explicit `BLOCKED: user action` requirement; patent filing protocol preserves pre-publication novelty embargo

## Decisions Made

| Decision | Rationale |
|---|---|
| Supersede `run_benchmark.py` instead of extending it | It measures the demo rule function, not the pipeline; its 100% synthetic-accuracy claim must not reach the paper or patent |
| CHIL primary, MICCAI workshop secondary | CHIL matches the clinical-ML framing; workshop format is the fallback if timing or result strength favors it |
| IPO as default jurisdiction | Project affiliation context; must be confirmed by the user before any filing step |
| Patent spec drafted as markdown first, exported to .docx at 3.4 | Draft iteration stays diff-able in git; docx is a filing-format concern, not a drafting concern |

## Errors Encountered

| Error | Attempt | Resolution |
|---|---|---|
| context7 MCP rejected invalid API key (Phase 2.1) | documented | Proceed on standard docs; record in progress if it recurs in Phase 3 |
| documents:visual-judge subagent provider unavailable (Phase 2.4) | fell back | Direct Read inspection of rendered PNGs, explicitly recorded as fallback in progress.md |
| eslint: `setState` in effect in persona.tsx + 4 `any` in api.ts | fixed same day | `useSyncExternalStore` for localStorage; typed payload interfaces; re-lint clean |
