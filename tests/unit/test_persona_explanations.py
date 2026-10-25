"""Workstream 2.2 — dual-mode explanation flavor guarantees.

Both explanation flavors (clinical ``explanation`` and plain-language
``patient_explanation``) must be present in every diagnosis payload so the
Patient/Clinician persona toggle always has content to render.
"""

import pytest
from fastapi.testclient import TestClient

from src.agents.rule_based_synthesis import RuleBasedSynthesizer


# ---------------------------------------------------------------------------
# RuleBasedSynthesizer.compose_explanations
# ---------------------------------------------------------------------------

class TestComposeExplanations:
    def test_fills_missing_patient_explanation(self):
        synth = {
            "diagnosis": [{"condition": "Pneumonia", "confidence": 0.72, "icd10_code": "J18.9"}],
            "explanation": "Clinical: consolidative process likely.",
        }
        result = RuleBasedSynthesizer().compose_explanations(synth)
        assert result["explanation"] == "Clinical: consolidative process likely."
        assert "Pneumonia" in result["patient_explanation"]
        assert len(result["patient_explanation"]) > 20

    def test_fills_missing_clinical_explanation(self):
        synth = {
            "diagnosis": [{"condition": "Pneumonia", "confidence": 0.72}],
            "patient_explanation": "Your symptoms may point to a chest infection.",
            "severity": "moderate",
            "red_flags": ["Difficulty breathing"],
        }
        result = RuleBasedSynthesizer().compose_explanations(synth)
        assert result["patient_explanation"] == "Your symptoms may point to a chest infection."
        assert "Primary differential: Pneumonia" in result["explanation"]
        assert "moderate" in result["explanation"]
        assert "Difficulty breathing" in result["explanation"]

    def test_preserves_both_when_present(self):
        synth = {
            "diagnosis": [{"condition": "Asthma", "confidence": 0.5}],
            "explanation": "clinical text",
            "patient_explanation": "plain text",
        }
        result = RuleBasedSynthesizer().compose_explanations(synth)
        assert result["explanation"] == "clinical text"
        assert result["patient_explanation"] == "plain text"

    def test_empty_diagnosis_still_composes_both(self):
        result = RuleBasedSynthesizer().compose_explanations({"diagnosis": []})
        assert result["patient_explanation"].strip()
        assert result["explanation"].strip()

    def test_normalizes_name_key_entries(self):
        """Diagnosis entries keyed by ``name`` (LLM schema) are also handled."""
        synth = {"diagnosis": [{"name": "Bronchitis", "confidence": 0.6}]}
        result = RuleBasedSynthesizer().compose_explanations(synth)
        assert "Bronchitis" in result["patient_explanation"]
        assert "Bronchitis" in result["explanation"]


# ---------------------------------------------------------------------------
# Endpoint payloads (both flavors present in /analyze and /refine)
# ---------------------------------------------------------------------------

class _StubOrchestrator:
    """Returns a synthesis payload with BOTH explanation flavors missing."""

    async def run(self, input_data, progress_cb=None):
        return {
            "symptoms": ["cough", "fever"],
            "synthesis_result": {
                "diagnosis": [
                    {
                        "condition": "Pneumonia",
                        "confidence": 0.72,
                        "icd10_code": "J18.9",
                        "rationale": "Fever with productive cough",
                    }
                ],
                "explanation": "",
                "patient_explanation": "",
                "recommendations": ["Chest X-ray"],
                "severity": "moderate",
                "doctor_alert": False,
                "differential_diagnoses": ["Bronchitis"],
                "red_flags": ["Difficulty breathing"],
                "confidence": {"overall_confidence": 0.7, "breakdown": {"nlp": 0.8}},
                "disclaimer": "stub disclaimer",
            },
        }


@pytest.fixture
def client(monkeypatch):
    from src.api.main import app
    import src.api.routes.diagnosis as diag_module

    monkeypatch.setattr(diag_module, "_orchestrator", _StubOrchestrator())
    return TestClient(app)


class TestEndpointPayloadFlavors:
    def test_analyze_returns_both_explanations(self, client):
        res = client.post(
            "/api/diagnosis/analyze",
            json={"text": "I have had a fever and cough for three days"},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["explanation"].strip()
        assert body["patient_explanation"].strip()
        assert body["diagnosis"][0]["icd10_code"] == "J18.9"

    def test_refine_returns_both_explanations(self, client):
        res = client.post(
            "/api/diagnosis/refine",
            json={"text": "I have had a fever and cough for three days", "follow_up_answers": []},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["explanation"].strip()
        assert body["patient_explanation"].strip()

    def test_llm_provided_flavors_pass_through_unchanged(self, client):
        class _FullOrchestrator(_StubOrchestrator):
            async def run(self, input_data, progress_cb=None):
                result = await super().run(input_data, progress_cb)
                result["synthesis_result"]["explanation"] = "LLM clinical text"
                result["synthesis_result"]["patient_explanation"] = "LLM plain text"
                return result

        import src.api.routes.diagnosis as diag_module
        diag_module._orchestrator = _FullOrchestrator()
        try:
            res = client.post(
                "/api/diagnosis/analyze",
                json={"text": "I have had a fever and cough for three days"},
            )
            assert res.status_code == 200
            body = res.json()
            assert body["explanation"] == "LLM clinical text"
            assert body["patient_explanation"] == "LLM plain text"
        finally:
            diag_module._orchestrator = None
