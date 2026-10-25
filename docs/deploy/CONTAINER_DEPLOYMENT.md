# Containerised On-Prem Deployment (AegisMed)

Phase 4, Workstream 4.2 — containerised on-prem deployment for hospital
or lab networks, plus the CPU ONNX export path.

## What ships

| Artifact | Purpose |
|---|---|
| `Dockerfile` | Backend image — FastAPI multi-agent service, CPU-only PyTorch, non-root user |
| `frontend/Dockerfile` | Frontend image — Next.js 16 standalone output, non-root user |
| `docker-compose.yml` | Two-service stack: `api` (loopback-only) + `frontend` (LAN-facing) |
| `requirements-container.txt` | Runtime dependencies for the backend image |
| `scripts/deploy/export_onnx.py` | Exports the vision model to ONNX with a PyTorch parity check |
| `frontend/src/app/api/backend/[...path]/route.ts` | Same-origin proxy from the browser to the API |

## Architecture

```
   Hospital LAN
       │
       │  http://<host>:3000
       ▼
┌─────────────────────────┐        ┌────────────────────────────┐
│  aegismed-frontend      │        │  aegismed-api              │
│  Next.js 16 standalone  │───────▶│  FastAPI + multi-agent     │
│                         │  proxy │  pipeline                  │
│  /api/backend/* ────────┼────────┼──▶  http://api:8000/api/*   │
└─────────────────────────┘        └────────────────────────────┘
                                          │
                                    volumes: ./data ./models ./logs
```

The browser never talks to port 8000 directly. Requests go to the
frontend's `/api/backend/*` route, which forwards them server-side with
the `X-API-Key` header. Three consequences:

1. The API key stays on the server (a `NEXT_PUBLIC_*` variable would be
   readable by any browser).
2. No CORS configuration is needed for a LAN deployment.
3. The API port can be bound to `127.0.0.1` and stay unreachable from
   outside the host.

## Prerequisites

- Docker Engine 24+ with the Compose plugin (verified with Docker 29.6.1 / Compose 5.2.0)
- `.env` at the repository root with `SECRET_KEY` set to a random string
- Model weights in `models/` and the FAISS vector store in
  `data/vector_store/` on the host (mounted into the containers, never
  baked into the images)
- On a **Linux** host, the mounted directories must be usable by the
  container's unprivileged user (uid 10001) — bind mounts preserve host
  ownership exactly:

  ```bash
  sudo chown -R 10001:10001 models data logs
  ```

  Run the preflight before `docker compose up`; it materialises
  iCloud-evicted files, load-tests the checkpoints, and checks container
  access (blocking on Linux, advisory on macOS where Docker Desktop maps
  bind-mount permissions permissively):

  ```bash
  venv/bin/python scripts/deploy/prepare_models.py
  ```

## Build and run

```bash
# 1. Build both images
docker compose build

# 2. Start the stack
docker compose up -d

# 3. Confirm both services are healthy
docker compose ps

# 4. Tail the API logs
docker compose logs -f api
```

The portal is then at <http://localhost:3000>.

## Configuration

| Variable | Service | Meaning |
|---|---|---|
| `SECRET_KEY` | both | Shared API key; the frontend forwards it as `X-API-Key` |
| `APP_ENV` | api | `production` in compose, which makes the key mandatory |
| `ENFORCE_API_KEY` | api | `true` in compose; forces the key even in development |
| `CORS_ORIGINS` | api | Comma-separated browser origins allowed to call the API directly |
| `BACKEND_URL` | frontend | Internal backend address (`http://api:8000`) |
| `NEXT_PUBLIC_API_URL` | frontend | Build-time browser base URL (`/api/backend` for same-origin) |
| `OPENROUTER_API_KEY` | api | LLM synthesis key (rule-based fallback works without it) |
| `DATABASE_URL` | api | SQLite path; persisted through the `./data` volume |

## Health checks and readiness

Both images define a `HEALTHCHECK`. The frontend waits for the API to
report healthy before it starts, so `docker compose ps` showing both
services as `healthy` means the stack is ready.

```bash
curl -fsS http://localhost:8000/health   # API health (loopback only)
curl -fsS http://localhost:3000/         # Portal
```

Note that the vision model is loaded lazily on the first request, so a
healthy API does not imply the CNN is resident in memory — the first
vision request after a restart pays the model-load cost.

## Model export to ONNX (CPU inference)

The ONNX graph lets an inference runtime serve the same predictions
without the PyTorch dependency:

```bash
uv pip install --python venv/bin/python -r scripts/deploy/requirements-onnx.txt
venv/bin/python scripts/deploy/export_onnx.py \
    --checkpoint models/vision_resnet50.pth \
    --output models/vision_model.onnx
```

The script refuses to accept an artifact whose logits drift from
PyTorch by more than the tolerance (default `1e-4`), and writes a
`.metadata.json` sidecar recording the architecture, opset, input shape,
parity gap, and a SHA-256 checksum for audit.

## Security notes

- Both images run as an unprivileged user (uid 10001); the backend image's
  `USER` directive is `aegismed`, so `docker inspect` shows a non-root
  default and the API process never serves as root.
- The backend entrypoint refuses to start when a mounted weight file
  exists but cannot be read — a permissions misconfiguration on the host
  is surfaced at container start instead of silently degrading to
  rule-based scoring. An empty model directory is allowed (warning only)
  for deployments that intentionally run without weights.
- The API port is published on `127.0.0.1` only.
- The `/api/backend` proxy attaches the service API key, which makes it a
  privileged relay: it refuses cross-site browser requests (the request's
  `Origin` must match its `Host`, or be listed in `ALLOWED_ORIGINS` for
  reverse-proxy setups that rewrite `Host`). Requests without an
  `Origin` header (server-to-server clients) are accepted.
- `.env`, model weights, datasets, and logs are excluded from the build
  context via `.dockerignore` and supplied at runtime.
- The deployment has no TLS termination and no authentication on the
  portal itself. Put it behind the hospital's reverse proxy and access
  control before clinical use.

## Troubleshooting

**`failed to solve: DeadlineExceeded: context deadline exceeded` during
`docker compose build`** — Docker Desktop's file-sharing layer can stall
while walking large excluded trees (`node_modules/`, `.next/`, `venv/`),
timing the build context out. A daemon restart usually clears it; if it
persists, build from a pre-excluded tar so buildkit never walks the
heavy trees:

```bash
# backend (minimal context: only what the Dockerfile copies)
tar -cf /tmp/be.tar --exclude='__pycache__' --exclude='*.pyc' \
    Dockerfile config src docker requirements-container.txt
docker build -t aegismed-backend:latest - < /tmp/be.tar

# frontend
cd frontend
tar -cf /tmp/fe.tar --exclude=node_modules --exclude=.next \
    --exclude=.env --exclude='.env.*' .
docker build -t aegismed-frontend:latest - < /tmp/fe.tar
```

Images tagged exactly as compose expects (`aegismed-backend:latest`,
`aegismed-frontend:latest`) are picked up by `docker compose up -d`
without a rebuild.

## Known limitations

- **CPU only.** The images install CPU PyTorch wheels; GPU inference is
  out of scope until TensorRT INT8 is validated on an NVIDIA host (see
  `TENSORRT_INT8_RUNBOOK.md`).
- **Single API worker.** The vision model is cached per process, so
  extra workers would each load their own copy of the weights.
- **SQLite only.** The persistence layer is SQLite through the `./data`
  volume; multi-instance deployments need a database server.
- **Model weights are host-mounted.** The image ships the code, not the
  weights; each site must stage its own `models/` directory.
- **No clinical validation.** The images are a deployment mechanism, not
  evidence of clinical efficacy. See Phase 4.3 (IRB validation), which
  remains `BLOCKED: external`.
