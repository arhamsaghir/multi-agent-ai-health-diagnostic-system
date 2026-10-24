# AegisMed — Phase 3 Planning Workflow

**Date:** 2026-10-05
**Branch:** `feat/full-stack-integration-and-automations` → new branch `feat/phase-3-patent-and-research-benchmark`
**Predecessor:** `.planning/2026-10-05-aegismed-phase-2/` (stepper, dual-mode UI, 500-doc RAG, PDF reports — all verified, 133 tests passing)
**PRD reference:** `PRD.md`, Phase 3 scope (§10) and Patent Claims (§9)
**Phase goal:** Turn shipped Phase 2 functionality into defensible research evidence and a filing-ready provisional patent package.

This document is the Phase 3 **planning workflow**: for each workstream it states (a) what gets built, (b) which **MCP services** the agent invokes at each step, (c) which **skills** are required, and (d) the acceptance gate that closes the workstream.

---

## 0. Workflow Conventions

- One workstream at a time; no parallel feature work inside Phase 3.
- Every workstream ends at its **acceptance gate** — build green (`pytest`, `npx tsc --noEmit`), deliverable artifacts on disk, live verification where the deliverable is interactive, planning files updated.
- All codebase exploration goes through the **codegraph MCP** (`codegraph_explore`). No blind grep/read sweeps.
- All library/API questions go through **context7 MCP** before writing integration code (noted: context7 rejected with invalid API key during 2.1 — if still failing, proceed on documented standard patterns and record the failure in `progress.md`).
- All browser-visible verification goes through **playwright MCP** (screenshots as evidence), all document-rendered visual judgment through **documents:visual-judge** (with Read-file fallback if the subagent provider is unavailable, record that too).
- Session state tracked in `.planning/2026-10-05-aegismed-phase-3/` (`task_plan.md`, `findings.md`, `progress.md`) per the `planning-with-files` methodology.
- **Legal honesty rule:** the repo produces a *draft* patent specification and a *readiness checklist*; actual filing and legal sign-off are human actions executed by the user with a registered patent agent (PRD sign-off table has this role pending). The plan must never represent a draft as filed.

---

## Workstream 3.0 — Recon & Baseline (status: DONE — executed during plan authoring)

| | |
|---|---|
| **Goal** | Confirm existing assets Phase 3 reuses and the hard dependencies it must plan around |
| **MCP services invoked** | `codegraph MCP` → `codegraph_explore` (report chapters, benchmark scripts, synopsis assets); shell inventory of `medical_ai_synopsis*/`, `SUBMISSION_CHECKLIST.md`, `REFERENCES.md` |
| **Skills required** | `planning-with-files` (session files) |

**Findings that shape Phase 3:**

1. **The existing benchmark is not research-grade.** `scripts/run_benchmark.py` + `scripts/generate_benchmark_cases.py` evaluate `frontend.pages.diagnosis._get_demo_result` (the demo rule function) on 200 synthetic cases and claim 100% accuracy (`SUBMISSION_CHECKLIST.md`). That measures a lookup function, not the multi-agent pipeline. Workstream 3.1 supersedes it with a real-pipeline harness; the old script stays only as a naming/dedup reference.
2. **Two synopsis suites exist.** `medical_ai_synopsis/` and `medical_ai_synopsis_revised/` contain full LaTeX chapters, 10+ figures (`.png`), and `References.bib`. These are direct inputs to 3.2 (patent spec sections) and 3.3 (paper skeleton) — do not rewrite from scratch.
3. **Chapters 1–8 exist in Markdown** (`chapter1…8_*.md`, `FULL_PROJECT_REPORT.md` 952 lines, `REFERENCES.md`) describing DEMAT, Grad-CAM, society/human-values framing — reusable paper prose.
4. **MIMIC-IV-CXR requires credentialed PhysioNet access** (human action: register, complete CITI training, sign DUA). This cannot be automated; Phase 3 gates on it or proceeds on the interim public path (NIH ChestX-ray14 download scripts already exist: `scripts/download_real_xray_images.py`, `scripts/download_chest_xray.py`).
5. **Phase 2 outputs are patent-figure evidence.** Live stepper screenshots (`evidence/phase2_stepper_*.png`), persona toggle, entropy trajectory, and the PDF report render the PRD §9 claims visible — 3.2 consumes these as figure source material.
6. **Phase 2 evidence paths:** 133 tests passing, 17 skipped (Python 3.13/XGBoost), `tsc` clean; RAG eval 25/25 top-5 at 100%; PDF endpoint live-verified.

---

## Workstream 3.1 — Research Benchmark Harness (DEMAT vs. ablations)

| | |
|---|---|
| **Goal** | Produce reproducible, research-grade benchmark results for the patent spec and paper: DEMAT active triage vs. single-pass ablation on MedQA-style clinical vignettes and chest-imaging cases |
| **Files (new)** | `scripts/benchmark/demat_benchmark.py` (harness), `scripts/benchmark/datasets.py` (loaders), `scripts/benchmark/metrics.py` (accuracy/top-k/ECE/entropy-reduction/latency), `data/benchmarks/results/*.json` (raw + summary tables), `tests/unit/test_benchmark_harness.py` |
| **Files (modified)** | `README.md` (benchmark section refresh noting the superseded demo-based runner) |

**Workflow steps:**

1. **Ground** — `codegraph MCP` → `codegraph_explore("DEMATEngine start_or_get_session select_questions update_belief_from_answer orchestrator run")` to pin the exact callable surfaces the harness must drive without UI or HTTP.
2. **Dataset decision** — `WebSearch`/`WebFetch`:
   - MedQA (4-option USMLE-style MCQ, e.g. `GBaker/MedQA-USMLE-4-options`): adapt to the system's output grammar — map differential list to option choice; fixed seeded subsample (e.g. n=300) with recorded seed.
   - MIMIC-IV-CXR: **prerequisite** — user must complete PhysioNet credentialing; if unavailable at execution time, run the imaging leg on the public NIH ChestX-ray14 path already in-repo and mark MIMIC-IV as pending-credentials in results.
3. **Library check** — `context7 MCP` → `datasets`, `numpy` ECE helpers; confirm pin versions.
4. **Harness** — two arms per case: (a) full pipeline incl. DEMAT interrogation budget (max 3 rounds per PRD §3.1), (b) ablation with DEMAT bypassed (single-pass). Metrics per arm: top-1/top-3 accuracy, expected calibration error, mean entropy before/after, questions asked, wall-clock latency distribution. Results written as JSON *plus* a markdown table ready for paper reuse.
5. **Acceptance gate** — `pytest` harness unit tests (metric math, arm isolation, seeded determinism: rerunning with the recorded seed reproduces identical metrics); harness completes a smoke run on a 20-case slice end-to-end; summary table committed under `data/benchmarks/results/`; `progress.md` updated with measured numbers. **The 133-test suite must not shrink.**

| Required skills | Why |
|---|---|
| `research` | Dataset selection + task adaptation |
| `benchmark` | Metric design, ECE, ablation rigor |
| `tdd` | Deterministic harness tests |
| `scientist` | Statistical readout discipline |

---

## Workstream 3.2 — Patent Specification & Figures (Draft)

| | |
|---|---|
| **Goal** | A complete, internally consistent *draft* provisional patent specification covering PRD §9 Claims 1–4, with figures that show each inventive step |
| **Files (new)** | `patent/specification/00-cover.md … 90-abstract.md` (field, background, summary, brief description of drawings, detailed description, claims, abstract), `patent/figures/*.mmd` + rendered `.svg/.png`, `patent/FIGURE_INDEX.md` |
| **Files (modified)** | none outside `patent/` |

**Workflow steps:**

1. **Claim mapping** — `codegraph MCP` → ground each PRD §9 claim to its implementing module (`src/core/demat.py`, orchestrator in `src/agents/orchestrator/agent.py`, `RuleBasedSynthesizer`/EN-SCAF surfaces, conformal output shape in `DiagnosisResponse`) so the detailed description cites real interfaces.
2. **Figures** — `diagram` skill for: (F1) system architecture, (F2) DEMAT loop (prior → entropy → argmax information question → stopping rule), (F3) EN-SCAF arbitration flow incl. conflict coefficient K and UMLS pruning gate, (F4) conformal risk-controlled synthesis, (F5) live execution stepper (playwright MCP screenshot of a real run as evidence for the figure). Each figure visually inspected before acceptance.
3. **Specification draft** — `document-generation` skill per standard provisional structure; every claim in §9 must map to ≥1 figure and ≥1 detailed-description section; terminology consistent with PRD math notation.
4. **Consistency pass** — lint the spec: no placeholder text, no un-mapped claim, all figure refs resolve.
5. **Acceptance gate** — all four claim areas covered by at least one figure and one spec section; figure set renders cleanly (documents:visual-judge pass or recorded fallback); a third-party-style readability pass produces no unresolved "unclear term" notes; explicit disclaimer line in the package that this is a **draft for attorney review**, not a filing.

| Required skills | Why |
|---|---|
| `document-generate` | Spec structure and drafting |
| `diagram` | Patent figures |
| `playwright` MCP | Live UI figure evidence |
| `documents:visual-judge` | Figure legibility acceptance |

---

## Workstream 3.3 — Research Paper Draft (CHIL / MICCAI)

| | |
|---|---|
| **Goal** | A compile-clean paper draft built on benchmark results, targeting CHIL (primary) or a MICCAI workshop (secondary), reusing existing chapters and bibliography |
| **Files (new)** | `paper/phase3-paper/main.tex`, `paper/phase3-paper/sections/*.tex`, `paper/phase3-paper/figures/` (benchmark plots + patent-figure reuse), `paper/phase3-paper/Makefile` |
| **Files (modified)** | `medical_ai_synopsis_revised/References.bib` (only if new sources are added) |

**Workflow steps:**

1. **Venue decision** — `WebSearch` current CHIL/MICCAI workshop calls (dates, anonymization, page limits); record decision + rationale in `findings.md`. Default recommendation: CHIL full paper if the benchmark harness lands with real results; MICCAI workshop format otherwise.
2. **Skeleton** — sections: abstract, intro (reuse `chapter1`), related work (reuse `chapter2`), method (DEMAT/EN-SCAF from PRD §3 + new figure set), experiments (3.1 tables verbatim from `data/benchmarks/results/`), discussion/limitations (synthetic-data caveat retained honestly), conclusion.
3. **Build** — LaTeX compiles, bibliography resolves; figures referenced and legible.
4. **Honesty check** — every quantitative claim in the text must trace to a committed benchmark result file; no "100% accuracy" carried over from the demo-based runner.
5. **Acceptance gate** — `make` in `paper/phase3-paper/` produces the PDF with 0 errors and 0 undefined references; each experiment-section number matches its JSON source; documents:visual-judge (or fallback pass) on rendered pages; planning files updated.

| Required skills | Why |
|---|---|
| `make-pdf`/`document-generate` | LaTeX build and layout conventions |
| `diagram` | Paper figure generation |
| `research` | Venue rules + framing |
| `code-review` (adapted) | Claim-to-evidence trace review |

---

## Workstream 3.4 — Filing & Submission Readiness Package

| | |
|---|---|
| **Goal** | Assemble everything the human executors need: provisional patent filing checklist + conference submission checklist, with drafts in the right formats and gaps explicitly flagged |
| **Files (new)** | `patent/FILING_CHECKLIST.md`, `patent/PATENT_AGENT_BRIEF.md`, `paper/SUBMISSION_CHECKLIST.md` (supersedes root one for Phase 3 items), `patent/specification/` export to `.docx` |
| **Files (modified)** | `SUBMISSION_CHECKLIST.md` (mark Phase 3 items as packaged/blocked-on-user) |

**Workflow steps:**

1. **Jurisdiction decision** — choose primary route: Indian Patent Office (provisional, Form 2 + drawings + fee) vs. USPTO provisional (cover sheet + spec + drawings + fee). Record as decision requiring user confirmation; default IPO given project affiliation.
2. **Package assembly** — spec `.docx` export, figures bundled at filing resolution, inventor/title/abstract metadata sheet; `documents:docx` skill for format requirements.
3. **Counsel brief** — `PATENT_AGENT_BRIEF.md`: one-page technical summary of the four claims, prior-art search terms, and open legal questions (software/medical-device patentability in the chosen jurisdiction).
4. **Conference package** — venue rules checklist: anonymization, page limit, supplemental material, reproduction package (benchmark repo path + seed file).
5. **Acceptance gate** — every checklist item resolves to a file on disk or an explicit `BLOCKED: user action` entry; no item marked done by assertion; planning files updated. **Nothing is filed or submitted — filing is the user's action.**

| Required skills | Why |
|---|---|
| `documents:docx` | Filing-format export |
| `research` | IPO/USPTO + venue procedural accuracy |
| `checklist discipline` (from planning-with-files) | No unchecked claims |

---

## Cross-Cutting Verification Workflow (runs after every workstream merges)

1. `pytest` full suite — must stay at **≥133 passing**; skips unchanged (17, documented XGBoost/py3.13).
2. `cd frontend && npx tsc --noEmit` — 0 errors (Phase 3 should touch no frontend code unless a figure needs a new state; any such change re-verifies).
3. Paper/patent artifacts compile; benchmark harness determinism test passes.
4. Update `.planning/2026-10-05-aegismed-phase-3/progress.md` with evidence paths and measured numbers (not adjectives).

## MCP Service Registry for Phase 3

| MCP service | Invoked for |
|---|---|
| `codegraph` | Grounding each workstream in current code before writing (3.1 step 1, 3.2 step 1) |
| `WebSearch` / `WebFetch` | MedQA dataset details, MIMIC-IV credentialing requirements, CHIL/MICCAI calls |
| `context7` | `datasets`/metric libraries for 3.1 (with the noted key failure fallback) |
| `playwright` | Live screenshot evidence for patent figure F5 and any UI-backed figure |
| `documents:docx` | Patent spec file-format export (3.4) |
| `documents:visual-judge` | Patent figure and paper page acceptance (fallback: direct Read inspection, recorded) |
| `codebase-memory` (optional) | Confirm no Phase 2 surface changes under Phase 3 edits |

## Risks

- **MIMIC-IV credentialing is a human dependency** — cannot be automated; 3.1 proceeds on NIH ChestX-ray14 (already scripted) and marks MIMIC-IV results pending credentials. Never claim MIMIC results without them.
- **Existing 100% synthetic benchmark is misleading** — supersede in docs; do not reuse its numbers anywhere in patent or paper.
- **Patent text is a draft** — medical/software claims need counsel; the repo's deliverable stops at filing-ready draft + checklist.
- **Venue deadlines are outside our control** — venue decision lands in 3.3 step 1 and may shift target from CHIL to a MICCAI workshop.
- **Benchmark runtime** — LLM-backed full-pipeline runs are slow (~20–30s/case at current latency); smoke-test slices and background execution, never run the full set in a foreground verification step.
