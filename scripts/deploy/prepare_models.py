"""Preflight check for the model weights used by the container deployment.

Run this before `docker compose up` on the host that serves the models:

    python scripts/deploy/prepare_models.py

Two things are checked:

1. **Readability.** macOS/iCloud can evict model files into "dataless"
   stubs. The host can still read them (iCloud re-downloads on demand),
   but Docker's file-sharing layer fails with
   "[Errno 35] Resource deadlock avoided", so the container silently
   falls back to rule-based scoring. This script materialises the files
   and verifies they can be read.
2. **Loadability.** The checkpoint and the joblib models are loaded once
   to prove the deployment environment matches the training environment
   (numpy/scikit-learn versions are picky about pickled estimators).
"""

from __future__ import annotations

import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# The container image runs the API as uid/gid 10001 (the "aegismed" user).
# On a Linux host bind mounts preserve host ownership exactly, so the
# mounted model weights must be readable by that uid and the mounted
# data/logs directories must be writable by it.
CONTAINER_UID = 10001
CONTAINER_GID = 10001

# On macOS, Docker Desktop maps bind-mount permissions permissively: a
# non-root container can read host files the mode bits would deny, so the
# uid checks below are advisory there and authoritative on Linux.
IS_LINUX = platform.system() == "Linux"


def _uid_access(path: Path, *, read: bool = False, write: bool = False) -> bool:
    """Whether a process running as CONTAINER_UID could read/write `path`.

    Directories additionally need the traverse (x) bit for either access.
    """
    wanted = (0o4 if read else 0o0) | (0o2 if write else 0o0)
    try:
        mode = path.stat().st_mode
        owner = path.stat().st_uid
        group = path.stat().st_gid
    except OSError:
        return False
    if IS_LINUX and path.is_dir():
        wanted |= 0o1
    if owner == CONTAINER_UID:
        flags = (mode >> 6) & 0o7
    elif group == CONTAINER_GID:
        flags = (mode >> 3) & 0o7
    else:
        flags = mode & 0o7
    return (flags & wanted) == wanted


def materialize(path: Path) -> bool:
    """Force the OS to pull a possibly-evicted file back onto local disk."""
    try:
        with path.open("rb") as handle:
            while handle.read(1024 * 1024):
                pass
        return True
    except OSError:
        pass

    if platform.system() == "Darwin":
        # Ask iCloud to download the file, then read it again.
        subprocess.run(["brctl", "download", str(path)], check=False)
        try:
            with path.open("rb") as handle:
                while handle.read(1024 * 1024):
                    pass
            return True
        except OSError:
            return False
    return False


def check_readable(paths: list[Path]) -> bool:
    """Verify every file can be read, materialising evicted ones."""
    ok = True
    for path in paths:
        if not path.exists():
            print(f"  MISSING  {path}")
            ok = False
            continue
        if materialize(path):
            print(f"  ok       {path.name} ({path.stat().st_size:,} bytes)")
        else:
            print(f"  UNREADABLE {path.name} — file is evicted or locked")
            print(
                "            Fix: `brctl download <path>` (iCloud) or copy the file\n"
                "            to local storage; Docker cannot read dataless stubs."
            )
            ok = False
    return ok


def check_loadable(models_dir: Path) -> bool:
    """Load the checkpoint and the joblib estimators once."""
    ok = True

    checkpoint = models_dir / "vision_resnet50.pth"
    if checkpoint.exists():
        try:
            import torch

            state_dict = torch.load(checkpoint, map_location="cpu", weights_only=True)
            print(f"  ok       {checkpoint.name} loads ({len(state_dict)} tensors)")
        except Exception as error:  # noqa: BLE001 - report any load failure verbatim
            print(f"  FAILED   {checkpoint.name}: {error}")
            ok = False

    joblibs = sorted(models_dir.glob("prediction_xgboost_*.joblib"))
    for path in joblibs:
        try:
            import joblib

            model = joblib.load(path)
            print(f"  ok       {path.name} loads ({type(model).__name__})")
        except Exception as error:  # noqa: BLE001
            print(f"  FAILED   {path.name}: {error}")
            print(
                "            The estimator was probably pickled with a different\n"
                "            numpy/scikit-learn version — check requirements.txt."
            )
            ok = False

    if not joblibs:
        print(f"  WARNING  no prediction_xgboost_*.joblib found in {models_dir}")

    return ok


def check_container_access(models_dir: Path) -> bool:
    """Verify the container's unprivileged user can use the mounted paths.

    Models must be readable by uid 10001; data/ and logs/ must be writable
    (SQLite history and application logs are written through the mounts).
    On macOS the checks are advisory — Docker Desktop relaxes bind-mount
    permissions — so a failure here prints the fix without failing the run.
    """
    project = models_dir.parent
    mounts: list[tuple[Path, bool, bool]] = [
        (models_dir, True, False),
        (project / "data", False, True),
        (project / "logs", False, True),
    ]

    ok = True
    blocking = IS_LINUX
    for path, needs_read, needs_write in mounts:
        if not path.exists():
            print(f"  MISSING  {path} (create it before docker compose up)")
            ok = False
            continue
        readable = _uid_access(path, read=True)
        writable = _uid_access(path, write=True)
        granted = (readable or not needs_read) and (writable or not needs_write)
        if granted:
            print(f"  ok       {path.name}/ accessible by uid {CONTAINER_UID}")
            continue

        verdict = "FAIL" if blocking else "note"
        hint = "" if blocking else " (advisory: Docker Desktop maps bind-mount permissions)"
        print(f"  {verdict:<8} {path.name}/ is not accessible by uid {CONTAINER_UID}{hint}")
        print(f"            Fix: sudo chown -R {CONTAINER_UID}:{CONTAINER_GID} {path}")
        ok = ok and not blocking
    return ok


def fix_permissions(models_dir: Path) -> int:
    """Make the mounted weights world-readable and try to chown data/logs.

    Model weights are not secret, so widening the read bits is safe and
    lets the unprivileged container stage them on any host. Writable
    directories need real ownership, which requires root, so a failure
    falls back to printing the sudo command.
    """
    changed = 0
    for path in sorted(models_dir.rglob("*")):
        mode = 0o755 if path.is_dir() else 0o644
        if path.stat().st_mode & 0o777 != mode:
            path.chmod(mode)
            changed += 1
    print(f"  chmod    {changed} path(s) under {models_dir} made readable")

    project = models_dir.parent
    for name in ("data", "logs"):
        target = project / name
        if not target.exists():
            continue
        try:
            os.chown(target, CONTAINER_UID, CONTAINER_GID)
            for child in target.rglob("*"):
                os.chown(child, CONTAINER_UID, CONTAINER_GID)
            print(f"  chown    {target} -> {CONTAINER_UID}:{CONTAINER_GID}")
        except PermissionError:
            print(
                f"  chown    {target} requires root — run:\n"
                f"            sudo chown -R {CONTAINER_UID}:{CONTAINER_GID} {target}"
            )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--models-dir",
        default=str(PROJECT_ROOT / "models"),
        help="Directory holding the model weights",
    )
    parser.add_argument(
        "--fix-permissions",
        action="store_true",
        help="chmod the weights readable and chown data/logs to the container user",
    )
    args = parser.parse_args()

    models_dir = Path(args.models_dir)
    if not models_dir.is_dir():
        print(f"Models directory not found: {models_dir}")
        return 1

    if args.fix_permissions:
        return fix_permissions(models_dir)

    print(f"Checking model weights in {models_dir}\n")
    print("Readability:")
    readable = check_readable(sorted(models_dir.iterdir()))

    print("\nLoadability:")
    loadable = check_loadable(models_dir)

    print("\nContainer access (uid 10001):")
    accessible = check_container_access(models_dir)

    if readable and loadable and accessible:
        print("\nAll model weights are ready for the container deployment.")
        return 0

    print("\nModel preparation FAILED — fix the items above before deploying.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
