# Ticket 2: Wire SQLite Diagnosis Persistence and History API

**Status:** `ready-for-agent`  
**Blocked by:** None  

## Context & Problem
`DiagnosisRepository` in `src/data/database/repository.py` passes all unit tests, but is completely unused by FastAPI routes. When `/api/diagnosis/analyze` completes, the diagnostic session is not stored in SQLite. There is no `/api/history` endpoint, and `frontend/src/components/history/DiagnosisHistory.tsx` displays static mock records.

## Vertical Slice Work
1. **Backend Route Creation:** Create `src/api/routes/history.py` with:
   - `GET /api/history`: List recent diagnostic sessions with diagnosis summaries.
   - `GET /api/history/{session_id}`: Fetch detailed record for a session.
2. **Mount History Router:** Include `history.router` in `src/api/main.py`.
3. **Wire Persistence into Diagnosis:** In `src/api/routes/diagnosis.py:analyze_symptoms`, call `DiagnosisRepository.save_session()` and `DiagnosisRepository.save_diagnosis()` for each detected condition upon successful analysis.
4. **Frontend API Client:** Add `fetchHistory(): Promise<DiagnosisRecord[]>` in `frontend/src/lib/api.ts`.
5. **Frontend Component:** Update `DiagnosisHistory.tsx` to load records from `fetchHistory()` on mount with loading skeleton and error states.
6. **Backend Test:** Add integration tests for `/api/history` in `tests/test_api_endpoints.py`.

## Acceptance Criteria
- Running `/api/diagnosis/analyze` creates rows in the SQLite `sessions` and `diagnoses` tables.
- `GET /api/history` returns the persisted sessions.
- Navigating to `/history` on the Next.js app fetches and renders saved sessions.
