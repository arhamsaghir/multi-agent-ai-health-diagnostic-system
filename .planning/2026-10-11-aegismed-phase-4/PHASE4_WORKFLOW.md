# AegisMed Phase 4 — Production Clinical Pilot & FHIR Integration (Workflow)

**Goal:** Turn the Phase 1–3 verified platform into a deployable, interoperable clinical-pilot build: a bidirectional HL7 FHIR R4 interoperability layer, a corrected containerized on-prem stack, and the documentation/harness scaffolds for IRB clinical validation and a PCT international patent filing.

**PRD scope:** `PRD.md` §10 Phase 4 (Months 4–8).
**Predecessor:** `.planning/2026-10-05-aegismed-phase-3/` (complete, 140 passed / 17 skipped).
**Branch:** continue on `feat/full-stack-integration-and-automations` (no new branch cut unless the user requests one).
**Execution model:** sequential, one workstream at a time, each ending at its own acceptance gate — identical discipline to Phases 2 and 3. Plan is authored first (this document); execution of Workstream 4.1 begins only on explicit user go-ahead.

## Honesty contract (carried from Phase 3)
- No capability is reported as working unless a test or command proves it; a clean programmatic check is the evidence, never prose.
- Items that depend on hardware we do not have (NVIDIA GPU/TensorRT), external approvals (IRB, hospital data), or legal action (PCT filing) are marked `BLOCKED: user action` and delivered as protocols/scaffolds — never simulated.
- The Phase 3 pre-publication novelty embargo remains in force over any new patentable subject matter produced here.

## Workstreams

### Workstream 4.0 — Recon & Baseline  — COMPLETE
Delivered in `findings.md`: asset inventory, buildable-vs-blocked split, risks. Confirmed FHIR is greenfield, the Docker frontend service is broken legacy (Streamlit vs. the real Next.js app), and TensorRT INT8 is hardware-blocked on Darwin arm64.

### Workstream 4.1 — HL7 FHIR R4 Interoperability Layer  (AUTONOMOUS)
Bidirectional FHIR R4 at the API edge, wrapping the existing orchestrator without touching core logic.
- 4.1.1 Add `fhir.resources` (R4) to `requirements.txt`; pin version.
- 4.1.2 `src/core/fhir_mapping.py`: map an inbound `Bundle` (Patient + symptom `Observation`/`Condition`) into the orchestrator's `DiagnosisRequest`; map a `DiagnosisResponse` outward into a FHIR `Bundle` (Patient, `Condition` differential ranked by probability, `RiskAssessment` for the conformal/triage output, `Observation` for triage entropy, `DocumentReference` for the narrative).
- 4.1.3 `src/api/routes/fhir.py`: `POST /api/fhir/diagnose` (consume a Bundle → run pipeline → return a Bundle) and `GET /api/fhir/diagnosis/{id}` (export a persisted history record as a Bundle); register the router in `src/api/main.py`.
- 4.1.4 Validate every emitted resource against the `fhir.resources` R4 models (construction-time validation) and round-trip (export → re-import → equivalent request).
- 4.1.5 Acceptance: `tests/unit/test_fhir_mapping.py` + `tests/test_fhir_endpoints.py` green; full suite ≥ 140 prior passes + new tests, 0 regressions; a synthetic Bundle flows end-to-end through the live app.

### Workstream 4.2 — Containerized On-Prem Deployment  (AUTONOMOUS; INT8 partial)
- 4.2.1 Rewrite `docker-compose.yml`: replace the broken `streamlit run frontend/app.py` service with a Next.js frontend service (`next build` → `next start`, port 3000) and keep the FastAPI service (port 8000); wire `API_URL`/`NEXT_PUBLIC_*` and healthchecks.
- 4.2.2 Add `frontend/Dockerfile` (Node multi-stage build) and fix the root `Dockerfile` (drop stale 8501; keep 8000; non-root user).
- 4.2.3 Add `.dockerignore` (exclude `venv*`, `.git`, `node_modules`, `*.log`, iCloud/`.nosync`, planning/report scratch).
- 4.2.4 ONNX export scaffold `scripts/deploy/export_onnx.py` (CPU `torch.onnx.export` of the ResNet vision model) + a documented, `BLOCKED`-tagged TensorRT INT8 calibration runbook for a GPU host.
- 4.2.5 Acceptance: `docker compose config` validates; image builds are defined and lint-clean; ONNX export unit-tested on CPU with `onnxruntime` parity check against the torch forward pass; TensorRT step explicitly `BLOCKED: GPU host`.

### Workstream 4.3 — Retrospective IRB Clinical Validation  (BLOCKED: external)
- 4.3.1 Author `clinical/VALIDATION_PROTOCOL.md`: retrospective design, inclusion/exclusion, endpoints (Top-k, calibration, decision-impact), sample-size rationale, de-identification/Safe-Harbor plan.
- 4.3.2 Design (not run) a validation harness interface reusing `scripts/benchmark/metrics.py` against a FHIR-ingested cohort.
- 4.3.3 Author IRB submission templates (protocol synopsis, data-use agreement checklist, consent-waiver justification for retrospective de-identified data).
- 4.3.4 Acceptance: every item is a verified repo file or an explicit `BLOCKED: user action` (IRB approval + hospital data) — zero simulated patient results.

### Workstream 4.4 — Global PCT International Patent Application  (BLOCKED: legal)
- 4.4.1 Author `patent/PCT_FILING_CHECKLIST.md`: PCT route via IPO/USPTO Receiving Office, 12-month Paris priority anchor from the Phase 3 provisional, 30-month national-phase map.
- 4.4.2 Extend the claim set with FHIR-interoperability embodiments produced in 4.1 (new dependent claims) in a draft addendum for counsel.
- 4.4.3 Acceptance: checklist maps each step to a file or `BLOCKED: user action`; filing strictly gated on the provisional application number existing first; embargo preserved.

## MCP / tooling registry
- `codebase-memory` / `codegraph` — code grounding (note: codegraph index returned a stale unrelated hit on 2026-10-11; fall back to targeted Read/Grep when it mismatches).
- `context7` — FHIR R4 / `fhir.resources` and `torch.onnx` doc lookups during 4.1/4.2.
- Standard libs — `fhir.resources`, `onnx`, `onnxruntime`, `pytest`.

## Required skills
- `tdd` / `superpowers:test-driven-development` — write failing tests first for 4.1 mapping and endpoints.
- `verify` / `superpowers:verification-before-completion` — acceptance gates.
- `verify-live-on-localhost` discipline (memory) — exercise `/api/fhir/*` against the running app before declaring 4.1 done.

## Global acceptance gate (phase close)
All autonomous workstreams (4.1, 4.2) green with no suite regression; all blocked workstreams (4.3, 4.4, TensorRT INT8) delivered as verified scaffolds/protocols with explicit `BLOCKED` tags; novelty embargo intact; `progress.md` updated per workstream.
