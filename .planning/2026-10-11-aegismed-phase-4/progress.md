# Phase 4 — Progress Log

## 2026-10-11 — Plan authored; Workstream 4.0 (Recon) complete

- Authored the Phase 4 planning package following the same `.planning/` convention as Phases 2–3: `PHASE4_WORKFLOW.md` (workstreams 4.0–4.4, MCP registry, required skills, acceptance gates, honesty contract), `task_plan.md`, `findings.md`.
- Recon (4.0) delivered in `findings.md`:
  - **FHIR/HL7 is greenfield** — zero references in `src/`, `config/`, `scripts/`. The 4.1 interoperability layer is the primary buildable workstream.
  - **Docker stack is broken legacy** — `docker-compose.yml` runs `streamlit run frontend/app.py`, but the frontend is Next.js (`frontend/package.json`: `next dev/build/start`) and `frontend/app.py` does not exist. No `.dockerignore` present. 4.2 must correct both.
  - **TensorRT INT8 is hardware-blocked** on Darwin arm64 (`torch==2.5.1`, no CUDA). Autonomous slice = ONNX export + CPU parity test; INT8 calibration documented for a GPU host as `BLOCKED`.
  - **API response schemas** (`DiagnosisResponse`, `VisionResponse`, history `DiagnosisItem`) are the mapping sources for FHIR resources; the vision model (`src/agents/vision/agent.py`) loads a ResNet-18/50 state_dict on CPU, so `torch.onnx.export` is feasible.
  - IRB validation (4.3) and PCT filing (4.4) are `BLOCKED: external/legal` and will be delivered as protocols/scaffolds, never simulated. Phase 3 novelty embargo remains in force over the new FHIR subject matter.
- Baseline reconfirmed from the Phase 3 close: **140 passed / 17 skipped**, `venv -> venv.nosync` symlink healthy.

### Next Action
- Execute Workstream 4.1 (FHIR R4 interoperability) test-first: `fhir.resources` dependency, `src/core/fhir_mapping.py`, `src/api/routes/fhir.py`, with `tests/unit/test_fhir_mapping.py` and `tests/test_fhir_endpoints.py`.

## 2026-10-11 — Workstream 4.1: HL7 FHIR R4 Interoperability Layer — COMPLETE

### Delivered
- `fhir.resources==8.3.0` pinned in `requirements.txt` (pydantic-v2 compatible; R4 resources via the `fhir.resources.R4B` subpackage).
- `src/core/fhir_mapping.py` — edge-facade mapping (no change to DEMAT/EN-SCAF core):
  - `bundle_to_diagnosis_request()`: inbound R4 `Bundle` → orchestrator `DiagnosisRequest` dict. Symptom text gathered from `Observation` (`valueString`, else coded `text`/`display`) and `Condition.code.text`; demographics (gender, computed age from `birthDate`) from `Patient`. Raises `ValueError` when no symptom text is present (→ HTTP 400).
  - `diagnosis_response_to_bundle()`: `DiagnosisResponse` → R4 `Bundle` with `Patient`, one ranked `Condition` per differential (confidence noted), a `RiskAssessment` (per-outcome `probabilityDecimal` + triage severity note), an entropy `Observation` (`valueQuantity` bits, from `triage.entropy_bits`), and a `DocumentReference` carrying the clinician narrative + disclaimer (base64 text).
  - `session_to_bundle()`: persisted history session record → R4 `Bundle`.
- `src/api/routes/fhir.py` — `POST /api/fhir/diagnose` (Bundle in → pipeline → Bundle out, `application/fhir+json`) and `GET /api/fhir/diagnosis/{session_id}` (export persisted record); registered in `src/api/main.py`.
- Tests: `tests/unit/test_fhir_mapping.py` (10) + `tests/test_fhir_endpoints.py` (5) — inbound extraction, outbound structure, RiskAssessment probabilities, entropy Observation, narrative round-trip (base64 decode), differential fallback, export→import equivalence, 400 on empty/malformed Bundle, 404 on missing session.

### Fixes during build
- R4B `RiskAssessment` has no `comment` field (that was STU3); switched the triage-severity annotation to `note=[{text}]`.
- Corrected a test fixture: FHIR `Observation` requires a mandatory `code`; added it (a `valueString`-only Observation is invalid R4 and correctly 400s).

### Acceptance gate — MET
- New FHIR tests: 15 passed, exit 0.
- Full suite: **155 passed / 17 skipped, exit 0** (380s) = prior 140 + 15 new, **0 regressions**.
- Endpoint integration exercised through the real ASGI app (`src.api.main:app`) via `TestClient` with a stubbed pipeline; FHIR serialization validated by the `fhir.resources` R4B models at construction time.

### Next Action
- Workstream 4.2 (Containerized On-Prem Deployment): rewrite `docker-compose.yml` for Next.js + FastAPI, add `frontend/Dockerfile` + `.dockerignore`, fix root `Dockerfile`, and add the CPU ONNX export scaffold (`scripts/deploy/export_onnx.py`) with the TensorRT INT8 runbook tagged `BLOCKED: GPU host`.
