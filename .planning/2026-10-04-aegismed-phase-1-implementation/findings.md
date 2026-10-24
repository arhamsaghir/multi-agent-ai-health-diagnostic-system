# Findings & Decisions

## Requirements
- Execute PRD.md Phase 1: Grad-CAM explainability, DEMAT entropy triage engine, Gemini Flash via OmniRoute
- All existing tests (99 passed, 17 skipped) must stay green
- Frontend demo fallbacks must keep working (new API fields optional everywhere)

## Research Findings

### Vision pipeline (from exploration)
- **CRITICAL BUG:** `models/vision_resnet50.pth` is actually a **ResNet-18** checkpoint — verified: `fc.weight` shape `[15, 512]` (512-dim features = ResNet-18/34), `layer4` blocks are BasicBlock (no conv3). `VisionAgent._load_model()` builds `models.resnet50` (`fc = Linear(2048, 15)`), `load_state_dict` raises shape mismatch, generic `except Exception` swallows it → **API serves an untrained, randomly-initialized ResNet-50 on every request**.
- Label mismatch: agent `DISEASE_CLASSES[14] = "Normal"`; checkpoint trained with `"No Finding"` (per `scripts/generate_synthetic_xray_images.py` DISEASE_LABELS and `TestVisionModelDirect`).
- Error path: `run()` failure returns `{"error", "findings", "confidence"}` — doesn't satisfy `VisionResponse` (missing `total_detected`/`highest_confidence`/`anomalies`) → 500s.
- No cross-request model reuse: `vision.py` builds a new `VisionAgent()` (and fresh model) per request. `src/utils/model_cache.py` exists (thread-safe singleton, `register`/`get`/`release`) but is **completely unused**.
- `ImagePreprocessor.preprocess_for_model` returns float32 `(3, 224, 224)` (C,H,W), plain LANCZOS resize (no letterbox), ImageNet mean/std normalization, transpose to channels-first.
- Inference runs inside `torch.no_grad()` — **Grad-CAM must run outside it** (needs gradients on activations + target logit).
- torch 2.11.0 / torchvision 0.26.0 available on CPU. No Grad-CAM code exists anywhere in repo.

### Diagnosis follow-up flow (from exploration)
- `/diagnosis/follow-up` exists: LLM prompt → up to 3 questions `{question, type: text|choice|yes_no, options, category, rationale}` in `FollowUpResponse{questions, has_more, session_id}`. `has_more` hardcoded `True`; `session_id` a fresh UUID, not persisted.
- `/diagnosis/refine` exists: string-concatenates answers into text and re-runs the orchestrator.
- **Frontend never calls either endpoint** — no UI for follow-up exists; diagnosis page is a strict two-state input↔results AnimatePresence swap.
- `_generate_rule_based_questions(text)`: keyword-triggered static questions (duration/severity/associated_symptoms/medical_history).
- Disease universe for DEMAT: `DISEASE_DATABASE` in diagnosis.py (9 diseases with name/icd10/symptoms/causes/risk_factors/...); rule-based prediction produces keys `cardiovascular_disease`, `diabetes`, `respiratory_infection`, `neurological_disorder`.
- **Family-history bug:** frontend sends `"heart_disease"` (underscore); backend rule-based scorer matches `"heart disease"` (space) → priors silently wrong.
- Orchestrator: prediction agent only runs when `patient_history` is non-None; NLP produces 11 symptom categories + 14 body systems.
- DiagnosticState keys: user_input, symptoms, image_path, patient_history, voice_transcript, {vision,nlp,rag,prediction,synthesis}_result, confidence_score, severity, doctor_alert, tasks_to_run, errors.

### OmniRoute
- Local OpenAI-compatible proxy; default port `20128` (`PORT=20128` per README/.env.example).
- Gemini models synced live from the user's Google key (e.g. `gemini/gemini-3-flash`); exact "flash 3.8" slug discoverable via `/v1/models` at runtime.
- Project at `/Users/arhamsaghir/OmniRoute` (dev server with esbuild companion observed running in earlier ps output).

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| Auto-detect ResNet arch from checkpoint `fc.weight` shape (512→resnet18, 2048→resnet50) | Fixes silent untrained-model bug; robust to either checkpoint |
| Heatmap computed for argmax class even below 0.5 reporting threshold | Shows where the model looked regardless of findings |
| In-memory TriageState dict keyed by session_id (chat.py `_conversations` pattern) | Simplest stateful multi-turn flow; no schema changes |
| Extract DISEASE_DATABASE to `src/core/disease_kb.py` | Avoids routes↔core circular import; single source of truth |
| Numpy jet colormap implementation (no matplotlib) | Self-contained, no new dependency |
| Accept both `"heart_disease"` and `"heart disease"` in priors | Fixes frontend/backend token mismatch |
| LLM stays as optional question narrator; selection is mathematical (information gain) | The inventive/patentable step is the algorithm, not the prompt |

## Issues Encountered
| Issue | Resolution |
|-------|------------|

## Resources
- PRD.md (product spec), REFERENCES.md, chapter2_literature_review.md
- planning session: `.planning/2026-10-04-aegismed-phase-1-implementation/`
