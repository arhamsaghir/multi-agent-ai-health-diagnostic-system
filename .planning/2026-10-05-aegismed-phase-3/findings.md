# Phase 3 — Findings (Recon 3.0)

**Date:** 2026-10-05

## Asset inventory (reuse-first)

- `medical_ai_synopsis/` and `medical_ai_synopsis_revised/` — full LaTeX chapter suites, 10+ rendered figures (architecture, pipeline, research gap, timeline), `References.bib` in both. Reuse in 3.2 (patent spec) and 3.3 (paper).
- Chapters in Markdown at repo root: `chapter1_introduction.md` … `chapter8_conclusion.md`, `FULL_PROJECT_REPORT.md` (952 lines), `REPORT_SPEC.md`, `REFERENCES.md` (41 lines).
- `SUBMISSION_CHECKLIST.md` — prior-submission state; superseded for Phase 3 items by this plan's 3.3/3.4.

## Benchmark state (critical)

- `scripts/run_benchmark.py` + `scripts/generate_benchmark_cases.py` produce 200 synthetic cases but evaluate `frontend.pages.diagnosis._get_demo_result` — the **demo rule function**, not the multi-agent pipeline. The claimed 100% Top-1 accuracy (in SUBMISSION_CHECKLIST.md) is not research evidence and must not propagate into the paper or patent.
- Phase 2 evidence that is legitimate: 133 passed / 17 skipped (`pytest`), `npx tsc --noEmit` clean, RAG eval 25/25 top-5 on the fixed query set, SSE endpoint live-verified, PDF endpoint live 200.

## External dependencies (human steps)

- **MIMIC-IV-CXR** requires PhysioNet credentialed access (registration → CITI training → signed DUA). Not automatable. Interim path: NIH ChestX-ray14 public download scripts already in repo (`scripts/download_real_xray_images.py`, `scripts/download_chest_xray.py`).
- **MedQA** is public on HuggingFace (`GBaker/MedQA-USMLE-4-options`); needs task adaptation from MCQ selection to the system's differential outputs and a recorded seed.
- **Patent filing** is a human/legal action with a registered patent agent (PRD sign-off pending). Repo deliverable ends at filing-ready draft + checklist.

## PRD anchors

- Phase 3 bullets: benchmark DEMAT vs MIMIC-IV-CXR & MedQA; draft technical spec + patent diagrams; provisional filing (IPO/USPTO); paper to CHIL/MICCAI.
- Patent claims (§9): 1) DEMAT entropy-minimizing active triage; 2) Dempster-Shafer conflict discounting K; 3) UMLS DAG neuro-symbolic pruning gate; 4) multimodal conformal risk-controlled bounding.
- Claims map to code: `src/core/demat.py` (engine; `start_or_get_session`, `update_belief_from_answer`), orchestrator arbitration (`src/agents/orchestrator/agent.py`), synthesis schema (`DiagnosisResponse` incl. `triage`, `confidence`), conflict surfaces in `src/agents/rule_based_synthesis.py`.

## Tooling notes

- context7 MCP rejected an invalid API key during Phase 2.1 research; if still failing, use standard docs and record the fallback.
- documents:visual-judge subagent provider was unavailable during Phase 2.4; fallback is direct Read inspection of rendered PNGs, logged as such.
