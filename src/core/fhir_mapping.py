"""HL7 FHIR R4 interoperability mapping for AegisMed (Phase 4, Workstream 4.1).

Edge facade only: translates inbound FHIR R4 Bundles into the orchestrator's
``DiagnosisRequest`` shape, and serialises a ``DiagnosisResponse`` (or a
persisted session record) back into a FHIR R4 Bundle. The patented
DEMAT / EN-SCAF engines are untouched — this module performs no diagnosis, it
only maps at the API boundary so AegisMed can exchange data with EHR/EMR
systems that speak FHIR R4.
"""
from __future__ import annotations

import base64
from datetime import date, datetime, timezone
from typing import Any, Optional

from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.condition import Condition
from fhir.resources.R4B.observation import Observation
from fhir.resources.R4B.riskassessment import RiskAssessment
from fhir.resources.R4B.documentreference import DocumentReference


def _resource_name(resource: Any) -> str:
    """Concrete FHIR resource type name regardless of fhir.resources version."""
    return getattr(resource, "resource_type", None) or type(resource).__name__


def _age_from_birthdate(birth: Any) -> Optional[int]:
    """Whole-year age from a FHIR date, tolerant of date objects or ISO strings."""
    if birth is None:
        return None
    if not isinstance(birth, date):
        try:
            birth = date.fromisoformat(str(birth)[:10])
        except ValueError:
            return None
    today = datetime.now(timezone.utc).date()
    return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))


def _patient_to_history(patient: Patient) -> dict:
    history: dict[str, Any] = {}
    if patient.gender:
        history["gender"] = patient.gender
    age = _age_from_birthdate(patient.birthDate)
    if age is not None:
        history["age"] = age
    return history


def _observation_phrase(obs: Observation) -> Optional[str]:
    if getattr(obs, "valueString", None):
        return obs.valueString
    code = getattr(obs, "code", None)
    if code is not None:
        if getattr(code, "text", None):
            return code.text
        coding = getattr(code, "coding", None)
        if coding and getattr(coding[0], "display", None):
            return coding[0].display
    return None


def bundle_to_diagnosis_request(payload: dict) -> dict:
    """Map an inbound FHIR R4 Bundle into the orchestrator ``DiagnosisRequest`` dict.

    Chief complaint / symptom text is gathered from ``Observation`` resources
    (``valueString`` or coded ``display``/``text``) and ``Condition`` codes;
    demographics come from the ``Patient`` resource. Raises ``ValueError`` when
    no symptom text can be extracted so the route can answer HTTP 400.
    """
    bundle = Bundle.model_validate(payload)
    phrases: list[str] = []
    patient_history: dict[str, Any] = {}

    for entry in (bundle.entry or []):
        resource = getattr(entry, "resource", None)
        if resource is None:
            continue
        name = _resource_name(resource)
        if name == "Patient":
            patient_history.update(_patient_to_history(resource))
        elif name == "Observation":
            phrase = _observation_phrase(resource)
            if phrase:
                phrases.append(phrase)
        elif name == "Condition":
            code = getattr(resource, "code", None)
            if code is not None and getattr(code, "text", None):
                phrases.append(code.text)

    text = ". ".join(p.strip() for p in phrases if p and p.strip())
    if not text:
        raise ValueError(
            "FHIR Bundle contained no symptom Observation/Condition text to analyse."
        )
    return {
        "text": text,
        "patient_history": patient_history or None,
        "image_path": None,
        "language": None,
    }


def _normalise_diagnoses(response: dict) -> list[dict]:
    """Return a ranked list of {name, confidence, severity} from a response dict."""
    diags = response.get("diagnosis") or []
    out: list[dict] = []
    for d in diags:
        out.append(
            {
                "name": d.get("name") or d.get("condition") or "Undetermined",
                "confidence": d.get("confidence"),
                "severity": d.get("severity"),
            }
        )
    if not out:
        for differential in response.get("differential_diagnoses") or []:
            out.append({"name": differential, "confidence": None, "severity": None})
    return out


def diagnosis_response_to_bundle(
    response: dict,
    *,
    patient_history: Optional[dict] = None,
    session_id: Optional[str] = None,
) -> dict:
    """Serialise a ``DiagnosisResponse`` dict into a FHIR R4 ``Bundle`` (JSON-ready dict).

    Emits: Patient, one ranked ``Condition`` per differential (confidence noted),
    a ``RiskAssessment`` with per-outcome probabilities and triage severity, an
    ``Observation`` carrying DEMAT diagnostic entropy (bits) when present, and a
    ``DocumentReference`` holding the clinician narrative plus disclaimer.
    """
    pid = f"aegismed-{session_id}" if session_id else "aegismed-patient"
    subject_ref = {"reference": f"Patient/{pid}"}

    patient_fields: dict[str, Any] = {"id": pid}
    hist = patient_history or {}
    if hist.get("gender") in {"male", "female", "other", "unknown"}:
        patient_fields["gender"] = hist["gender"]
    patient = Patient(**patient_fields)
    entries: list[dict] = [{"resource": patient}]

    diagnoses = _normalise_diagnoses(response)
    predictions: list[dict] = []
    for idx, diag in enumerate(diagnoses, start=1):
        condition = Condition(
            id=f"condition-{idx}",
            subject=subject_ref,
            code={"text": diag["name"]},
        )
        if diag["confidence"] is not None:
            condition.note = [{"text": f"Model confidence: {float(diag['confidence']):.3f}"}]
        entries.append({"resource": condition})
        prediction: dict[str, Any] = {"outcome": {"text": diag["name"]}}
        if diag["confidence"] is not None:
            prediction["probabilityDecimal"] = float(diag["confidence"])
        predictions.append(prediction)

    risk_fields: dict[str, Any] = {
        "id": "risk-1",
        "status": "final",
        "subject": subject_ref,
        "prediction": predictions or None,
    }
    severity = response.get("severity")
    if severity:
        risk_fields["note"] = [
            {
                "text": (
                    f"Triage severity: {severity}; "
                    f"doctor_alert={bool(response.get('doctor_alert', False))}"
                )
            }
        ]
    entries.append({"resource": RiskAssessment(**risk_fields)})

    triage = response.get("triage")
    entropy = triage.get("entropy_bits") if isinstance(triage, dict) else None
    if entropy is not None:
        entries.append(
            {
                "resource": Observation(
                    id="obs-entropy",
                    status="final",
                    subject=subject_ref,
                    code={"text": "DEMAT diagnostic entropy"},
                    valueQuantity={
                        "value": float(entropy),
                        "unit": "bit",
                        "system": "http://unitsofmeasure.org",
                        "code": "bit",
                    },
                )
            }
        )

    narrative = response.get("explanation") or response.get("patient_explanation") or ""
    disclaimer = response.get("disclaimer") or ""
    blob = (narrative + ("\n\n" + disclaimer if disclaimer else "")).strip() or "No narrative available."
    entries.append(
        {
            "resource": DocumentReference(
                id="doc-1",
                status="current",
                subject=subject_ref,
                content=[
                    {
                        "attachment": {
                            "contentType": "text/plain",
                            "data": base64.b64encode(blob.encode("utf-8")).decode("ascii"),
                        }
                    }
                ],
            )
        }
    )

    bundle = Bundle(type="collection", timestamp=datetime.now(timezone.utc), entry=entries)
    return bundle.model_dump(mode="json", exclude_none=True)


def session_to_bundle(session: dict) -> dict:
    """Serialise a persisted history session record into a FHIR R4 Bundle."""
    diagnoses = [
        {
            "name": d.get("condition_name"),
            "confidence": d.get("confidence"),
            "severity": d.get("severity"),
        }
        for d in session.get("diagnoses", [])
    ]
    synthesis = (session.get("agent_outputs", {}).get("synthesis", {}) or {}).get("output", {})
    if not isinstance(synthesis, dict):
        synthesis = {}
    response = {
        "diagnosis": diagnoses,
        "explanation": synthesis.get("explanation", ""),
        "patient_explanation": synthesis.get("patient_explanation", ""),
        "severity": (diagnoses[0]["severity"] if diagnoses else "unknown"),
        "disclaimer": synthesis.get("disclaimer", ""),
        "triage": None,
    }
    return diagnosis_response_to_bundle(
        response,
        patient_history=session.get("patient_history"),
        session_id=session.get("id"),
    )
