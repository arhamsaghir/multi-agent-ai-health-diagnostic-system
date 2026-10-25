"""Contract tests for the containerised on-prem deployment assets.

These guard the Phase 4.2 deliverables against silent drift: the compose
file must describe the Next.js + FastAPI stack (not the retired Streamlit
shell), the images must run as non-root with health checks, and the
container requirements must stay in sync with requirements.txt.
"""

from __future__ import annotations

import os
import re
import stat
import subprocess
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
COMPOSE_FILE = PROJECT_ROOT / "docker-compose.yml"
BACKEND_DOCKERFILE = PROJECT_ROOT / "Dockerfile"
ENTRYPOINT = PROJECT_ROOT / "docker" / "entrypoint.sh"
FRONTEND_DOCKERFILE = PROJECT_ROOT / "frontend" / "Dockerfile"
FRONTEND_DOCKERIGNORE = PROJECT_ROOT / "frontend" / ".dockerignore"
ROOT_DOCKERIGNORE = PROJECT_ROOT / ".dockerignore"
CONTAINER_REQUIREMENTS = PROJECT_ROOT / "requirements-container.txt"
REQUIREMENTS = PROJECT_ROOT / "requirements.txt"
NEXT_CONFIG = PROJECT_ROOT / "frontend" / "next.config.ts"
PROXY_ROUTE = PROJECT_ROOT / "frontend" / "src" / "app" / "api" / "backend" / "[...path]" / "route.ts"

CONTAINER_UID = 10001


def _parse_requirements(path: Path) -> dict[str, str]:
    """Map package name -> pinned specifier for a requirements file."""
    packages: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        name = re.split(r"[<>=!~\[; ]", line, maxsplit=1)[0].strip().lower()
        packages[name] = line
    return packages


def _container_exclusions() -> set[str]:
    """Read the documented exclusion list from requirements-container.txt."""
    for line in CONTAINER_REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        if line.startswith("# Excluded from requirements.txt:"):
            raw = line.split(":", 1)[1]
            return {pkg.strip().lower() for pkg in raw.split(",") if pkg.strip()}
    raise AssertionError("requirements-container.txt is missing its exclusion list header")


def _effective_user(dockerfile: str) -> str:
    """The user the image actually runs under — its last USER directive."""
    directives = [
        line.split(None, 1)[1].strip()
        for line in dockerfile.splitlines()
        if line.startswith("USER ")
    ]
    return directives[-1] if directives else "root"


def _run_entrypoint(monkeypatch_tmp: Path, mount_files: dict[str, int], command: str) -> subprocess.CompletedProcess[str]:
    """Run the entrypoint against a sandboxed model mount.

    ``mount_files`` maps file name -> permission bits to create inside the
    simulated ``/app/models`` bind mount.
    """
    mounted = monkeypatch_tmp / "mounted"
    staged = monkeypatch_tmp / "staged"
    mounted.mkdir()
    staged.mkdir()
    for name, mode in mount_files.items():
        path = mounted / name
        path.write_bytes(b"aegismed-weight")
        path.chmod(mode)

    env = {
        "AEGISMED_LOCAL_MODELS": str(staged),
        "AEGISMED_MOUNTED_MODELS": str(mounted),
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
    }
    return subprocess.run(
        ["sh", str(ENTRYPOINT), command],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


@pytest.fixture(scope="module")
def compose() -> dict:
    """Parsed compose file."""
    return yaml.safe_load(COMPOSE_FILE.read_text(encoding="utf-8"))


class TestComposeFile:
    """The compose file must describe the current two-service stack."""

    def test_declares_api_and_frontend_services(self, compose: dict) -> None:
        assert set(compose["services"]) == {"api", "frontend"}

    def test_frontend_serves_nextjs_not_streamlit(self, compose: dict) -> None:
        frontend = compose["services"]["frontend"]
        assert frontend["build"]["context"] == "./frontend"
        assert "streamlit" not in yaml.dump(compose).lower()

    def test_api_port_is_not_exposed_to_the_lan(self, compose: dict) -> None:
        """The browser reaches the API through the frontend proxy."""
        ports = compose["services"]["api"]["ports"]
        assert any(str(port).startswith("127.0.0.1:8000") for port in ports)

    def test_frontend_publishes_port_3000(self, compose: dict) -> None:
        assert "3000:3000" in compose["services"]["frontend"]["ports"]

    def test_both_services_define_healthchecks(self, compose: dict) -> None:
        for name, service in compose["services"].items():
            assert "healthcheck" in service, f"{name} has no healthcheck"
            assert service["healthcheck"].get("test")

    def test_api_enforces_the_api_key(self, compose: dict) -> None:
        environment = compose["services"]["api"]["environment"]
        assert environment["APP_ENV"] == "production"
        assert environment["ENFORCE_API_KEY"] == "true"

    def test_frontend_receives_backend_url_and_key(self, compose: dict) -> None:
        environment = compose["services"]["frontend"]["environment"]
        assert environment["BACKEND_URL"] == "http://api:8000"
        assert environment["API_KEY"] == "${SECRET_KEY}"

    def test_model_and_data_are_mounted_as_volumes(self, compose: dict) -> None:
        volumes = " ".join(compose["services"]["api"]["volumes"])
        assert "./models:/app/models" in volumes
        assert "./data:/app/data" in volumes


class TestBackendImage:
    """The backend image builds from the container requirements, not the full set."""

    def test_uses_container_requirements(self) -> None:
        dockerfile = BACKEND_DOCKERFILE.read_text(encoding="utf-8")
        assert "requirements-container.txt" in dockerfile
        assert "COPY . ." not in dockerfile

    def test_runs_as_non_root_with_healthcheck(self) -> None:
        dockerfile = BACKEND_DOCKERFILE.read_text(encoding="utf-8")
        assert _effective_user(dockerfile) == "aegismed"
        assert "HEALTHCHECK" in dockerfile
        assert "/health" in dockerfile

    def test_uses_cpu_only_pytorch(self) -> None:
        assert "--extra-index-url https://download.pytorch.org/whl/cpu" in CONTAINER_REQUIREMENTS.read_text(
            encoding="utf-8"
        )


class TestEntrypoint:
    """The entrypoint stages host weights and refuses to serve without them."""

    def test_stages_readable_weights_as_unprivileged_user(self, tmp_path: Path) -> None:
        if os.geteuid() == 0:
            pytest.skip("permission-based staging contract requires a non-root test runner")
        proc = _run_entrypoint(tmp_path, {"vision_resnet50.pth": 0o644}, "true")
        assert proc.returncode == 0, proc.stderr
        staged = tmp_path / "staged" / "vision_resnet50.pth"
        assert staged.exists()
        assert "Staged 1 model file(s)" in proc.stdout

    def test_refuses_to_start_when_weights_are_unreadable(self, tmp_path: Path) -> None:
        if os.geteuid() == 0:
            pytest.skip("root can read mode-000 files, so the refusal cannot be exercised")
        proc = _run_entrypoint(tmp_path, {"vision_resnet50.pth": 0o000}, "true")
        assert proc.returncode != 0
        assert "cannot read" in proc.stderr
        assert "10001" in proc.stderr

    def test_empty_mount_falls_back_with_a_warning(self, tmp_path: Path) -> None:
        proc = _run_entrypoint(tmp_path, {}, "true")
        assert proc.returncode == 0, proc.stderr
        assert "WARNING" in proc.stderr
        assert "rule-based" in proc.stderr

    def test_drops_privileges_when_started_as_root(self) -> None:
        script = ENTRYPOINT.read_text(encoding="utf-8")
        assert "setpriv" in script
        assert 'exec "$@"' in script


class TestFrontendImage:
    """The frontend image serves the Next.js standalone build."""

    def test_dockerfile_exists(self) -> None:
        assert FRONTEND_DOCKERFILE.exists()

    def test_copies_standalone_build(self) -> None:
        dockerfile = FRONTEND_DOCKERFILE.read_text(encoding="utf-8")
        assert "/app/.next/standalone" in dockerfile
        assert "/app/.next/static" in dockerfile
        assert "CMD [\"node\", \"server.js\"]" in dockerfile

    def test_binds_all_interfaces(self) -> None:
        dockerfile = FRONTEND_DOCKERFILE.read_text(encoding="utf-8")
        assert "HOSTNAME=0.0.0.0" in dockerfile

    def test_next_config_enables_standalone_output(self) -> None:
        assert 'output: "standalone"' in NEXT_CONFIG.read_text(encoding="utf-8")


class TestProxyRoute:
    """The same-origin proxy must exist and keep the API key server-side."""

    def test_route_handler_exists(self) -> None:
        source = PROXY_ROUTE.read_text(encoding="utf-8")
        assert "export const POST = proxy" in source
        assert "process.env.API_KEY" in source
        assert "process.env.BACKEND_URL" in source

    def test_route_is_not_statically_optimized(self) -> None:
        assert 'export const dynamic = "force-dynamic"' in PROXY_ROUTE.read_text(encoding="utf-8")

    def test_rejects_cross_site_browser_requests(self) -> None:
        """The proxy holds the service key, so foreign origins must not ride it."""
        source = PROXY_ROUTE.read_text(encoding="utf-8")
        assert "function originAllowed" in source
        assert "Cross-origin request refused" in source
        assert "ALLOWED_ORIGINS" in source
        # Same-origin acceptance: the request Origin must match the request Host.
        assert 'new URL(origin).host === host' in source


class TestIgnoreFiles:
    """Secrets, model weights and dependency trees must stay out of the images."""

    @pytest.mark.parametrize("ignore_file", [ROOT_DOCKERIGNORE, FRONTEND_DOCKERIGNORE])
    def test_ignores_secrets_and_dependencies(self, ignore_file: Path) -> None:
        contents = ignore_file.read_text(encoding="utf-8")
        assert ".env" in contents
        assert "node_modules" in contents

    def test_root_ignore_excludes_models_and_data(self) -> None:
        contents = ROOT_DOCKERIGNORE.read_text(encoding="utf-8")
        assert "models/" in contents
        assert "data/" in contents


class TestRequirementsParity:
    """The container requirements must mirror requirements.txt minus documented exclusions."""

    def test_every_requirement_is_present_or_documented_as_excluded(self) -> None:
        base = set(_parse_requirements(REQUIREMENTS))
        container = set(_parse_requirements(CONTAINER_REQUIREMENTS))
        excluded = _container_exclusions()

        missing = base - container - excluded
        assert not missing, f"packages missing from requirements-container.txt: {sorted(missing)}"

    def test_exclusion_list_has_no_stale_entries(self) -> None:
        base = set(_parse_requirements(REQUIREMENTS))
        excluded = _container_exclusions()
        stale = excluded - base
        assert not stale, f"excluded packages are not in requirements.txt: {sorted(stale)}"

    def test_vision_stack_is_never_excluded(self) -> None:
        excluded = _container_exclusions()
        assert "torch" not in excluded
        assert "torchvision" not in excluded
        assert "faiss-cpu" not in excluded
