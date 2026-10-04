# Specification: Full-Stack Integration, Session Persistence & Developer Automations

**Status:** `ready-for-agent`  
**Authors:** ZCode Agent & User  
**Target Feature:** End-to-End System Connectivity, SQLite Persistence, Landing Portal & Dev Automations  

---

## Problem Statement

The Multi-Agent AI Health Diagnostic System possesses a comprehensive Python backend (FastAPI, LangGraph orchestrator, ResNet-50 CNN, FAISS vector search, and a tested SQLite repository), but is hobbled by critical disconnects:
1. **Frontend Mock Lock-in:** The Next.js frontend is almost entirely isolated from the backend. The Diagnosis page defaults to `demoMode: true` with artificial `setTimeout` delays; the Vision Uploader ignores user files and returns hardcoded pneumonia stats; Medical Chat uses an in-memory 5-string dictionary; and Diagnosis History displays static mock records.
2. **FastAPI Route Prefix Collision:** In `src/api/routes/vision.py`, `prefix="/api/vision"` combined with `app.include_router(prefix="/api")` creates a broken `/api/api/vision/analyze` route.
3. **Missing Session Persistence:** `DiagnosisRepository` in `src/data/database/repository.py` passes all 9 unit tests, but is never invoked by `src/api/routes/diagnosis.py`. Completed diagnoses vanish on response, and there is no `/api/history` REST endpoint.
4. **Unfinished Root Landing Page:** `frontend/src/app/page.tsx` is still the stock create-next-app boilerplate ("To get started, edit the page.tsx file").
5. **Lack of Developer Automations:** As highlighted by `claude-automation-recommender`, there are no automated hooks to catch cross-language schema mismatches or lint regressions between Pydantic and TypeScript.

---

## Solution

Deliver a unified, fully working medical diagnostic application where the Next.js frontend communicates seamlessly with the FastAPI backend and SQLite database, supported by persistent developer automations:
1. **Fix Route Mounting:** Standardize all backend routes under `/api/` (specifically fixing `/api/vision/analyze`).
2. **Wire Real APIs in Next.js:** Replace all mock handlers in `frontend/src/lib/api.ts`, `VisionUploader.tsx`, `MedicalChat.tsx`, and `DiagnosisHistory.tsx` with live HTTP calls, including error boundaries and offline fallbacks.
3. **Persist Diagnostic History:** Wire `DiagnosisRepository` into `/api/diagnosis/analyze` to save completed sessions and diagnoses, and expose `GET /api/history` for client consumption.
4. **Build Clinical Landing Dashboard:** Design a sleek healthcare portal at `frontend/src/app/page.tsx` featuring system status (active agents), quick-action entry points (Symptom Checker, Scan Analysis, Medical Chat), and statistics.
5. **Install Developer Automations:** Deploy a post-edit linter hook and an API contract sync workflow to keep frontend and backend schemas aligned.

---

## User Stories

1. As a patient, I want to type my symptoms on `/diagnosis` and receive real multi-agent analysis (NLP, RAG, risk scoring) from the FastAPI backend rather than simulated demo data.
2. As a patient, I want to input my age, gender, BMI, and family history so that the backend prediction agent factors my personal risk factors into the differential diagnosis.
3. As a clinician or patient, I want to upload a real chest X-ray image (`.png` / `.jpg`) on `/vision` and have it processed by the backend ResNet-50 model.
4. As a clinician, I want to see the top multi-class disease findings with confidence bars and medical urgency levels derived from model inference.
5. As a user, I want to chat with the Medical AI on `/chat` and receive evidence-based responses from the backend RAG/LLM engine rather than static pre-written strings.
6. As a user, I want my chat conversation context to be remembered across turns within my session.
7. As a patient, I want my completed symptom and vision diagnoses to be saved automatically so that I can review them later.
8. As a user, I want to navigate to `/history` and view my actual chronological diagnostic records fetched from the SQLite database.
9. As a user, I want to filter my history by condition severity (Critical, High, Moderate, Low).
10. As a visitor opening `http://localhost:3000`, I want to see a healthcare diagnostic dashboard introducing the multi-agent system rather than a generic Next.js template.
11. As a developer, I want all API routes to follow consistent prefixing (`/api/diagnosis`, `/api/vision`, `/api/chat`, `/api/history`) so that routing is predictable.
12. As a developer, I want code changes in Python or TypeScript to trigger automatic syntax and lint verification so that regressions are caught immediately.
13. As a developer, I want an automated skill to verify that Pydantic response models and Next.js TypeScript interfaces remain in sync.

---

## Implementation Decisions

### 1. Backend Route & Persistence Architecture
- **Fix Vision Prefix:** In `src/api/routes/vision.py`, change `prefix="/api/vision"` to `prefix="/vision"`.
- **Add History Router (`src/api/routes/history.py`):**
  - `GET /api/history`: Returns list of past sessions ordered by `created_at DESC` using `DiagnosisRepository.list_sessions(limit=50)`.
  - `GET /api/history/{session_id}`: Returns session detail with associated diagnoses.
- **Wire Diagnosis Persistence:**
  - In `src/api/routes/diagnosis.py:analyze_symptoms`, instantiate `DiagnosisRepository()` and save the session and resulting differential diagnoses to SQLite before returning.
- **Mount New Routes:** In `src/api/main.py`, mount `history.router` under `/api`.

### 2. Frontend Client Integration
- **`frontend/src/lib/api.ts`:**
  - Update `diagnose()` default to `demoMode = false`.
  - Add `fetchHistory(): Promise<DiagnosisRecord[]>`.
  - Add `analyzeImage(file: File): Promise<VisionResult>`.
  - Add `sendChatMessage(message: string, conversationId?: string): Promise<ChatMessageResponse>`.
  - Graceful fallback: If the backend is unreachable (e.g. `fetch` fails), return an informative error state with option to view demo mode.
- **`VisionUploader.tsx`:**
  - In `runAnalysis()`, create a `FormData` payload containing the selected `File` and send it to `/api/vision/analyze`.
  - Parse real predictions, primary findings, and severity from the backend response.
- **`MedicalChat.tsx`:**
  - Send user messages to `/api/chat/message`.
  - Support multi-turn conversation memory with a client-managed `conversationId` (`uuidv4`).
- **`DiagnosisHistory.tsx`:**
  - Fetch records on mount via `fetchHistory()`.
  - Support live status badges and severity filtering.
- **`frontend/src/app/page.tsx`:**
  - Replace create-next-app template with a dashboard:
    - Welcome hero with system overview and system health indicators.
    - 3 primary action cards: "Symptom Diagnosis", "Chest X-Ray Analysis", "Clinical Chatbot".
    - Overview of the 5 agents: NLP (BioBERT), Vision (ResNet-50), RAG (FAISS), Prediction (XGBoost), Synthesis (Gemini/Nemotron).

### 3. Developer Automations
- **Hook (`.zcode/hooks/post-edit.sh`):**
  - Executes `ruff check --fix` on modified Python files.
  - Executes `npx prettier --write` or fast lint on frontend files.
- **Skill (`.zcode/skills/sync-api-contracts/SKILL.md`):**
  - Inspects `DiagnosisResponse`, `VisionResponse`, `ChatMessageResponse` and aligns them with `frontend/src/lib/api.ts` and component types.

---

## Testing Decisions

We test at the highest possible seams:
1. **API Integration Tests (`tests/test_api_endpoints.py`):**
   - Add tests for `GET /api/history` and verify session retrieval.
   - Verify `POST /api/vision/analyze` responds at the correct single `/api/vision/analyze` endpoint.
   - Verify `POST /api/diagnosis/analyze` commits records to the database.
2. **Frontend Type & Build Seam:**
   - Execute `npx tsc --noEmit` to ensure complete type safety across all updated components.
3. **Database Repository Seam (`tests/unit/test_database.py`):**
   - Retain 9/9 passing tests for `DiagnosisRepository`.

---

## Out of Scope

- Model retraining: Existing weights in `models/vision_resnet50.pth` and `models/prediction_xgboost_*.joblib` are treated as frozen assets.
- Production authentication server: Development uses standard API-key middleware or dev bypass.
- Replacing LangGraph with another orchestration engine.
