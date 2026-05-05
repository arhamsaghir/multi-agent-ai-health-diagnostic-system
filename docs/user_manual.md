# User Manual

> Multi-Agent AI Health Diagnostic System
> 
> Version: 0.1.0 | Last Updated: 2026-05-05

---

## Table of Contents

1. [Overview](#1-overview)
2. [Installation](#2-installation)
3. [Configuration](#3-configuration)
4. [Running the System](#4-running-the-system)
5. [Using Each Feature](#5-using-each-feature)
6. [Troubleshooting FAQ](#6-troubleshooting-faq)

---

## 1. Overview

The Multi-Agent AI Health Diagnostic System is an AI-powered medical diagnosis platform that uses 8 specialized agents working together to:

- **Extract symptoms** from patient descriptions (NLP Agent)
- **Analyze medical images** — X-rays, MRIs (Vision Agent)
- **Retrieve medical knowledge** from clinical guidelines (RAG Agent)
- **Calculate disease risk scores** using machine learning (Prediction Agent)
- **Transcribe spoken symptoms** (Voice Agent)
- **Synthesize diagnostic reports** using LLMs (Synthesis Agent)
- **Coordinate all agents** for a unified diagnosis (Orchestrator Agent)

### Who Is This For?

- **Students/Researchers**: Study multi-agent AI architectures for healthcare
- **Developers**: Learn how to build agentic AI systems with LangGraph
- **Healthcare Professionals**: Explore AI-assisted diagnostic workflows (research only)

---

## 2. Installation

### Prerequisites

- **Python 3.11+** (tested with 3.13)
- **pip** (Python package manager)
- **Git** (for cloning the repository)

### Step-by-Step Installation

```bash
# 1. Clone or navigate to the project
cd "Final Year Project"

# 2. Create a virtual environment
python3 -m venv venv

# 3. Activate the virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Verify installation
python -c "import streamlit, fastapi, torch; print('All dependencies installed')"
```

### Optional Dependencies

- **reportlab** (PDF export) — included in requirements.txt
- **openai** (voice transcription) — included in requirements.txt
- **plotly** (charts) — included in requirements.txt

---

## 3. Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required for LLM features
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Optional — for voice transcription
OPENAI_API_KEY=sk-proj-your-key-here

# Optional — for Gemini synthesis
GOOGLE_API_KEY=AIza-your-key-here
```

### Getting API Keys

| Provider | URL | Cost |
|---|---|---|
| OpenRouter | https://openrouter.ai | Free tier available |
| OpenAI | https://platform.openai.com | Pay-per-use (Whisper is cheap) |
| Google AI | https://ai.google.dev | Free tier available |

### Without API Keys

The system works in **Demo Mode** without any API keys. All features are available with pre-computed results.

---

## 4. Running the System

### Option A: Streamlit Frontend (Recommended)

```bash
# Start the web interface
streamlit run frontend/app.py

# Or use Makefile
make frontend
```

Open your browser to: `http://localhost:8501`

### Option B: API Server + Frontend

```bash
# Terminal 1: Start API server
uvicorn src.api.main:app --reload --port 8000

# Terminal 2: Start frontend
streamlit run frontend/app.py
```

API docs available at: `http://localhost:8000/docs`

### Verifying the System

1. Open `http://localhost:8501`
2. Navigate to the **About** page
3. Verify the architecture diagram loads
4. Go to **Diagnosis** and toggle **Demo Mode**
5. Select a scenario and click **Run Diagnosis**
6. Results should appear within 2 seconds (Demo Mode)

---

## 5. Using Each Feature

### 5.1 Text Diagnosis

**Purpose**: Analyze patient symptoms described in text.

**Steps**:
1. Go to **Diagnosis** page
2. Toggle **Demo Mode** ON (sidebar) for instant results, or OFF for live AI
3. Either:
   - Type symptoms in the text area, OR
   - Select a pre-built scenario from the dropdown
4. Fill in optional details: age, BMI, gender, family history
5. Click **Run Diagnosis**
6. Review results: severity, conditions, red flags, recommendations
7. Click **Download PDF** or **Download CSV** to export the report

### 5.2 Voice Input

**Purpose**: Speak symptoms instead of typing.

**Steps**:
1. Go to **Diagnosis** page → **Voice Input** tab
2. Click **Start Recording**
3. Speak your symptoms clearly
4. Click **Stop Recording**
5. Wait for transcription (2-5 seconds)
6. The transcribed text appears in the symptom field
7. Edit if needed, then click **Run Diagnosis**

**Requirements**: `OPENAI_API_KEY` must be set in `.env`

### 5.3 Medical Image Analysis

**Purpose**: Analyze X-ray, MRI, or CT images for anomalies.

**Steps**:
1. Go to **Vision** page
2. Toggle **Use Demo Mode** ON (sidebar) for instant results
3. Either:
   - Upload an image file (PNG, JPG, JPEG, TIFF), OR
   - Select a demo case from the dropdown
4. Click **Analyze Image** (if uploading) or **Load Demo Case** (if using demo)
5. Review findings: detected conditions, confidence scores, severity
6. View the confidence distribution chart
7. Click **Save to History** to store the result

**Supported Conditions** (15 chest X-ray classes):
Atelectasis, Cardiomegaly, Effusion, Infiltration, Mass, Nodule, Pneumonia, Pneumothorax, Consolidation, Edema, Emphysema, Fibrosis, Pleural Thickening, Hernia, Normal

### 5.4 Medical Chat

**Purpose**: Ask medical questions in a conversational format.

**Steps**:
1. Go to **Chat** page
2. Type your question (e.g., "What are the symptoms of diabetes?")
3. Click **Send**
4. Wait for the AI response (10-30 seconds)
5. Continue the conversation — context is maintained
6. View past conversations in the sidebar

**Requirements**: API server must be running (`uvicorn src.api.main:app`)

### 5.5 Diagnosis History

**Purpose**: Track and review past diagnoses.

**Steps**:
1. After any diagnosis or image analysis, click **Save to History**
2. Go to **History** page
3. View all saved records with:
   - Date/time
   - Type (text diagnosis or image analysis)
   - Primary finding/condition
   - Severity level
   - Confidence score
4. Filter by type or severity using sidebar controls
5. Export all records as CSV or JSON

### 5.6 Report Export

**Purpose**: Generate shareable diagnostic reports.

**Available Formats**:
- **PDF**: Formatted report with severity badges, confidence charts, and recommendations (requires reportlab)
- **CSV**: Structured data for spreadsheet analysis
- **Text**: Plain text summary for quick sharing

**Steps**:
1. Run any diagnosis or image analysis
2. Scroll to the **Export Report** section
3. Click the desired format button
4. The file downloads automatically

---

## 6. Troubleshooting FAQ

### Q: Streamlit won't start — "ModuleNotFoundError"

**A**: Ensure you're running from the project root directory and dependencies are installed:
```bash
cd "Final Year Project"
pip install -r requirements.txt
streamlit run frontend/app.py
```

### Q: Demo Mode doesn't show results

**A**: Make sure Demo Mode is toggled ON in the sidebar, then select a scenario and click "Run Diagnosis."

### Q: Voice transcription fails

**A**: Verify your `OPENAI_API_KEY` is set in the `.env` file. Test it with:
```bash
python -c "from openai import OpenAI; import os; c = OpenAI(api_key=os.environ['OPENAI_API_KEY']); print(c.models.list())"
```

### Q: API server returns 500 errors

**A**: Check the terminal running uvicorn for error messages. Common causes:
- Missing API keys
- Model files not present
- Port 8000 already in use

### Q: "XGBoost segfault" error

**A**: This is a known issue with XGBoost on Python 3.13/macOS. The system automatically falls back to scikit-learn GradientBoosting. No action needed.

### Q: Vision analysis is slow

**A**: CPU inference takes 10-30 seconds per image. Use Demo Mode for instant results during presentations.

### Q: PDF export doesn't work

**A**: Ensure `reportlab` is installed:
```bash
pip install reportlab
```

### Q: Chat agent doesn't respond

**A**: The API server must be running. Start it with:
```bash
uvicorn src.api.main:app --reload --port 8000
```

### Q: How do I reset the app?

**A**: In Streamlit, click the **🔄 Rerun** button in the top-right corner, or refresh the browser page.

### Q: Where are logs stored?

**A**: Application logs are in the `logs/` directory, rotated daily.

---

## Support

For issues, bugs, or questions:
1. Check this manual's troubleshooting section
2. Review the `README.md` for known limitations
3. Check application logs in `logs/`
4. Contact the project team

---

*This system is for research and educational purposes only. It does not replace professional medical diagnosis.*
