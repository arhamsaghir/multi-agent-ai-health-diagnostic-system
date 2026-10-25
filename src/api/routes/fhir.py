"""HL7 FHIR R4 interoperability API routes (Phase 4, Workstream 4.1).

Exposes a FHIR-native edge so EHR/EMR systems can drive AegisMed:
``POST /api/fhir/diagnose`` consumes a FHIR R4 Bundle and returns a Bundle;
``GET /api/fhir/diagnosis/{session_id}`` exports a persisted diagnosis as a
Bundle. These wrap the existing orchestrator pipeline without altering it.
"""

from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger

from src.api.routes.diagnosis import DiagnosisRequest, run_analysis
from src.core.fhir_mapping import (
    bundle_to_diagnosis_request,
    diagnosis_response_to_bundle,
    session_to_bundle,
)
from src.data.database.repository import DiagnosisRepository

router = APIRouter(prefix="/fhir", tags=["fhir"])

_FHIR_MEDIA_TYPE = "application/fhir+json"


@router.post("/diagnose")
async def fhir_diagnose(payload: dict = Body(..., description="A FHIR R4 Bundle")):
    """Run the AegisMed pipeline from a FHIR R4 Bundle and return a FHIR R4 Bundle."""
    try:
        request_fields = bundle_to_diagnosis_request(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # malformed/invalid FHIR
        raise HTTPException(status_code=400, detail=f"Invalid FHIR Bundle: {exc}")

    try:
        response = await run_analysis(DiagnosisRequest(**request_fields))
        bundle = diagnosis_response_to_bundle(
            response.model_dump(),
            patient_history=request_fields.get("patient_history"),
            session_id=response.session_id,
        )
        return JSONResponse(content=bundle, media_type=_FHIR_MEDIA_TYPE)
    except Exception as exc:
        logger.error(f"FHIR diagnose pipeline failed: {exc}")
        raise HTTPException(status_code=500, detail=f"FHIR analysis failed: {exc}")


@router.get("/diagnosis/{session_id}")
async def fhir_export_diagnosis(session_id: str):
    """Export a persisted diagnostic session as a FHIR R4 Bundle."""
    try:
        session = DiagnosisRepository().get_session(session_id)
    except Exception as exc:
        logger.error(f"FHIR export lookup failed for {session_id}: {exc}")
        raise HTTPException(status_code=500, detail=f"Lookup failed: {exc}")
    if not session:
        raise HTTPException(status_code=404, detail="Diagnosis session not found")
    return JSONResponse(content=session_to_bundle(session), media_type=_FHIR_MEDIA_TYPE)
