"""Vision API routes — medical image analysis endpoint."""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/vision", tags=["vision"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".tif"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


class VisionResponse(BaseModel):
    """Response model for vision analysis endpoint.

    Attributes:
        findings: List of detected conditions with confidence scores.
        total_detected: Number of conditions found in the image.
        highest_confidence: Highest confidence score among all findings.
        anomalies: List of detected condition names.
    """
    findings: list[dict]
    total_detected: int
    highest_confidence: float
    anomalies: list[str]


def validate_image_file(file: UploadFile) -> None:
    """Validate uploaded image file type and size."""
    # Check file extension
    ext = None
    if file.filename:
        ext = "." + file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )


@router.post("/analyze", response_model=VisionResponse)
async def analyze_image(image: UploadFile = File(...)):
    """Analyze a medical image using the Vision Agent (ResNet-50)."""
    from src.agents.vision.agent import VisionAgent
    import tempfile

    # Validate file
    validate_image_file(image)

    # Read and check file size
    content = await image.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )

    # Save uploaded image temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        agent = VisionAgent()
        result = await agent.run({"image_path": tmp_path})
        return VisionResponse(**result)
    finally:
        import os
        os.unlink(tmp_path)
