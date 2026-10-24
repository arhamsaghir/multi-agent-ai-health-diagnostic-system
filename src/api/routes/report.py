"""Clinical consultation report generation endpoint."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from src.utils.report_exporter import generate_pdf_report

router = APIRouter(prefix="/report", tags=["report"])


class ReportRequest(BaseModel):
    symptom_input: str = ""
    age: int | None = None
    gender: str = ""
    bmi: float | None = None
    diagnosis: list[dict] = Field(default_factory=list)
    explanation: str = ""
    patient_explanation: str = ""
    recommendations: list[str] = Field(default_factory=list)
    severity: str = "unknown"
    doctor_alert: bool = False
    differential_diagnoses: list[str] = Field(default_factory=list)
    red_flags: list[str] = Field(default_factory=list)
    confidence: dict = Field(default_factory=dict)
    disclaimer: str = ""
    triage: dict | None = None
    execution_trace: list[dict] = Field(default_factory=list)


@router.post("/generate")
async def generate_report(request: ReportRequest):
    """Render a deterministic PDF consultation report from diagnosis JSON."""
    try:
        payload = request.model_dump()
        payload["triage_entropy"] = (request.triage or {}).get("entropy_bits")
        payload["execution_trace"] = request.execution_trace
        pdf = generate_pdf_report(payload)
        if not pdf or not pdf.startswith(b"%PDF"):
            raise ValueError("Report renderer did not return a valid PDF")
        return Response(
            content=pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="aegismed-clinical-report.pdf"'},
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {exc}") from exc
