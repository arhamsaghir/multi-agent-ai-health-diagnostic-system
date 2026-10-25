# AegisMed backend image — FastAPI multi-agent diagnostic service
#
# Build:  docker build -t aegismed-backend .
# Run:    docker run --rm -p 8000:8000 --env-file .env aegismed-backend
#
# CPU-only PyTorch keeps the image small enough for hospital on-prem
# networks. Model weights and the vector store are mounted at runtime,
# they are not baked into the image.

# Python 3.12 matches the development environment and the version the
# prediction models were trained under (langchain only caps numpy at <2
# for Python < 3.12, and the models need numpy 2.x).
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# build-essential is needed for wheels without prebuilt manylinux binaries
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Dependencies first so application edits don't invalidate the pip layer
COPY requirements-container.txt ./
RUN pip install --no-cache-dir -r requirements-container.txt

# Application code
COPY config/ ./config/
COPY src/ ./src/
COPY docker/entrypoint.sh /usr/local/bin/aegismed-entrypoint.sh
RUN chmod +x /usr/local/bin/aegismed-entrypoint.sh

# Runtime directories (overridden by volumes in docker-compose)
# /var/lib/aegismed holds the staged model weights — see docker/entrypoint.sh
RUN mkdir -p /app/data/vector_store /app/data/processed /app/models /app/logs \
        /var/lib/aegismed/models \
    && useradd --create-home --uid 10001 aegismed \
    && chown -R aegismed:aegismed /app /var/lib/aegismed

# The service runs unprivileged. The entrypoint stages the host-mounted
# weights into a directory this user owns, so no privileges are needed to
# start the container.
USER aegismed

EXPOSE 8000

# Models load lazily on first request, so /health is the readiness signal.
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

# Single worker: the vision model is cached per process, so extra workers
# would each load their own copy of the weights into memory.
ENTRYPOINT ["aegismed-entrypoint.sh"]
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
