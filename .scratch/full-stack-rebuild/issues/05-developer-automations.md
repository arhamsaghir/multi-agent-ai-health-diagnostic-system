# Ticket 5: Developer Automations (Post-Edit Hook & API Contract Sync)

**Status:** `ready-for-agent`  
**Blocked by:** `01-fix-vision-route-and-client.md`, `03-wire-diagnosis-and-chat-apis.md`  

## Context & Problem
As identified by `claude-automation-recommender`, maintaining a hybrid Python/FastAPI and TypeScript/Next.js repository without automated contract checking leads to silent drift between backend Pydantic models and frontend client interfaces.

## Vertical Slice Work
1. **Post-Edit Linter Hook:**
   - Create `.zcode/hooks/post-edit.sh` (executable).
   - If Python file modified: run `ruff check --fix` or `python -m py_compile`.
   - If TypeScript/TSX file modified: verify syntax and run fast formatter.
2. **API Contract Verification Tool:**
   - Create a lightweight verification script or skill (`scripts/verify_api_contracts.py` or `.zcode/skills/sync-api-contracts/SKILL.md`) that inspects FastAPI routes (`/api/diagnosis/analyze`, `/api/vision/analyze`, `/api/chat/message`, `/api/history`) and ensures `frontend/src/lib/api.ts` defines matching endpoints and required payload keys.

## Acceptance Criteria
- Running the contract verification script flags any endpoint route discrepancies or missing schema fields.
- Post-edit hook script is executable and validates modified source files.
