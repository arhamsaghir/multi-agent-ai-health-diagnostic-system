#!/bin/sh
# AegisMed backend container entrypoint.
#
# Model weights are mounted from the host (they must not be baked into the
# image). Reading them straight off a bind mount can fail with
# "[Errno 35] Resource deadlock avoided" — joblib and torch take file
# locks that some bind-mount filesystems (notably Docker Desktop's macOS
# mounts) do not support. The weights are therefore staged onto the
# container's own filesystem before the API starts.
#
# The container runs as the unprivileged "aegismed" user (uid 10001).
# Staging is a plain copy into a directory that user owns, so it needs no
# privileges. If a host-mounted weight cannot be read the container refuses
# to start rather than silently serving rule-based fallback results.
#
# Paths are overridable through the environment so the staging behaviour
# can be exercised by the deployment contract tests.
set -e

LOCAL_MODELS="${AEGISMED_LOCAL_MODELS:-/var/lib/aegismed/models}"
MOUNTED_MODELS="${AEGISMED_MOUNTED_MODELS:-/app/models}"
RUN_AS_USER="aegismed"

mkdir -p "$LOCAL_MODELS"

staged=0
failed=0

if [ -d "$MOUNTED_MODELS" ]; then
    for file in "$MOUNTED_MODELS"/*; do
        [ -f "$file" ] || continue
        if cp -f "$file" "$LOCAL_MODELS/" 2>/dev/null; then
            staged=$((staged + 1))
        else
            echo "[entrypoint] ERROR: cannot read $file" >&2
            failed=$((failed + 1))
        fi
    done
fi

if [ "$failed" -gt 0 ]; then
    echo "[entrypoint] ERROR: $failed model file(s) could not be staged." >&2
    echo "[entrypoint] The API process runs as uid 10001 and needs read access" >&2
    echo "[entrypoint] to the mounted weights. On a Linux host, prepare them:" >&2
    echo "[entrypoint]   sudo chown -R 10001:10001 models data logs" >&2
    echo "[entrypoint] See docs/deploy/CONTAINER_DEPLOYMENT.md for the full check." >&2
    exit 1
fi

if [ "$staged" -eq 0 ]; then
    echo "[entrypoint] WARNING: no model weights found in $MOUNTED_MODELS." >&2
    echo "[entrypoint] The pipeline will fall back to rule-based scoring." >&2
else
    echo "[entrypoint] Staged $staged model file(s) at $LOCAL_MODELS"
fi

if [ -f "$LOCAL_MODELS/$(basename "${VISION_MODEL_PATH:-vision_resnet50.pth}")" ]; then
    VISION_MODEL_PATH="$LOCAL_MODELS/$(basename "${VISION_MODEL_PATH:-vision_resnet50.pth}")"
    export VISION_MODEL_PATH
fi

if [ -f "$LOCAL_MODELS/$(basename "${PREDICTION_MODEL_PATH:-prediction_xgboost.pkl}")" ]; then
    PREDICTION_MODEL_PATH="$LOCAL_MODELS/$(basename "${PREDICTION_MODEL_PATH:-prediction_xgboost.pkl}")"
    export PREDICTION_MODEL_PATH
fi

# Drop privileges before starting the service. The container image already
# runs unprivileged, but an operator may start it as root (for example to
# read host-owned weights); the API must never serve requests as root.
if [ "$(id -u)" = "0" ]; then
    exec setpriv --reuid="$RUN_AS_USER" --regid="$RUN_AS_USER" --init-groups "$@"
fi

exec "$@"
