"""Regression tests for API authentication and client-controlled path handling.

These lock in the P0 truth-alignment and PHI-hygiene behaviour:
- the service API key is enforced unless the development bypass is on
- production refuses to start without a secret and without enforcement
- a client cannot hand the pipeline a filesystem path for an image
- `/health` reports what is actually usable instead of a fixed "all active"
"""

import pytest
from fastapi.testclient import TestClient

from config import settings


@pytest.fixture
def client():
    from src.api.main import app
    return TestClient(app)


@pytest.fixture
def enforced(monkeypatch):
    """Authentication enforced, with a known secret."""
    monkeypatch.setattr(settings, "enforce_api_key", True)
    monkeypatch.setattr(settings, "allow_insecure_dev", False)
    monkeypatch.setattr(settings, "app_env", "production")
    monkeypatch.setattr(settings, "secret_key", "test-secret-key")
    return settings


class TestApiKeyEnforcement:
    def test_missing_key_is_rejected(self, client, enforced):
        response = client.get("/api/chat/conversations")
        assert response.status_code == 401
        assert "X-API-Key" in response.json()["error"]

    def test_wrong_key_is_rejected(self, client, enforced):
        response = client.get("/api/chat/conversations", headers={"X-API-Key": "wrong"})
        assert response.status_code == 401

    def test_valid_key_is_accepted(self, client, enforced):
        response = client.get(
            "/api/chat/conversations", headers={"X-API-Key": "test-secret-key"}
        )
        assert response.status_code == 200

    def test_health_stays_public(self, client, enforced):
        response = client.get("/health")
        assert response.status_code == 200

    def test_development_bypass_skips_the_check(self, client, monkeypatch):
        monkeypatch.setattr(settings, "enforce_api_key", True)
        monkeypatch.setattr(settings, "allow_insecure_dev", True)
        monkeypatch.setattr(settings, "app_env", "development")
        response = client.get("/api/chat/conversations")
        assert response.status_code == 200

    def test_bypass_does_not_apply_in_production(self, client, monkeypatch):
        monkeypatch.setattr(settings, "enforce_api_key", True)
        monkeypatch.setattr(settings, "allow_insecure_dev", True)
        monkeypatch.setattr(settings, "app_env", "production")
        monkeypatch.setattr(settings, "secret_key", "test-secret-key")
        response = client.get("/api/chat/conversations")
        assert response.status_code == 401


class TestProductionStartupGuards:
    def test_production_requires_a_secret(self, monkeypatch):
        from src.api.main import startup_event

        monkeypatch.setattr(settings, "app_env", "production")
        monkeypatch.setattr(settings, "enforce_api_key", True)
        monkeypatch.setattr(settings, "secret_key", "")

        import asyncio

        with pytest.raises(RuntimeError, match="SECRET_KEY"):
            asyncio.run(startup_event())

    def test_production_requires_enforcement(self, monkeypatch):
        from src.api.main import startup_event

        monkeypatch.setattr(settings, "app_env", "production")
        monkeypatch.setattr(settings, "enforce_api_key", False)
        monkeypatch.setattr(settings, "secret_key", "test-secret-key")

        import asyncio

        with pytest.raises(RuntimeError, match="ENFORCE_API_KEY"):
            asyncio.run(startup_event())

    def test_production_disables_interactive_docs(self):
        """The docs surface is built from APP_ENV at import time.

        Run in a fresh interpreter because the app object is constructed
        when the module is first imported.
        """
        import os
        import subprocess
        import sys

        script = (
            "from src.api.main import app;"
            "print(app.docs_url, app.redoc_url, app.openapi_url)"
        )
        env = {**os.environ, "APP_ENV": "production"}
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == "None None None"

    def test_development_keeps_interactive_docs(self):
        import os
        import subprocess
        import sys

        script = (
            "from src.api.main import app;"
            "print(app.docs_url, app.redoc_url, app.openapi_url)"
        )
        env = {**os.environ, "APP_ENV": "development"}
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == "/docs /redoc /openapi.json"


class TestClientCannotSupplyAnImagePath:
    def test_request_model_has_no_image_path_field(self):
        from src.api.routes.diagnosis import DiagnosisRequest

        assert "image_path" not in DiagnosisRequest.model_fields

    def test_client_supplied_image_path_is_ignored(self, client, monkeypatch):
        """A path in the request body never reaches the orchestrator."""
        import src.api.routes.diagnosis as diag_module

        captured: dict = {}

        class _StubOrchestrator:
            async def run(self, input_data, progress_cb=None):
                captured.update(input_data)
                return {
                    "symptoms": [],
                    "synthesis_result": {
                        "diagnosis": [],
                        "explanation": "",
                        "patient_explanation": "",
                        "recommendations": [],
                        "severity": "unknown",
                        "doctor_alert": False,
                        "differential_diagnoses": [],
                        "red_flags": [],
                        "confidence": {},
                        "disclaimer": "",
                    },
                }

        monkeypatch.setattr(diag_module, "_orchestrator", _StubOrchestrator())

        response = client.post(
            "/api/diagnosis/analyze",
            json={"text": "I have a cough", "image_path": "/etc/passwd"},
        )

        assert response.status_code == 200
        assert captured.get("image_path") is None
        assert captured.get("text") == "I have a cough"


class TestHealthReportsRealState:
    def test_health_lists_every_agent(self, client):
        data = client.get("/health").json()
        expected = [
            "orchestrator", "vision", "nlp", "rag", "prediction", "voice", "synthesis",
        ]
        for agent in expected:
            assert agent in data["agents"], f"Missing agent: {agent}"

    def test_health_reports_authentication_mode(self, client, enforced):
        data = client.get("/health").json()
        assert data["authentication"] == "enforced"

    def test_health_does_not_claim_every_agent_is_active(self, client):
        """Agent status must describe the deployment, not a fixed claim."""
        data = client.get("/health").json()
        statuses = set(data["agents"].values())
        assert statuses != {"active"}
        assert all(isinstance(value, str) and value for value in data["agents"].values())
