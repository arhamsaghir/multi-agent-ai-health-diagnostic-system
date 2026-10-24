# AegisMed Phase 4 — Task Plan

**Goal:** Deliver a deployable, interoperable clinical-pilot build — HL7 FHIR R4 interoperability, a corrected containerized stack, and IRB/PCT scaffolds — on the Phase 1–3 verified base.

**Plan doc:** `PHASE4_WORKFLOW.md` in this directory. **Recon:** `findings.md`.
**PRD scope:** `PRD.md` §10 Phase 4. **Branch:** `feat/full-stack-integration-and-automations`.
**Execution order:** sequential, one workstream at a time, each ending at its acceptance gate.

## Next Step

Workstream 4.1 (FHIR R4 interoperability) is complete and gated (155 passed / 17 skipped, 0 regressions). Execute **Workstream 4.2 — Containerized On-Prem Deployment** next.

## Current Phase

### Workstream 4.2 — Containerized On-Prem Deployment
**Status:** pending (next)

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
**Status:** pending
- [ ] 4.2.1 Rewrite `docker-compose.yml` for Next.js frontend (3000) + FastAPI (8000) with healthchecks.
- [ ] 4.2.2 `frontend/Dockerfile` (Node multi-stage) + fixed root `Dockerfile` (non-root, drop 8501).
- [ ] 4.2.3 `.dockerignore`.
- [ ] 4.2.4 `scripts/deploy/export_onnx.py` (CPU) + TensorRT INT8 runbook tagged `BLOCKED: GPU host`.
- [ ] 4.2.5 Acceptance: `docker compose config` valid; ONNX parity test vs torch forward pass green.

### Workstream 4.3 — Retrospective IRB Clinical Validation
**Status:** pending (BLOCKED: external — IRB + hospital data)
- [ ] 4.3.1 `clinical/VALIDATION_PROTOCOL.md`.
- [ ] 4.3.2 Validation harness interface design (reuses `scripts/benchmark/metrics.py`).
- [ ] 4.3.3 IRB submission templates.
- [ ] 4.3.4 Acceptance: every item a file or explicit `BLOCKED: user action`; no simulated patient results.

### Workstream 4.4 — Global PCT International Patent Application
**Status:** pending (BLOCKED: legal — gated on provisional filing first)
- [ ] 4.4.1 `patent/PCT_FILING_CHECKLIST.md` (30-month national-phase map, Paris priority anchor).
- [ ] 4.4.2 FHIR-interoperability dependent-claim addendum for counsel.
- [ ] 4.4.3 Acceptance: checklist maps to files or `BLOCKED`; embargo preserved.

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
