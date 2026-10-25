# AegisMed — Phase 2 Planning Workflow

**Date:** 2026-10-05
**Branch:** `feat/full-stack-integration-and-automations` → new branch `feat/phase-2-clinical-differentiators`
**Predecessor:** `.planning/2026-10-04-aegismed-phase-1-implementation/` (Grad-CAM, DEMAT, OmniRoute — all verified, 110 tests passing)
**PRD reference:** `PRD.md`, Phase 2 scope

This document is the Phase 2 **planning workflow**: it states, for every workstream, (a) what gets built, (b) which **MCP services** the agent invokes at each step, (c) which **skills** are required, and (d) the acceptance gate that must pass before the workstream closes.

---

## 0. Workflow Conventions

- One workstream at a time; no parallel feature work inside Phase 2.
- Every workstream ends at its **acceptance gate** — build green (`pytest`, `npx tsc --noEmit`), live verification via browser MCP, planning files updated.
- All codebase exploration goes through the **codegraph MCP** (`codegraph_explore`). No blind grep/read sweeps.
- All library/API questions go through **context7 MCP** before writing integration code.
- All UI verification goes through **playwright MCP** (browser_navigate → evaluate → screenshot) at 554×900 and 1280×800.
- Session state is tracked in `.planning/2026-10-05-aegismed-phase-2/` (`task_plan.md`, `findings.md`, `progress.md`) per the `planning-with-files` methodology.

---

## Workstream 2.0 — Recon & Baseline (status: DONE — executed during plan authoring)

| | |
|---|---|
| **Goal** | Confirm current architecture facts the workstreams build on |
| **MCP services invoked** | `codegraph MCP` → `codegraph_explore` (diagnosis UI graph: `DiagnosisPage → DiagnosisResults/SymptomInput/FollowUpQuestions`; backend: `OrchestratorAgent._node_*` LangGraph nodes; `RAGAgent._search_faiss`, `ingest_documents`) |
| **Skills used** | `planning-with-files` (session files), `understand` (repo orientation) |

**Findings that shape Phase 2:**

1. **No streaming exists.** The orchestrator runs `run()` → `_run_sequential()` over graph nodes and returns one final response. The execution stepper (2.1) therefore needs a new **SSE progress endpoint** that emits per-node events — the UI cannot fake this reliably.
2. **`DiagnosisResults` already has the loading state seam.** `LoadingSkeleton` (diagnosis/DiagnosisResults.tsx:258) is the exact component the live stepper replaces during runs.
3. **Persona toggle data is already present, split across two fields.** `/refine` returns both `explanation` (clinical) and `patient_explanation` (plain-language). No new backend generation is needed for 2.2 — only plumbing + a view switcher.
4. **RAG ingestion path already exists.** `RAGAgent.ingest_documents()` (src/agents/rag/agent.py:194) plus `scripts/ingest_medical_knowledge.py` handle persistence — 2.3 is a curation + batch-ingest task, not new infrastructure.
5. **No PDF/reporting layer exists anywhere.** 2.4 introduces it fresh: backend render + frontend download trigger.

---

## Workstream 2.1 — Live Multi-Agent Execution Stepper

| | |
|---|---|
| **Goal** | During a diagnosis run, the UI shows each agent (NLP → Vision → RAG → Prediction → Synthesis, plus DEMAT arbitration) as an animated step with live status: queued → running → done/failed, with per-agent elapsed time |
| **Files (new)** | `src/api/routes/stream.py` (SSE endpoint), `frontend/src/components/diagnosis/AgentExecutionStepper.tsx` |
| **Files (modified)** | `src/agents/orchestrator/agent.py` (emit progress events from each `_node_*` handler), `src/api/main.py` (mount route), `frontend/src/lib/api.ts` (`streamDiagnosis()` via `EventSource`/fetch-stream), `frontend/src/app/diagnosis/page.tsx` (replace `isLoading` skeleton with the stepper) |

**Workflow steps:**

1. **Ground** — `codegraph MCP` → `codegraph_explore("run _run_sequential _node_nlp_analysis _node_rag_retrieval _node_prediction")` to pin exact event-emission points inside the orchestrator's sequential executor.
2. **Research the transport** — `context7 MCP` → resolve `FastAPI` docs for `StreamingResponse` / SSE and Next.js client-side stream consumption; decide SSE over WebSocket (unidirectional; SSE is sufficient and simpler).
3. **Backend events** — add a per-run event queue (`asyncio.Queue` keyed by `run_id`); each `_node_*` handler publishes `{agent, status, elapsed_ms, summary}` at start/finish/fail; new endpoint `GET /api/diagnosis/stream/{run_id}` drains the queue as SSE.
4. **Frontend stepper** — animated vertical step rail with status rings (pending/running spinner/done check/fail cross), agent icons matching the landing page set, elapsed-time readouts, final "arbitration complete" state handing off to `DiagnosisResults`.
5. **Acceptance gate** — new pytest for the SSE endpoint (events ordered, terminal event emitted); `tsc` clean; playwright MCP live run at both viewports showing all five agents animate during a real diagnosis; planning files updated.

| Required skills | Why |
|---|---|
| `implement` | Backend SSE + orchestrator event plumbing |
| `frontend-design` | Stepper interaction/motion spec |
| `tdd` | SSE event-ordering tests written first |
| `design-review` | Post-implementation visual pass via playwright MCP |

---

## Workstream 2.2 — Clinician / Patient Dual-Mode Persona Toggle

| | |
|---|---|
| **Goal** | One toggle on the results (and chat) views switches every rendered artifact between **patient mode** (plain language, no jargon, `patient_explanation`) and **clinician mode** (ICD-10 codes, ESI triage level, confidence intervals, `explanation` + `differential_diagnoses`) |
| **Files (new)** | `frontend/src/components/ui/PersonaToggle.tsx`, `frontend/src/lib/persona.tsx` (React context) |
| **Files (modified)** | `frontend/src/components/diagnosis/DiagnosisResults.tsx` (dual rendering), `frontend/src/lib/api.ts` (carry `icd10_code`, `rationale`, `patient_explanation` through `transformAPIResponse`), `frontend/src/app/layout.tsx` (context provider + toggle in header), `src/api/routes/diagnosis.py` (guarantee both fields always populated) |

**Workflow steps:**

1. **Ground** — `codegraph MCP` → `codegraph_explore("DiagnosisResponse explanation patient_explanation differential_diagnoses icd10")` to lock the response schema both modes render from.
2. **Schema check** — verify `/analyze` and `/refine` always return both explanation flavors; add a fallback composer when the LLM omits one (reuse `RuleBasedSynthesizer`).
3. **Context + toggle** — app-wide `PersonaProvider` persisting to `localStorage`; pill toggle in the mobile header and desktop sidebar footer.
4. **Dual rendering** — patient mode: narrative, plain recommendations, rounded reassurance tone; clinician mode: ICD-10 chips, per-differential `confidence` + `rationale`, ESI badge, red-flag table.
5. **Acceptance gate** — unit test that both response fields are present in all endpoint payloads; playwright MCP toggles the switch on a real result and screenshots both modes at both viewports.

| Required skills | Why |
|---|---|
| `frontend-design` | Two coherent visual languages from one data model |
| `implement` | Context provider + schema plumbing |
| `code-review` | Accessibility check (toggle discoverability, contrast) |

---

## Workstream 2.3 — RAG Knowledge Base Expansion (10 → 500+ documents)

| | |
|---|---|
| **Goal** | Replace the 4-symptom `_fallback_knowledge` dict and the tiny seed store with 500+ curated, cited clinical practice guideline summaries, indexed in FAISS via the existing `ingest_documents()` path |
| **Files (new)** | `data/knowledge/guidelines/*.json` (curated corpus), `scripts/curate_guidelines.py` (fetch/normalize/dedupe/cite), expanded `scripts/ingest_medical_knowledge.py` batches |
| **Files (modified)** | `src/agents/rag/agent.py` (source-citation passthrough, retrieval score threshold tuning), `tests/unit/test_rag_agent.py` (corpus-size + citation assertions) |

**Workflow steps:**

1. **Corpus sourcing** — `WebSearch` + `WebFetch` against public guideline sources (WHO, CDC, NICE, StatPearls open summaries); each document normalized to `{content, source, icd10, last_reviewed}`.
2. **Library check** — `context7 MCP` → `sentence-transformers` / `faiss` docs to confirm batch-encoding and index-rebuild patterns for the larger corpus.
3. **Ingestion** — run curated corpus through `RAGAgent.ingest_documents()` in batches; rebuild `medical_knowledge.faiss` + metadata JSON; record document count and per-source distribution.
4. **Quality gate** — retrieval eval: a fixed set of 25 symptom queries must return a relevant guideline in top-5 ≥ 90% of the time; measure and log per-query top-1 score distribution.
5. **Acceptance gate** — store loads with ≥ 500 documents (asserted by test); eval harness passes; `/api/diagnosis/refine` answers cite real `source` values end-to-end (verified via playwright MCP on one live query).

| Required skills | Why |
|---|---|
| `research` | Guideline corpus sourcing with citations |
| `benchmark` | Retrieval quality harness (top-k hit rate) |
| `tdd` | Corpus integrity tests |

---

## Workstream 2.4 — One-Click Clinical PDF Consultation Report

| | |
|---|---|
| **Goal** | "Download Report" on the diagnosis results view produces a branded PDF: patient context, DEMAT entropy trajectory, differentials with confidence bars, agent execution trace, Grad-CAM image embeds (when present), red flags, and disclaimer footer |
| **Files (new)** | `src/services/report.py` (ReportLab/fpdf2 renderer), `src/api/routes/report.py` (`POST /api/report/generate`), `frontend/src/components/diagnosis/ReportButton.tsx` |
| **Files (modified)** | `frontend/src/components/diagnosis/DiagnosisResults.tsx` (button placement), `frontend/src/lib/api.ts` (`downloadReport()`) |

**Workflow steps:**

1. **Library decision** — `context7 MCP` → compare `reportlab` vs `fpdf2` docs; pick the one with mature table/image support (default: `reportlab`).
2. **Backend renderer** — assemble the report from the `DiagnosisResponse` JSON + optional base64 heatmap; deterministic template, no LLM in the render path.
3. **Frontend trigger** — button on results page; `fetch` → blob → object-URL download; loading + error states.
4. **Visual gate** — render the PDF to page PNGs and run the **documents:visual-judge MCP agent** as the acceptance pass (layout, typography, no overflow); iterate until all pages pass.
5. **Acceptance gate** — pytest for `POST /api/report/generate` (200, `application/pdf`, non-trivial byte size); visual-judge verdict clean; playwright MCP verifies the download flow end-to-end.

| Required skills | Why |
|---|---|
| `document-generate` | Report template structure |
| `documents:docx` knowledge (patterns) | Sectioning/tables conventions reused for PDF |
| `implement` | Route + renderer |
| `make-pdf` (reference) | Output conventions |

---

## Cross-Cutting Verification Workflow (runs after every workstream merges)

1. `pytest` full suite — must hold at 110+ passing (new tests add to, never subtract).
2. `cd frontend && npx tsc --noEmit` — 0 errors.
3. Restart backend + frontend; **playwright MCP** smoke path: `/` → `/diagnosis` full DEMAT run → stepper animates → toggle both personas → download PDF → `/vision` Grad-CAM still renders.
4. Update `.planning/2026-10-05-aegismed-phase-2/progress.md` with evidence (screenshot paths, test output).

## MCP Service Registry for Phase 2

| MCP service | Invoked for |
|---|---|
| `codegraph` | All codebase grounding before edits (workstreams 2.1–2.4, step 1) |
| `context7` | FastAPI SSE, Next.js streaming, sentence-transformers/faiss, reportlab/fpdf2 docs |
| `playwright` | Live UI verification at 554×900 and 1280×800 after each workstream |
| `documents:visual-judge` | PDF report page acceptance (2.4 step 4) |
| `WebSearch` / `WebFetch` | Guideline corpus sourcing (2.3 step 1) |
| `codebase-memory` (optional) | Impact radius re-check before merging 2.1's orchestrator changes |

## Risks

- **SSE vs. the current one-shot `analyze` contract** — mitigated by keeping `/analyze` untouched and adding streaming as an opt-in parallel endpoint; frontend falls back to the skeleton if the stream errors.
- **Corpus licensing** — only government/CC-BY guideline sources; each document carries its `source` string into retrieval results.
- **PDF payload size with heatmaps** — compress embeds to JPEG q80 inside the renderer; assert report < 2 MB in tests.
