# Task Plan: AegisMed Phase 1 Implementation (PRD.md → Code)

## Goal
Implement PRD Phase 1: Grad-CAM heatmap explainability for the vision agent, the DEMAT (Dynamic Entropy-Minimizing Active Triage) engine wired into the follow-up/refine diagnosis loop, and Gemini Flash via OmniRoute — with all existing tests staying green.

## Next Step
Phase 1 implementation complete and verified. Ready for next project phase.

## Current Phase
Completed

## Phases

### Phase 1: Vision Foundation Fixes
- [x] Architecture auto-detect from checkpoint (`fc.weight` shape: 512→resnet18, 2048→resnet50) — fixes silent untrained-model bug
- [x] Label fix: `DISEASE_CLASSES[14]` "Normal" → "No Finding" (match training labels)
- [x] Error-path fix: error dicts include all VisionResponse keys (no more 500s)
- [x] Register model in `src/utils/model_cache.py` for cross-request reuse
- **Status:** completed

### Phase 2: Grad-CAM Engine + API + Frontend Heatmap
- [x] New `src/agents/vision/gradcam.py`: GradCAM class (hook on layer4[-1], backward outside no_grad, α_k spatial mean, ReLU weighted sum, normalize, jet colormap, blend, base64 PNG)
- [x] `VisionAgent.run()`: compute heatmap for argmax class; add `heatmap`, `heatmap_class`, `heatmap_confidence` to result
- [x] `src/api/routes/vision.py`: extend VisionResponse with optional heatmap fields
- [x] Frontend `api.ts` + `VisionUploader.tsx`: heatmap overlay card with opacity slider
- **Status:** completed

### Phase 3: DEMAT Engine (src/core package)
- [x] `src/core/disease_kb.py`: extract DISEASE_DATABASE from diagnosis.py (routes import from here)
- [x] `src/core/demat.py`: DEMATEngine — initial belief P(D) (symptom overlap × history priors), shannon_entropy(), Bayesian update_from_answer(), expected_info_gain(), select_questions(k), stopping criteria (H≤0.45 bits / 3 rounds / IG<0.02), serializable TriageState
- [x] `src/core/question_bank.py`: clinical questions with P(option|disease) likelihood tables
- **Status:** completed

### Phase 4: DEMAT Wiring (Endpoints + Frontend Q&A)
- [x] `/diagnosis/follow-up`: entropy-driven question selection, `has_more` from projected entropy, triage metadata in response
- [x] `/diagnosis/refine`: Bayesian posterior update → inject `demat_posterior` into orchestrator synthesis prompt
- [x] Frontend: `fetchFollowUpQuestions()`/`refineDiagnosis()` in api.ts, new `FollowUpQuestions.tsx`, 3-state diagnosis page flow
- **Status:** completed

### Phase 5: Gemini 3.8 Flash via OmniRoute
- [x] `config/settings.py`: `omniroute_base_url` / `omniroute_api_key` / `omniroute_model` (`antigravity/gemini-3.8-flash-high`)
- [x] `OpenRouterClient.__init__`: switch base URL when Omniroute configured
- [x] Verified live generation: "Gemini 3.8 Flash is active via OmniRoute"
- **Status:** completed

### Phase 6: Tests + Verification
- [x] `tests/unit/test_demat.py` (entropy math, IG selection, Bayesian updates, stopping, monotonic entropy decrease)
- [x] `tests/unit/test_gradcam.py` (heatmap shape/range/valid base64 vs real checkpoint)
- [x] Update `TestVisionEndpoint` valid-image test to assert heatmap key
- [x] Full `pytest` green: 110 passed, 0 failed, 17 skipped
- [x] `npx tsc --noEmit`: 0 errors
- [x] Restarted backend and live-verified both endpoints via requests/curl
- **Status:** completed

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| Auto-detect ResNet arch from checkpoint fc.weight shape | Checkpoint is actually ResNet-18 while code builds ResNet-50 → silent untrained-model bug; auto-detect is robust to either |
| Heatmap for argmax class even below 0.5 threshold | Shows where the model looked regardless of findings; better explainability |
| In-memory TriageState keyed by session_id | Matches existing `_conversations` pattern in chat.py; simplest stateful flow |
| Extract DISEASE_DATABASE to src/core/disease_kb.py | Avoids routes↔core circular import; single source of truth for DEMAT |
| Pure numpy jet colormap (no matplotlib) | Self-contained; avoids new dependency |
| Accept both "heart_disease" and "heart disease" in priors | Frontend sends underscore, backend matched space — pre-existing silent bug |
| LLM stays as optional question narrator; selection is mathematical (information gain) | The inventive/patentable step is the algorithm, not the prompt |
| antigtavity/gemini-3.8-flash-high via OmniRoute on port 20128 | Active provider with valid session; sub-second live completion |

## Errors Encountered
| Error | Resolution |
|-------|------------|
| `test_nlp_agent.py` failed with `RuntimeError: There is no current event loop` | In Python 3.12+, `asyncio.get_event_loop().run_until_complete()` fails without an active loop; switched to `asyncio.run()` |
| Round 2 DEMAT follow-up did not decrease entropy | `session.asked_question_ids` was checked instead of `session.answered_question_ids`; added separate tracking so previous answers update belief |
