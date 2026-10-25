# Ticket 4: Build Healthcare Diagnostic Landing Portal

**Status:** `ready-for-agent`  
**Blocked by:** None  

## Context & Problem
`frontend/src/app/page.tsx` currently displays the stock Next.js starter template ("To get started, edit the page.tsx file..."), giving an incomplete first impression for project evaluators and users.

## Vertical Slice Work
1. **Design Healthcare Dashboard in `frontend/src/app/page.tsx`:**
   - **Hero Section:** Clear title ("Multi-Agent AI Clinical Diagnostic System"), value proposition, and primary CTA buttons ("Start Symptom Check", "Analyze X-Ray Scan", "Clinical Chat").
   - **Live System Status Bar:** Displays active status of backend agents (NLP, Vision, RAG, Prediction, Synthesis).
   - **Quick Action Cards:** Direct links to `/diagnosis`, `/vision`, `/chat`, and `/history` with concise capability descriptions.
   - **Multi-Agent Pipeline Overview:** Visual architecture card explaining how the 5 agents collaborate (NLP symptom extraction → FAISS knowledge retrieval → XGBoost risk scoring → ResNet-50 imaging → Gemini/Nemotron synthesis).
2. **Polish Responsive Styling:** Ensure sleek dark and light mode styling using Tailwind CSS v4 and Lucide React icons.

## Acceptance Criteria
- Opening `http://localhost:3000/` displays a professional clinical diagnostic portal.
- All CTA buttons and cards route correctly to their respective functional pages.
- TypeScript compiles cleanly without errors (`npx tsc --noEmit`).
