# Multi-Agent AI Health Diagnostic System

> B.Tech Final Year Project — A multi-agent AI system for medical diagnosis using agentic AI orchestration, deep learning, and RAG.

## 🎨 New: Next.js Frontend

The project now features a **modern Next.js 16 + React 19 frontend** with:
- 🎨 Modern healthcare-themed UI (teal palette #0F766E)
- 📱 Fully mobile responsive with sidebar navigation
- 🌓 Dark mode toggle (next-themes)
- ✨ Framer Motion scroll animations
- 📊 Recharts data visualizations
- ♿ WCAG 2.2 accessible (passed a11y audit)

## Architecture

```
┌───────────────────────────────────────────────────────┐
│                    Next.js Frontend (NEW)                  │
│  ┌───────────────────────────────────────────────┐  │
│  │  Diagnosis │ Vision │ Chat │ History │ About    │  │
│  │  NLP Input │ X-Ray  │ Q&A  │Records │System   │  │
│  └───────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌───────────────────────────────────────────────────────┐
│                     Orchestrator Agent (LangGraph)        │
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │ NLP Agent│  │Vision    │  │RAG Agent │  │Prediction Agent  │   │
│  │(Clinical │  │(ResNet)  │  │(FAISS)   │  │(GradientBoosting)│   │
│  │   NLP)   │  │          │  │          │  │                  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬─────────┘   │
│       │              │             │                  │             │
│       ▼              ▼             ▼                  ▼             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Confidence Scorer & Severity Engine              │  │
│  └──────────────────────────────┬───────────────────────────────┘  │
│                                 │                                  │
│                                 ▼                                  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Report Synthesis (OpenRouter LLM / Rule-Based Fallback)     │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|---|---|
| **Orchestration** | LangGraph `StateGraph` (agent routing), DEMAT (evidence arbitration), EN-SCAF (risk bounding) |
| **LLMs** | OpenRouter/OmniRoute free-tier + Gemini fallback, rule-based synthesis when offline |
| **Deep Learning** | PyTorch (CPU), ResNet (vision), optional biomedical NER checkpoint (NLP) |
| **RAG** | FAISS vector store, 500 provenance-bearing passages from 9 guideline sources, 25-query evaluation |
| **ML Models** | scikit-learn GradientBoosting (4 disease models), rule-based fallback |
| **Frontend** | Next.js 16 + React 19 + TypeScript + Tailwind CSS v4 |
| **Animations** | Framer Motion (scroll-triggered, staggered) |
| **Charts** | Recharts (confidence visualization) |
| **Voice** | OpenAI Whisper API (speech-to-text, optional) |
| **API** | FastAPI (diagnosis, chat, vision, SSE stream, PDF report, FHIR R4) |
| **Interoperability** | HL7 FHIR R4 (`fhir.resources` 8.3.0) — Bundle in/out |
| **Deployment** | Docker + Compose (Next.js standalone + FastAPI, CPU-only, non-root) |
| **Inference Export** | ONNX Runtime (CPU, parity-verified); TensorRT INT8 `BLOCKED: GPU host` |
| **Report Export** | reportlab (PDF), csv (CSV), plain text |
| **Testing** | pytest (214 tests: 197 passed, 17 skipped) |

## Quick Start

### Prerequisites
- Python 3.11+ (tested with 3.13)
- OpenRouter API key (free-tier models only)
- OpenAI API key (optional, for voice transcription)

### Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys:
# OPENROUTER_API_KEY=your-key-here
# OPENAI_API_KEY=your-key-here  (optional, for voice)

# 4. Start the FastAPI backend
make api
# or: uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# 5. Start the Next.js frontend (separate terminal)
cd frontend
npm install
npm run dev
# or: frontend/node_modules/.bin/next dev
```

The portal is then at <http://localhost:3000> and the API at <http://localhost:8000>.

### Container Deployment (On-Prem)

```bash
cp .env.example .env        # set SECRET_KEY and your API keys
docker compose build
docker compose up -d
docker compose ps            # both services report "healthy"
```

The frontend is served on port 3000; the API stays bound to loopback because
the browser reaches it through the frontend's same-origin proxy. Model
weights and the vector store are mounted from the host, not baked into the
images. Full runbook: [`docs/deploy/CONTAINER_DEPLOYMENT.md`](docs/deploy/CONTAINER_DEPLOYMENT.md).

### Demo Mode (Recommended for Presentations)

The UI includes a **Demo Mode** toggle that uses pre-computed results for instant display. This is recommended for live demonstrations as it bypasses slow CPU inference and LLM latency.

1. Launch the Next.js portal
2. Go to the **Diagnosis** page
3. Toggle **Demo Mode** on
4. Select from 5 pre-built patient scenarios:
   - **Chest Pain**: 55yo male with chest pain radiating to left arm, shortness of breath, history of hypertension → High severity, Cardiovascular Disease
   - **Respiratory Infection**: 35yo female with persistent cough, fever, yellow-green phlegm → Moderate severity, Pneumonia
   - **Diabetes Screening**: 48yo with excessive thirst, frequent urination, fatigue → Moderate severity, Type 2 Diabetes
   - **Neurological Symptoms**: 28yo with severe headaches, light sensitivity, nausea → High severity, Migraine
   - **Common Cold**: 22yo with runny nose, sore throat, mild fever → Low severity, Upper Respiratory Infection

### Vision Demo

1. Go to the **Vision** page
2. Toggle **Use Demo Mode** on
3. Select a demo case:
   - **Pneumonia Case** — 89% confidence
   - **Normal Chest X-ray** — 92% confidence
   - **Cardiomegaly Case** — 78% confidence
   - **Pneumothorax Case** — 85% confidence (Critical severity)
4. Click **Load Demo Case** to see formatted results with confidence charts

## Project Structure

```
├── config/                  # Configuration & settings
├── src/
│   ├── agents/
│   │   ├── orchestrator/    # LangGraph task planner & router
│   │   ├── vision/          # ResNet medical image analysis + Grad-CAM
│   │   ├── nlp/             # BioBERT symptom extraction
│   │   ├── rag/             # Medical knowledge retrieval (FAISS)
│   │   ├── prediction/      # GradientBoosting risk scoring (4 disease models)
│   │   ├── voice/           # OpenAI Whisper speech-to-text
│   │   ├── synthesis/       # GenAI report synthesis (Gemini)
│   │   └── rule_based_synthesis.py  # LLM fallback report generator
│   ├── core/                # DEMAT engine, disease KB, question bank, FHIR mapping
│   ├── api/
│   │   ├── main.py          # FastAPI entry point (CORS, validation, health)
│   │   ├── progress.py      # SSE run-event bus for live agent tracing
│   │   └── routes/          # Diagnosis, chat, vision, stream, report, history, FHIR
│   ├── llm/
│   │   ├── openrouter_client.py     # OpenRouter API client (30s timeouts)
│   │   └── gemini_client.py         # Report synthesis with fallback
│   ├── data/
│   │   ├── preprocessing/   # Text, image, tabular preprocessors
│   │   ├── embedding.py     # Sentence transformer embeddings
│   │   └── vector_store/    # FAISS index + metadata
│   └── utils/
│       └── report_exporter.py       # PDF/CSV/Text report generation
├── frontend/                # Next.js 16 + React 19 clinical portal
│   ├── src/app/             # Landing, diagnosis, vision, chat, history, about
│   ├── src/components/      # Execution stepper, persona toggle, results, uploader
│   ├── src/app/api/backend/ # Same-origin proxy to the FastAPI backend
│   └── Dockerfile           # Multi-stage standalone build
├── scripts/
│   ├── benchmark/           # Phase 3 research benchmark + metrics
│   └── deploy/              # ONNX export scaffold for CPU inference
├── clinical/                # (Phase 4.3) IRB validation protocol — BLOCKED
├── docs/deploy/             # Container runbook + TensorRT INT8 runbook
├── paper/                   # CHIL manuscript (LaTeX + PDF)
├── patent/                  # Provisional patent package (12 claims + figures)
├── data/                    # Datasets, vector stores, benchmark evidence
├── tests/                   # Unit & integration tests (197 passed / 17 skipped)
├── models/                  # Saved model weights (vision, prediction)
└── logs/                    # Application logs
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | System health check with agent status |
| `POST` | `/api/diagnosis/analyze` | Run multi-agent diagnosis on text input |
| `POST` | `/api/diagnosis/analyze-with-image` | Analyze uploaded X-ray image |
| `POST` | `/api/diagnosis/analyze-stream` | Same, streamed as SSE agent progress events |
| `POST` | `/api/diagnosis/refine-stream` | DEMAT arbitration refinement, streamed |
| `POST` | `/api/diagnosis/follow-up` | Next triage question from the question bank |
| `POST` | `/api/vision/analyze` | Vision agent analysis + Grad-CAM heatmap |
| `POST` | `/api/report/generate` | One-click clinical PDF report |
| `POST` | `/api/fhir/diagnose` | HL7 FHIR R4 Bundle in → Bundle out |
| `GET` | `/api/fhir/diagnosis/{id}` | Export a stored session as a FHIR Bundle |
| `GET` | `/api/history` | Past diagnosis sessions (SQLite) |
| `POST` | `/api/chat/message` | Send message to medical chat agent |
| `GET` | `/api/chat/conversations` | List all chat conversations |
| `GET` | `/api/chat/conversation/{id}` | Get specific conversation |
| `DELETE` | `/api/chat/conversation/{id}` | Delete conversation |
| `POST` | `/api/chat/conversation/{id}/summarize` | Summarize conversation |

## API Keys

| Provider | Purpose | Get Key |
|---|---|---|
| OpenRouter | All LLM calls (free-tier models) | openrouter.ai |
| OpenAI | Whisper (voice-to-text) — optional | platform.openai.com |
| HuggingFace | Optional biomedical NER checkpoint — only when `ENABLE_BIOBERT_NER=true` | huggingface.co |

### Service authentication

The clinical API is protected by a service API key that is **enforced by
default**. Clients send it as an `X-API-Key` header; the browser portal never
sees it, because the Next.js proxy attaches it server-side.

| Setting | Default | Effect |
|---|---|---|
| `ENFORCE_API_KEY` | `true` | Require a valid key on every non-public endpoint |
| `SECRET_KEY` | *(empty)* | The key itself — must be set outside development |
| `ALLOW_INSECURE_DEV` | `true` | Development-only bypass; ignored outside `APP_ENV=development` |

In production the service refuses to start unless `SECRET_KEY` is set and
`ENFORCE_API_KEY` is on, and the interactive OpenAPI docs are disabled.
Set `ALLOW_INSECURE_DEV=false` to require the key even in development.

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_api_endpoints.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=term-missing
```

### Test Results

| Test Suite | Tests | Status |
|---|---|---|
| API Endpoints | 26 | ✅ All passed |
| Deployment assets | 28 | ✅ All passed |
| Integration Comprehensive | 22 | ⚠️ 15 passed, 7 skipped |
| Preprocessing (Unit) | 16 | ✅ All passed |
| NLP Agent (Unit) | 12 | ✅ All passed |
| SSE stream progress (Unit) | 11 | ✅ All passed |
| Confidence Scorer | 11 | ✅ All passed |
| Report Exporter (Unit) | 10 | ✅ All passed |
| FHIR R4 mapping (Unit) | 10 | ✅ All passed |
| Database (Unit) | 9 | ✅ All passed |
| Persona explanations (Unit) | 8 | ✅ All passed |
| ONNX export & parity | 8 | ✅ All passed |
| DEMAT benchmark harness (Unit) | 7 | ✅ All passed |
| Integration | 7 | ✅ All passed |
| DEMAT engine (Unit) | 6 | ✅ All passed |
| Embedding (Unit) | 5 | ✅ All passed |
| FHIR endpoints | 5 | ✅ All passed |
| RAG agent (Unit) | 3 | ✅ All passed |
| Grad-CAM (Unit) | 3 | ✅ All passed |
| Report endpoint (Unit) | 1 | ✅ All passed |
| **Total** | **214** | **197 passed, 17 skipped** |

**Note**: the skipped tests are documented Python 3.13 / XGBoost compatibility
issues on macOS (segmentation fault during model pickle load). The prediction
agent handles this gracefully by falling back to scikit-learn GradientBoosting
with rule-based risk scoring.

## Results & Evaluation

### Model Performance

Every number below is reproducible from an artifact in this repository. The
artifact that produced each metric is named in the last column.

| Model | Training Data | Validation Metric | Result | Artifact |
|---|---|---|---|---|
| Vision (ResNet) | 4,500 synthetic X-rays (15 classes) | Validation loss | 0.0562 (reported at training time; no artifact retained) | `scripts/train_vision_model.py` |
| Prediction (GradientBoosting) | 500 synthetic patient records | Accuracy per disease | cardiovascular 90%, respiratory 96%, diabetes 99%, neurological 91% | `models/prediction_xgboost_metadata.json` |
| RAG (FAISS) | 500 passages from 9 guideline sources | Top-5 hit rate, 25-query evaluation | 100% | `data/knowledge/guidelines/rag_eval.json` |
| NLP (clinical patterns) | Rule-based clinical pattern catalogue | — | No accuracy benchmark is published; extraction is deterministic and covered by unit tests | `tests/unit/test_nlp_agent.py` |

**Not measured:** there is no published accuracy or F1 figure for the NLP
extractor, and the vision validation loss above is a training-time report
rather than a re-runnable evaluation. The `data/benchmark_results.json` file
covers a synthetic 200-case knowledge-base lookup (100% top-1 by
construction) and is not a clinical accuracy measure.

### Agent Coverage

| Agent | Function | Status |
|---|---|---|
| Orchestrator | Task planning & routing (LangGraph `StateGraph`) | ✅ Active |
| NLP | Symptom extraction, severity assessment | ✅ Active — deterministic patterns; biomedical NER model is optional and off by default (`ENABLE_BIOBERT_NER`) |
| Vision | Chest X-ray anomaly detection (15 conditions) | ✅ Active — checkpoint architecture is detected at load time (ResNet-18 or ResNet-50) |
| RAG | Medical guideline retrieval | ✅ Active — falls back to raw retrieved passages when no LLM is reachable |
| Prediction | Disease risk scoring (4 models) | ✅ Active — scikit-learn GradientBoosting via joblib, rule-based fallback |
| Voice | Speech-to-text transcription | ⚙️ Optional — requires an OpenAI API key |
| Synthesis | Report generation (LLM + fallback) | ✅ Active — LLM when a provider is reachable, rule-based report otherwise |

`GET /health` reports the live state of every agent and model instead of
advertising a fixed "all active" list.

### System Capabilities
- **5 demo scenarios** covering cardiovascular, respiratory, metabolic, neurological, and infectious conditions
- **4 vision demo cases**: pneumonia, normal, cardiomegaly, pneumothorax
- **PDF/CSV/Text report export** with formatted diagnostic reports
- **Voice input** with OpenAI Whisper API transcription
- **Chat interface** for multi-turn medical Q&A
- **History tracking** with filter, search, and CSV export
- **Demo Mode** for instant results without API server

## Known Limitations

1. **Legacy XGBoost Artifacts**: The shipped risk models are scikit-learn `GradientBoostingClassifier` estimators in joblib files whose names still carry the `xgboost` prefix, and `scripts/train_prediction_model.py` still trains with XGBoost. XGBoost checkpoints can crash on macOS/Python 3.13 during unpickling; the agent falls back to rule-based scoring when a model cannot be loaded.
2. **CPU Inference Speed**: Full pipeline execution takes 2-5 minutes on CPU due to model loading and LLM latency. Use **Demo Mode** for instant results.
3. **Synthetic Vision Data**: The vision model was trained on procedurally generated X-ray images (4,500 images, 15 classes) for prototype validation. Production use requires real medical imaging data (e.g., NIH ChestX-ray14).
4. **Free-Tier LLM Latency**: OpenRouter free-tier models may have variable response times. The system implements 30-second timeouts with automatic fallback to rule-based synthesis.
5. **SQLite Persistence**: Diagnosis history is persisted to SQLite through the `./data` volume. A multi-instance deployment needs PostgreSQL for patient records and audit trails.
6. **Voice API Dependency**: Voice transcription requires an OpenAI API key. Without it, the voice tab shows a configuration message.
7. **No TLS or Portal Login**: The API enforces a service API key by default (see [API Keys](#api-keys)), but the container stack publishes the portal on port 3000 with no TLS termination and no end-user authentication. Deploy it behind the hospital's reverse proxy and access control.
8. **No Clinical Validation**: The deployment mechanism is not evidence of clinical efficacy. Retrospective validation under IRB approval (Phase 4.3) is still outstanding, and TensorRT INT8 quantization is `BLOCKED: GPU host` with no measured numbers.
9. **Unverified Metrics in Legacy Reports**: `FULL_PROJECT_REPORT.md` still cites a vision validation loss and an NLP F1 score that no artifact in this repository reproduces. The table above lists only metrics backed by a stored artifact.

## Future Work

1. **Real Medical Imaging Data**: Integrate NIH ChestX-ray14 dataset (112,120 images) for production-grade vision model training.
2. **Production Database**: Migrate to PostgreSQL for persistent patient records, audit trails, and compliance logging.
3. **Enhanced RAG Pipeline**: Expand medical knowledge base with PubMed articles, clinical guidelines, and drug interaction databases.
4. **Multi-Modal Input**: Combine text, voice, image, and structured lab results in a single diagnostic pipeline.
5. **Model Optimization**: Deploy models with ONNX/TensorRT for faster inference; add GPU support for real-time analysis.
6. **Clinical Validation**: Partner with healthcare providers for retrospective validation on real patient data.
7. **Regulatory Compliance**: Implement HIPAA/GDPR compliance, data encryption, and audit logging for production deployment.
8. **Mobile Application**: Develop React Native app for point-of-care diagnostics in resource-limited settings.

## Development

```bash
make test        # Run all tests
make lint        # Run linter
make format      # Format code
make clean       # Remove generated files
make api         # Start FastAPI backend
make frontend    # Start Next.js dev server
```

## Acknowledgments

- **Supervisor**: [Your Supervisor's Name], Department of Computer Science
- **Institution**: [Your University Name]
- **Open Source Libraries**: LangChain, LangGraph, CrewAI, PyTorch, scikit-learn, Streamlit, FastAPI, FAISS, LlamaIndex, OpenRouter
- **Medical Knowledge Sources**: CDC guidelines, WHO clinical protocols, MSLSD symptom ontology

## License

MIT — Academic project
