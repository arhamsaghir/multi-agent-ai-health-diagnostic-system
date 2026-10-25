# Phase 4 — Findings & Recon (Workstream 4.0)

**Date:** 2026-10-11
**Scope source:** `PRD.md` §10 — "PHASE 4: PRODUCTION CLINICAL PILOT & FHIR INTEGRATION (Months 4–8)".
**Predecessor:** Phase 3 complete & verified (`.planning/2026-10-05-aegismed-phase-3/`). Suite baseline **140 passed / 17 skipped**.

PRD-stated Phase 4 bullets: (a) bidirectional HL7 FHIR R4 Bundle import/export; (b) containerized on-premise Docker stack with TensorRT INT8; (c) retrospective IRB-approved hospital data validation; (d) file global PCT International Patent Application.

## Asset Inventory (grounded on disk)

| Area | Current state | Implication for Phase 4 |
|---|---|---|
| **FHIR / HL7** | Zero references anywhere in `src/`, `config/`, `scripts/` (grep clean) | **Greenfield, fully buildable autonomously.** 4.1 is the crown-jewel workstream. |
| **API response schemas** | `DiagnosisResponse` (`src/api/routes/diagnosis.py:65`), `VisionResponse` (`vision.py:13`), history `DiagnosisItem` (`history.py:13`), `ReportRequest` (`report.py:12`) | These are the source objects to map into FHIR resources (Condition / Observation / RiskAssessment / ImagingStudy). |
| **Route surface** | `chat, diagnosis, history, report, stream, vision` under `src/api/routes/` | FHIR facade adds a new `src/api/routes/fhir.py` wrapping the existing orchestrator; no rewrite of core needed. |
| **Dockerfile** | `python:3.11-slim`, `EXPOSE 8000 8501`, `CMD uvicorn ...` | API image base is sound; port 8501 is a stale Streamlit artifact. |
| **docker-compose.yml** | `frontend` service runs `streamlit run frontend/app.py` | **BROKEN/LEGACY** — the frontend is Next.js, and `frontend/app.py` does not exist. 4.2 must rewrite the compose stack for Next.js + FastAPI. |
| **.dockerignore** | **Missing** | Image build would copy `venv.nosync/`, `.git/`, `node_modules/`, iCloud artifacts → bloated/incorrect image. 4.2 must add one. |
| **Frontend** | Next.js (`frontend/package.json` scripts: `next dev/build/start`; `frontend/server.js` present) | Container for the frontend is a Node/Next build, not Streamlit. |
| **Vision model** | `src/agents/vision/agent.py` loads ResNet-18/50 `state_dict` via `torch.load(..., map_location="cpu")`, `model.eval()` | ONNX export via `torch.onnx.export` is feasible/testable on CPU. |
| **Platform** | Darwin arm64; `torch==2.5.1`, no CUDA | **TensorRT INT8 is hardware-blocked here** (NVIDIA-only). Autonomous slice = ONNX export + CPU dynamic quantization; TensorRT calibration deferred to GPU host. |
| **Deps** | `fastapi 0.115.6`, `pydantic 2.10.4`, `torch 2.5.1`; no `fhir.resources`, no `onnx` | 4.1 adds `fhir.resources` (R4); 4.2 adds `onnx`/`onnxruntime` for the export scaffold. |

## Buildable-vs-Blocked split (mirrors Phase 3's honesty discipline)

- **Fully autonomous (code + tests + acceptance gate):** 4.1 FHIR R4 import/export; 4.2 Docker stack correction + `.dockerignore` + ONNX export scaffold.
- **`BLOCKED: user action` (documented, not simulated):**
  - TensorRT INT8 calibration — requires an NVIDIA GPU host; cannot run on Darwin arm64. ONNX artifact prepared; INT8 build steps documented for the GPU host.
  - 4.3 Retrospective IRB clinical validation — requires IRB approval + real (de-identified) hospital data under a data-use agreement. Deliver the protocol, metrics harness design, and IRB documentation templates; the data run itself is blocked.
  - 4.4 Global PCT application — legal action, and strictly gated on the Phase 3 provisional being filed first (priority anchor). Deliver the PCT readiness checklist and 30-month national-phase map; filing is blocked.

## Risks / constraints carried forward
- **Novelty embargo (from Phase 3):** the FHIR interoperability layer is additional patentable subject matter candidate; keep it inside the same embargo until the provisional application number is secured.
- **venv fragility:** `venv -> venv.nosync` symlink must stay intact; never read pytest exit through `| tail` (see `.planning/2026-10-05-aegismed-phase-3/progress.md` 2026-10-11 entry).
- **No PHI on this machine:** all 4.1/4.2 tests use synthetic FHIR bundles and the existing synthetic benchmark fixtures only.
