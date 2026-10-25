"""History API routes — diagnostic session history retrieval and management."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Any
from loguru import logger

from src.data.database.repository import DiagnosisRepository

router = APIRouter(prefix="/history", tags=["history"])


class DiagnosisItem(BaseModel):
    condition_name: str
    confidence: float
    severity: str


class SessionSummary(BaseModel):
    id: str
    created_at: str
    user_input: str
    symptoms: list[str] = Field(default_factory=list)
    image_path: Optional[str] = None
    status: str = "completed"
    primary_condition: str = "Undetermined"
    severity: str = "low"
    confidence: float = 0.0
    diagnoses: list[DiagnosisItem] = Field(default_factory=list)


class HistoryListResponse(BaseModel):
    sessions: list[SessionSummary]
    total: int


@router.get("", response_model=HistoryListResponse)
async def list_history(
    limit: int = Query(50, ge=1, le=100, description="Number of sessions to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
):
    """Retrieve list of past diagnostic sessions with summary diagnoses."""
    try:
        repo = DiagnosisRepository()
        total = repo.get_session_count()

        # If repo has list_sessions_with_diagnoses, use it; else fallback
        if hasattr(repo, "list_sessions_with_diagnoses"):
            sessions_data = repo.list_sessions_with_diagnoses(limit=limit, offset=offset)
        else:
            raw_sessions = repo.list_sessions(limit=limit, offset=offset)
            sessions_data = []
            for s in raw_sessions:
                detail = repo.get_session(s["id"]) or {}
                diagnoses = detail.get("diagnoses", [])
                top_diag = diagnoses[0] if diagnoses else {}
                s["diagnoses"] = [
                    {
                        "condition_name": d.get("condition_name", "Unknown"),
                        "confidence": float(d.get("confidence", 0.0)),
                        "severity": d.get("severity", "low"),
                    }
                    for d in diagnoses
                ]
                s["primary_condition"] = top_diag.get("condition_name", "Undetermined")
                s["severity"] = top_diag.get("severity", "low")
                s["confidence"] = float(top_diag.get("confidence", 0.0))
                sessions_data.append(s)

        return HistoryListResponse(
            sessions=[SessionSummary(**s) for s in sessions_data],
            total=total,
        )
    except Exception as e:
        logger.error(f"Failed to list diagnosis history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")


@router.get("/{session_id}")
async def get_session_detail(session_id: str):
    """Get full details of a specific diagnostic session."""
    try:
        repo = DiagnosisRepository()
        session = repo.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Diagnosis session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session: {str(e)}")
