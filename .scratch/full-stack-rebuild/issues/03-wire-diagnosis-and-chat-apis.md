# Ticket 3: Wire Live Diagnosis & Chat Endpoints in Next.js

**Status:** `ready-for-agent`  
**Blocked by:** `02-session-persistence-and-history.md`  

## Context & Problem
`frontend/src/lib/api.ts` hardcodes `demoMode: boolean = true`, meaning symptom diagnosis requests never hit `/api/diagnosis/analyze`.
`frontend/src/components/chat/MedicalChat.tsx` answers questions from a static dictionary after a fake delay, never contacting `/api/chat/message`.

## Vertical Slice Work
1. **Frontend API Client (`api.ts`):**
   - Update `diagnose()` default to `demoMode = false`.
   - Ensure the request body matches `DiagnosisRequest` expected by FastAPI (`text`, `patient_history`, etc.).
   - Implement `sendChatMessage(message: string, conversationId?: string): Promise<ChatMessageResponse>` calling `/api/chat/message`.
2. **Diagnosis Page (`frontend/src/app/diagnosis/page.tsx`):**
   - Remove fake `setTimeout(resolve, 1500)`.
   - Pass real user symptoms and patient history directly to `diagnose()`.
   - Add graceful error display if backend is offline, with a one-click toggle to view demo results.
3. **Medical Chat Component (`MedicalChat.tsx`):**
   - Replace in-memory dictionary lookup with `sendChatMessage()`.
   - Persist `conversationId` in component state for continuous conversational context across messages.
   - Display backend disclaimer and timestamp from the response.

## Acceptance Criteria
- Typing symptoms on `/diagnosis` sends an HTTP POST request to `/api/diagnosis/analyze` and renders the real differential diagnosis.
- Sending a message on `/chat` sends an HTTP POST to `/api/chat/message` and displays the response from the backend.
- Both pages remain responsive and show helpful error messages if the backend server is unreachable.
