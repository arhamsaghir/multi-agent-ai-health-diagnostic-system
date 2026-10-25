# AegisMed Phase 4 — Task Plan

**Goal:** Deliver a deployable, interoperable clinical-pilot build — HL7 FHIR R4 interoperability, a corrected containerized stack, and IRB/PCT scaffolds — on the Phase 1–3 verified base.

**Plan doc:** `PHASE4_WORKFLOW.md` in this directory. **Recon:** `findings.md`.
**PRD scope:** `PRD.md` §10 Phase 4. **Branch:** `feat/full-stack-integration-and-automations`.
**Execution order:** sequential, one workstream at a time, each ending at its acceptance gate.

## Next Step

**Phase 4 is closed.** Autonomous workstreams 4.1 and 4.2 are complete and gated; 4.3 and 4.4 are delivered as verified scaffolds with explicit `BLOCKED` tags. Everything remaining is user action (statutory filings, IRB, OpenReview) — see `progress.md` blocked-item registers.

## Current Phase

### Workstream 4.2 — Containerized On-Prem Deployment
**Status:** complete (verified live 2026-10-25)

## Phases

### Workstream 4.0 — Recon & Baseline
**Status:** complete (see `findings.md`)
- [x] Inventoried FHIR (greenfield), API schemas, Docker stack (broken Streamlit service), vision model loader, platform (Darwin arm64, no CUDA), deps.
- [x] Buildable-vs-blocked split established; embargo + venv fragility risks carried forward.

### Workstream 4.1 — HL7 FHIR R4 Interoperability Layer
**Status:** complete
- [x] 4.1.1 Add pinned `fhir.resources==8.3.0` (R4 via `fhir.resources.R4B`).
- [x] 4.1.2 `src/core/fhir_mapping.py` — inbound Bundle → `DiagnosisRequest`; `DiagnosisResponse` → outbound Bundle (Patient, ranked `Condition`, `RiskAssessment`, triage `Observation`, narrative `DocumentReference`); plus `session_to_bundle`.
- [x] 4.1.3 `src/api/routes/fhir.py` — `POST /api/fhir/diagnose`, `GET /api/fhir/diagnosis/{id}`; registered in `src/api/main.py`.
- [x] 4.1.4 R4B model validation + export→import round-trip equivalence (tested).
- [x] 4.1.5 Acceptance: 15 new tests green; full suite **155 passed / 17 skipped**, 0 regressions.

### Workstream 4.2 — Containerized On-Prem Deployment
**Status:** verifying (final acceptance evidence pending)
- [x] 4.2.1 Rewrite `docker-compose.yml` for Next.js frontend (3000) + FastAPI (8000) with healthchecks.
- [x] 4.2.2 `frontend/Dockerfile` (Node multi-stage) + fixed root `Dockerfile` (non-root `USER aegismed`, drop 8501).
- [x] 4.2.3 `.dockerignore` (root + frontend).
- [x] 4.2.4 `scripts/deploy/export_onnx.py` (CPU) + TensorRT INT8 runbook tagged `BLOCKED: GPU host`.
- [x] 4.2.5 Acceptance: `docker compose config` valid; ONNX parity vs torch forward pass **2.6e-06** (tol 1e-4); contract tests 28 green; full suite **197 passed / 17 skipped**; live stack healthy with non-root PID 1, key enforcement, cross-origin guard, and a full DEMAT diagnosis flow through the portal proxy.

### Workstream 4.3 — Retrospective IRB Clinical Validation
**Status:** complete as scaffold (`BLOCKED: external`)
- [x] 4.3.1 `clinical/VALIDATION_PROTOCOL.md` — retrospective design, cohort criteria, endpoints E1–E6, sample-size rationale (n≥350 paired, McNemar), Safe-Harbor de-identification plan, blocked-item register.
- [x] 4.3.2 `clinical/VALIDATION_HARNESS_DESIGN.md` — `CohortSource`/`run_validation` interface reusing `scripts/benchmark/metrics.py`; synthetic smoke-run requirement, never quotable as evidence.
- [x] 4.3.3 `clinical/IRB_SUBMISSION_TEMPLATES.md` — protocol synopsis, DUA checklist, consent-waiver justification, submission checklist.
- [x] 4.3.4 Acceptance: every item is a repo file or explicit `BLOCKED: user action`; zero simulated patient results.

### Workstream 4.4 — Global PCT International Patent Application
**Status:** complete as scaffold (`BLOCKED: legal`)
- [x] 4.4.1 `patent/PCT_FILING_CHECKLIST.md` — RO choice (IPO default / USPTO alt), `D0`+12-month Paris window, `D0`+30-month national-phase map (8 offices), cost anchors, embargo schedule through publication.
- [x] 4.4.2 `patent/FHIR_INTEROP_CLAIM_ADDENDUM.md` — 6 draft dependent claims (A–F) covering the 4.1 FHIR embodiments with claims→code→tests traceability and §3(k)/§101 technical-effect notes for counsel.
- [x] 4.4.3 Acceptance: checklist maps each step to a file or `BLOCKED`; filing strictly gated on the provisional application number; embargo preserved.

## Decisions Made

| Decision | Rationale |
|---|---|
| Continue on existing branch, no new cut | Phase 3 work is uncommitted on this branch; avoid fragmenting history until the user directs commits |
| FHIR layer as an edge facade, not a core rewrite | Keeps the patented DEMAT/EN-SCAF engines untouched; interoperability is additive and independently testable |
| ONNX-on-CPU as the autonomous INT8 slice | TensorRT INT8 needs an NVIDIA GPU absent on Darwin arm64; ONNX export is testable now, INT8 documented for the GPU host |
| IRB validation & PCT delivered as scaffolds | External approvals/legal action cannot be simulated; mirrors Phase 3's `BLOCKED: user action` honesty discipline |

## Errors Encountered

| Error | Attempt | Resolution |
|---|---|---|
| codegraph_explore returned a stale unrelated file (origo_permission_letter.py) for an on-topic query | observed 2026-10-11 | Fell back to targeted Read/Grep for grounding; noted in `findings.md` and workflow MCP registry |
