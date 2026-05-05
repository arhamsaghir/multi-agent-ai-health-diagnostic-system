# Quick Start Guide

> Multi-Agent AI Health Diagnostic System — Get running in 5 minutes

---

## 1-Minute Setup

```bash
# 1. Navigate to project
cd "Final Year Project"

# 2. Install dependencies (first time only)
pip install -r requirements.txt

# 3. Start the app
streamlit run frontend/app.py
```

Open: `http://localhost:8501`

---

## Demo in 3 Steps

1. **Go to Diagnosis page** → Toggle **Demo Mode** ON
2. **Select a scenario** → Click **Run Diagnosis**
3. **View results** → Click **Download PDF**

That's it. No API keys needed.

---

## Enable All Features

Add to `.env` file:

```bash
OPENROUTER_API_KEY=sk-or-v1-your-key
OPENAI_API_KEY=sk-proj-your-key
```

Then restart: `streamlit run frontend/app.py`

---

## Run Tests

```bash
python -m pytest tests/ -v
```

Expected: **82 passed, 10 skipped**

---

## Start API Server

```bash
uvicorn src.api.main:app --reload --port 8000
```

Docs: `http://localhost:8000/docs`

---

## Need Help?

- Full manual: `docs/user_manual.md`
- Demo script: `docs/demo_script.md`
- README: `README.md`
