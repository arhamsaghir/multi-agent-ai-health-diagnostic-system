"""Unit tests for the FHIR R4 interoperability mapping (Phase 4, Workstream 4.1)."""

import base64

import pytest

from src.core.fhir_mapping import (
    bundle_to_diagnosis_request,
    diagnosis_response_to_bundle,
    session_to_bundle,
)


def _sample_inbound_bundle() -> dict:
    return {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [
            {"resource": {"resourceType": "Patient", "id": "p1", "gender": "female", "birthDate": "1990-05-01"}},
            {"resource": {"resourceType": "Observation", "status": "final", "code": {"text": "Severe headache for 3 days"}}},
            {"resource": {"resourceType": "Observation", "status": "final", "code": {"text": "chief complaint"}, "valueString": "mild fever and nausea"}},
            {"resource": {"resourceType": "Condition", "subject": {"reference": "Patient/p1"}, "code": {"text": "possible migraine"}}},
        ],
    }


def _sample_response() -> dict:
    return {
        "session_id": "sess-1",
        "diagnosis": [
            {"name": "Migraine", "confidence": 0.82, "severity": "moderate"},
            {"name": "Tension headache", "confidence": 0.11, "severity": "low"},
        ],
        "explanation": "Clinical narrative explaining the differential.",
        "patient_explanation": "A simpler explanation for the patient.",
        "severity": "moderate",
        "doctor_alert": False,
        "differential_diagnoses": ["Migraine", "Tension headache"],
        "disclaimer": "This is not a substitute for professional care.",
        "triage": {"entropy_bits": 1.318},
    }


class TestInboundMapping:
    def test_extracts_text_and_demographics(self):
        req = bundle_to_diagnosis_request(_sample_inbound_bundle())
        text = req["text"].lower()
        assert "headache" in text
        assert "mild fever and nausea" in text  # valueString preferred over code.text
        assert "possible migraine" in text
        assert req["patient_history"]["gender"] == "female"
        assert req["patient_history"]["age"] >= 30

    def test_empty_symptoms_raises_value_error(self):
        bundle = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [{"resource": {"resourceType": "Patient", "id": "p1", "gender": "male"}}],
        }
        with pytest.raises(ValueError):
            bundle_to_diagnosis_request(bundle)

    def test_malformed_payload_raises(self):
        with pytest.raises(Exception):
            bundle_to_diagnosis_request({"resourceType": "Patient", "id": "nope"})


class TestOutboundMapping:
    def test_bundle_structure(self):
        bundle = diagnosis_response_to_bundle(
            _sample_response(), patient_history={"gender": "female", "age": 35}, session_id="sess-1"
        )
        assert bundle["resourceType"] == "Bundle"
        kinds = [e["resource"]["resourceType"] for e in bundle["entry"]]
        assert "Patient" in kinds
        assert kinds.count("Condition") == 2
        assert "RiskAssessment" in kinds
        assert "Observation" in kinds  # entropy
        assert "DocumentReference" in kinds

    def test_riskassessment_carries_probabilities(self):
        bundle = diagnosis_response_to_bundle(_sample_response(), session_id="sess-1")
        risk = next(e["resource"] for e in bundle["entry"] if e["resource"]["resourceType"] == "RiskAssessment")
        probs = [p.get("probabilityDecimal") for p in risk["prediction"]]
        assert pytest.approx(0.82, abs=1e-6) in probs

    def test_entropy_observation_value(self):
        bundle = diagnosis_response_to_bundle(_sample_response(), session_id="sess-1")
        obs = next(e["resource"] for e in bundle["entry"] if e["resource"]["resourceType"] == "Observation")
        assert obs["valueQuantity"]["value"] == pytest.approx(1.318, abs=1e-6)
        assert obs["valueQuantity"]["unit"] == "bit"

    def test_narrative_documentreference_roundtrips_text(self):
        bundle = diagnosis_response_to_bundle(_sample_response(), session_id="sess-1")
        doc = next(e["resource"] for e in bundle["entry"] if e["resource"]["resourceType"] == "DocumentReference")
        decoded = base64.b64decode(doc["content"][0]["attachment"]["data"]).decode("utf-8")
        assert "Clinical narrative" in decoded
        assert "not a substitute" in decoded.lower()

    def test_differential_fallback_when_no_diagnosis(self):
        resp = {"diagnosis": [], "differential_diagnoses": ["Flu", "Common cold"], "severity": "low"}
        bundle = diagnosis_response_to_bundle(resp, session_id="s2")
        names = [
            e["resource"]["code"]["text"]
            for e in bundle["entry"]
            if e["resource"]["resourceType"] == "Condition"
        ]
        assert names == ["Flu", "Common cold"]


class TestRoundTrip:
    def test_export_then_import_preserves_condition_names(self):
        exported = diagnosis_response_to_bundle(_sample_response(), session_id="sess-1")
        reimported = bundle_to_diagnosis_request(exported)
        assert "migraine" in reimported["text"].lower()
        assert "tension headache" in reimported["text"].lower()


class TestSessionMapping:
    def test_session_record_to_bundle(self):
        session = {
            "id": "sess-9",
            "user_input": "headache and fever",
            "patient_history": {"gender": "male", "age": 40},
            "diagnoses": [
                {"condition_name": "Migraine", "confidence": 0.7, "severity": "moderate"},
            ],
            "agent_outputs": {"synthesis": {"output": {"explanation": "Narrative.", "disclaimer": "Disc."}}},
        }
        bundle = session_to_bundle(session)
        assert bundle["resourceType"] == "Bundle"
        names = [
            e["resource"]["code"]["text"]
            for e in bundle["entry"]
            if e["resource"]["resourceType"] == "Condition"
        ]
        assert names == ["Migraine"]
