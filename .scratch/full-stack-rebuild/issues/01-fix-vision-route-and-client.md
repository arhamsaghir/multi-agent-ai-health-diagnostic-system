# Ticket 1: Fix Vision API Route Prefix and Wire Image Upload

**Status:** `ready-for-agent`  
**Blocked by:** None  

## Context & Problem
In `src/api/routes/vision.py`, the router is defined with `prefix="/api/vision"`. When mounted in `src/api/main.py` with `prefix="/api"`, the endpoint resolves to `/api/api/vision/analyze`.
In `frontend/src/components/vision/VisionUploader.tsx`, image files selected by the user are never sent to the backend; instead, the component waits 2 seconds and displays hardcoded pneumonia demo data.

## Vertical Slice Work
1. **Backend:** Change `prefix="/api/vision"` to `prefix="/vision"` in `src/api/routes/vision.py` so the endpoint is consistently `/api/vision/analyze`.
2. **Frontend API Client:** Add `analyzeImage(file: File): Promise<VisionResult>` in `frontend/src/lib/api.ts` using `FormData`.
3. **Frontend Component:** Update `VisionUploader.tsx` `runAnalysis` to send the uploaded file to `analyzeImage()` and render the real model prediction and findings. Keep demo buttons as fallback.
4. **Backend Test:** Add `test_analyze_image_endpoint` to `tests/test_api_endpoints.py` verifying that sending an image file returns 200 with prediction classes.

## Acceptance Criteria
- `POST /api/vision/analyze` responds at `/api/vision/analyze` with 200 for valid image uploads.
- Uploading an image in the Next.js UI sends an HTTP POST request to the backend and renders the model predictions.
- Existing tests in `tests/test_api_endpoints.py` pass.
