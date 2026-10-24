"""Server-Sent Events routes for live multi-agent execution progress.

POST /diagnosis/analyze-stream  — same body as /diagnosis/analyze, streams
    agent lifecycle events followed by a terminal `result` frame carrying the
    DiagnosisResponse payload.
POST /diagnosis/refine-stream   — same body as /diagnosis/refine; additionally
    emits a DEMAT triage arbitration event before the agent pipeline runs.
"""

import asyncio
import uuid

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from loguru import logger

from src.api.progress import event_bus, make_progress_cb, stream_run_events, format_sse
from src.api.routes.diagnosis import (
    DiagnosisRequest,
    RefineDiagnosisRequest,
    run_analysis,
    run_refinement,
)

router = APIRouter(prefix="/diagnosis", tags=["diagnosis-stream"])

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
    "Connection": "keep-alive",
}


@router.post("/analyze-stream")
async def analyze_stream(request: DiagnosisRequest):
    """Stream live agent progress for a diagnostic run via SSE."""
    run_id = str(uuid.uuid4())
    event_bus.create(run_id)
    event_bus.publish(run_id, {"type": "run_started", "run_id": run_id})

    progress_cb = make_progress_cb(run_id)
    task = asyncio.create_task(run_analysis(request, progress_cb=progress_cb))
    logger.info(f"Started streamed analysis run {run_id}")

    return StreamingResponse(
        stream_run_events(run_id, task),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )


@router.post("/refine-stream")
async def refine_stream(request: RefineDiagnosisRequest):
    """Stream DEMAT arbitration + agent progress for a refinement run via SSE."""
    run_id = str(uuid.uuid4())
    event_bus.create(run_id)
    event_bus.publish(run_id, {"type": "run_started", "run_id": run_id})

    progress_cb = make_progress_cb(run_id)
    task = asyncio.create_task(run_refinement(request, progress_cb=progress_cb))
    logger.info(f"Started streamed refinement run {run_id}")

    return StreamingResponse(
        stream_run_events(run_id, task),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )
