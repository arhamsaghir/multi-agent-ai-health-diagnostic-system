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

## 2026-10-25 — Workstream 4.2: Containerized On-Prem Deployment — verifying (acceptance evidence below)

### Delivered
- `docker-compose.yml` rewritten: `api` (FastAPI, published on `127.0.0.1:8000` only) + `frontend` (Next.js 16 standalone, `:3000`, waits on API health); healthchecks on both; no Streamlit anywhere.
- `frontend/Dockerfile`: node:22-alpine multi-stage (`npm ci` → `npm run build` → standalone), non-root `nextjs` uid 10001, `HEALTHCHECK` via node fetch; `next.config.ts` sets `output: "standalone"`.
- Root `Dockerfile` fixed: python:3.12-slim, CPU-only PyTorch from `requirements-container.txt`, non-root `USER aegismed` (uid 10001), model weights staged from the host mount into `/var/lib/aegismed/models` by `docker/entrypoint.sh` (works around the Errno 35 bind-mount file-lock failure on macOS mounts), `HEALTHCHECK` on `/health`.
- `docker/entrypoint.sh`: stages weights as the unprivileged user, **refuses to start when a mounted weight exists but is unreadable** (no silent rule-based degradation), warns on an empty model dir, still drops privileges if an operator starts it as root.
- `.dockerignore` (root + frontend): secrets, weights, datasets, logs, venv, node_modules, planning/report scratch excluded from build context.
- `frontend/src/app/api/backend/[...path]/route.ts`: same-origin proxy — forwards browser calls to `BACKEND_URL` with the server-side `X-API-Key` (browser never holds the key), streams SSE through, and **rejects cross-site browser requests** (`Origin` must match `Host`, or be listed in `ALLOWED_ORIGINS`) because the proxy is a privileged relay.
- `scripts/deploy/export_onnx.py`: CPU `torch.onnx.export` of the vision model with a mandatory parity gate vs the torch forward pass (default tolerance 1e-4) and a `.metadata.json` audit sidecar (arch, opset, SHA-256).
- `scripts/deploy/prepare_models.py`: host preflight — materialises iCloud-evicted files, load-tests every checkpoint/estimator, and checks the mounts are accessible to container uid 10001 (blocking on Linux, advisory on macOS where Docker Desktop maps bind-mount permissions); `--fix-permissions` chmods weights readable and attempts the data/logs chown.
- `docs/deploy/CONTAINER_DEPLOYMENT.md` runbook (architecture, config table, host prep, security notes) + `docs/deploy/TENSORRT_INT8_RUNBOOK.md` tagged `BLOCKED: GPU host` with an explicit do-not-quote-int8-numbers honesty contract.

### Acceptance evidence
- Contract tests `tests/unit/test_deployment_assets.py` (28): compose describes exactly the two-service Next.js+FastAPI stack, API loopback-only, both healthchecks, API-key enforced in compose, parity between `requirements.txt` and `requirements-container.txt` minus documented exclusions, effective `USER` directive of both images is non-root, entrypoint staging behaviour exercised for real (stages readable weights, exits non-zero on unreadable weights, warns on empty mount, drops privileges when started as root), proxy route keeps the key server-side and refuses cross-origin requests.
- `docker compose config` valid; ONNX parity gate green on the real checkpoint: max |torch − onnxruntime| = **2.6e-06** (tolerance 1e-4). Note: the exporter detects the checkpoint as **resnet18** (`fc.weight` input dim 512) despite the `vision_resnet50.pth` filename; the metadata sidecar records the true architecture.
- Full suite: **197 passed / 17 skipped, exit 0** (was 186/17 at 4.1 close) — 0 regressions.
- Live stack verification (2026-10-25, rebuilt images on this session's Docker Desktop): `docker compose config` valid; `docker compose up -d` → both services `healthy` (api on `127.0.0.1:8000`, portal on `:3000`); API PID 1 (uvicorn) runs as **uid 10001** with no setpriv needed (image `USER aegismed`), entrypoint staged **8 model files**; direct API `/api/history` → **401** without key, `/health` public; proxy without Origin → **200** (server-side key attached), cross-site `Origin: http://evil.example` → **403**, same-origin Origin → **200**. A real diagnosis POST through the portal proxy returned **HTTP 200 in 102 s** (session `d0607fe5…`, ACS top differential at 0.85 confidence, severity moderate). In a real browser against the containerized stack: landing + Diagnosis pages render with no console errors; the live DEMAT flow ran 5/5 agents, entropy collapsed **3.22 → 2.03 bits** after two information-gain-ranked questions, and the refined result rendered (Cardiovascular Disease, HIGH severity, 85% confidence, red-flag panel, Download Report).
- Environment note: `docker compose build` hit Docker Desktop `DeadlineExceeded` on context transfer after a VM reset (file-sharing walk over large excluded trees stalls); documented the tar-piped build workaround in `docs/deploy/CONTAINER_DEPLOYMENT.md` §Troubleshooting.
