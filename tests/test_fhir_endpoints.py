"""Endpoint tests for the FHIR R4 interoperability routes (Phase 4, Workstream 4.1).

The heavy orchestrator pipeline is stubbed so these exercise the FHIR edge
(Bundle in -> Bundle out, error handling, export) deterministically.
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.routes.diagnosis import DiagnosisResponse
from src.data.database.repository import DiagnosisRepository


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def stub_pipeline(monkeypatch):
    async def fake_run_analysis(request, progress_cb=None):
        return DiagnosisResponse(
            session_id="test-session-1",
            diagnosis=[{"name": "Migraine", "confidence": 0.82, "severity": "moderate"}],
            explanation="Clinical narrative.",
            patient_explanation="Simple explanation.",
            severity="moderate",
            differential_diagnoses=["Migraine", "Tension headache"],
            disclaimer="Not a substitute for professional care.",
            triage={"entropy_bits": 1.3},
        )

    monkeypatch.setattr("src.api.routes.fhir.run_analysis", fake_run_analysis)


def _inbound_bundle() -> dict:
    return {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [
            {"resource": {"resourceType": "Patient", "id": "p1", "gender": "female", "birthDate": "1988-01-01"}},
            {"resource": {"resourceType": "Observation", "status": "final", "code": {"text": "chief complaint"}, "valueString": "severe headache and fever"}},
        ],
    }


class TestFhirDiagnose:
    def test_returns_fhir_bundle(self, client, stub_pipeline):
        resp = client.post("/api/fhir/diagnose", json=_inbound_bundle())
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("application/fhir+json")
        body = resp.json()
        assert body["resourceType"] == "Bundle"
        names = [
            e["resource"]["code"]["text"]
            for e in body["entry"]
            if e["resource"]["resourceType"] == "Condition"
        ]
        assert "Migraine" in names

    def test_empty_symptoms_returns_400(self, client, stub_pipeline):
        empty = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [{"resource": {"resourceType": "Patient", "id": "p1"}}],
        }
        resp = client.post("/api/fhir/diagnose", json=empty)
        assert resp.status_code == 400

    def test_malformed_bundle_returns_400(self, client, stub_pipeline):
        resp = client.post("/api/fhir/diagnose", json={"resourceType": "Patient", "id": "x"})
        assert resp.status_code == 400


class TestFhirExport:
    def test_missing_session_returns_404(self, client, monkeypatch):
        monkeypatch.setattr(DiagnosisRepository, "get_session", lambda self, sid: None)
        resp = client.get("/api/fhir/diagnosis/does-not-exist")
        assert resp.status_code == 404

    def test_export_returns_bundle(self, client, monkeypatch):
        session = {
            "id": "sess-9",
            "user_input": "headache",
            "patient_history": {"gender": "male", "age": 40},
            "diagnoses": [{"condition_name": "Migraine", "confidence": 0.7, "severity": "moderate"}],
            "agent_outputs": {"synthesis": {"output": {"explanation": "N.", "disclaimer": "D."}}},
        }
        monkeypatch.setattr(DiagnosisRepository, "get_session", lambda self, sid: session)
        resp = client.get("/api/fhir/diagnosis/sess-9")
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("application/fhir+json")
        body = resp.json()
        assert body["resourceType"] == "Bundle"
        names = [
            e["resource"]["code"]["text"]
            for e in body["entry"]
            if e["resource"]["resourceType"] == "Condition"
        ]
        assert names == ["Migraine"]
