# Live Demo Script

> Multi-Agent AI Health Diagnostic System — B.Tech Final Year Presentation
> 
> **Duration**: 12-15 minutes
> **Mode**: Demo Mode (recommended for smooth presentation)

---

## Pre-Demo Checklist (5 minutes before)

- [ ] Open terminal, navigate to project directory
- [ ] Run: `streamlit run frontend/app.py`
- [ ] Wait for Streamlit to load at `http://localhost:8501`
- [ ] Open browser to `http://localhost:8501`
- [ ] Verify all pages load: Diagnosis, Vision, Chat, History, About
- [ ] **Do NOT start the API server** unless demonstrating live AI (Demo Mode works without it)

---

## Demo Flow

### 1. Introduction (1 minute)

**What to say:**
> "This is a Multi-Agent AI Health Diagnostic System that uses 8 specialized AI agents working together to analyze patient symptoms, medical images, and clinical knowledge to produce diagnostic reports."

**Action:**
- Show the **About** page briefly
- Point out the architecture in the sidebar

---

### 2. Text Diagnosis — Chest Pain Scenario (3 minutes)

**What to say:**
> "Let me start with a text-based diagnosis. I'll use a pre-built scenario of a 55-year-old male with chest pain."

**Steps:**
1. Navigate to **Diagnosis** page
2. Toggle **Demo Mode** ON (in sidebar)
3. Select scenario: **"Chest Pain"**
4. Click **"Run Diagnosis"**
5. Point out:
   - Agent status indicators (NLP, RAG, Prediction, Vision)
   - Severity badge (HIGH — orange)
   - Confidence bars for each condition
   - Red flags section
   - AI Analysis Summary
   - Recommendations

**Expected Output:**
- Primary condition: Cardiovascular Disease (85% confidence)
- Secondary: Angina (72% confidence)
- Red flags: Chest pain radiating to left arm, shortness of breath
- Action: Seek emergency care

---

### 3. Text Diagnosis — Common Cold Scenario (1 minute)

**What to say:**
> "Now let me show a mild case to demonstrate how severity varies."

**Steps:**
1. Select scenario: **"Common Cold"**
2. Click **"Run Diagnosis"**
3. Point out:
   - Severity badge (LOW — green)
   - Lower confidence scores
   - Different recommendations (rest, hydration)

---

### 4. Voice Input Demo (2 minutes)

**What to say:**
> "The system also accepts voice input. Patients can speak their symptoms, and the audio is transcribed using OpenAI Whisper."

**Steps:**
1. Click the **Voice Input** tab
2. Click **"Start Recording"**
3. Speak: *"I have had a headache for three days with sensitivity to light"*
4. Click **"Stop Recording"**
5. Show transcribed text appearing
6. Explain: "The transcribed text feeds into the same NLP pipeline"

**Note:** Requires `OPENAI_API_KEY` in `.env`. If unavailable, explain the architecture without running.

---

### 5. Vision / X-ray Analysis (3 minutes)

**What to say:**
> "Now let me demonstrate the medical image analysis. The system can detect 15 different chest X-ray conditions."

**Steps:**
1. Navigate to **Vision** page
2. Toggle **Use Demo Mode** ON (sidebar)
3. Select: **"Pneumonia Case"**
4. Click **"Load Demo Case"**
5. Point out:
   - Primary finding: Pneumonia (89% confidence)
   - Secondary findings: Consolidation (62%), Infiltration (45%)
   - Severity: HIGH (orange)
   - Confidence bar chart (Plotly)
   - AI Recommendation
6. Switch to: **"Pneumothorax Case"**
7. Point out:
   - Critical severity (red)
   - Emergency recommendation
   - How the system escalates for life-threatening conditions

---

### 6. Report Export (1 minute)

**What to say:**
> "After each diagnosis, the system can generate formatted reports in PDF, CSV, or text format."

**Steps:**
1. Go back to **Diagnosis** page
2. Run any scenario (e.g., Chest Pain)
3. Scroll to **Export Report** section
4. Click **"Download PDF"** → show formatted PDF
5. Click **"Download CSV"** → show structured data
6. Explain: "These reports can be shared with healthcare providers"

---

### 7. History Page (1 minute)

**What to say:**
> "All diagnoses can be saved to a history log for tracking over time."

**Steps:**
1. Click **"Save to History"** on any results page
2. Navigate to **History** page
3. Point out:
   - Summary stats (total records, severity breakdown)
   - Filter by type (text/vision) and severity
   - Export as CSV/JSON
4. Show a saved record's details

---

### 8. Chat Agent (1 minute)

**What to say:**
> "Finally, the system includes a conversational medical Q&A agent."

**Steps:**
1. Navigate to **Chat** page
2. Type: *"What are the symptoms of pneumonia?"*
3. Send message
4. Show response (may take 10-30 seconds if API is running)
5. If API is NOT running: explain the architecture and move on

---

## Troubleshooting

| Issue | Solution |
|---|---|
| Streamlit won't start | Run `pip install -r requirements.txt` |
| Demo Mode not showing | Check sidebar — toggle must be ON |
| Vision page missing | Restart Streamlit: `streamlit run frontend/app.py` |
| Voice not transcribing | Verify `OPENAI_API_KEY` in `.env` |
| API server errors | Use Demo Mode instead — no API needed |
| Slow loading | CPU inference is slow; Demo Mode is instant |
| "Module not found" errors | Run from project root: `cd "Final Year Project"` |

---

## Backup Plan (If Demo Mode Fails)

1. **Pre-recorded screenshots**: Keep screenshots of each page ready
2. **Static results**: Show saved PDF reports from previous runs
3. **Architecture walkthrough**: Focus on the system design diagram
4. **Code walkthrough**: Show agent implementations in the IDE

---

## Timing Guide

| Section | Time | Priority |
|---|---|---|
| Introduction | 1 min | Required |
| Chest Pain Demo | 3 min | Required |
| Common Cold Demo | 1 min | Optional |
| Voice Input | 2 min | Optional |
| Vision Demo | 3 min | Required |
| Report Export | 1 min | Required |
| History | 1 min | Optional |
| Chat | 1 min | Optional |
| **Total** | **13 min** | |

**Minimum viable demo** (if time is short):
1. Introduction (30 sec)
2. Chest Pain Demo (2 min)
3. Vision Demo (2 min)
4. Report Export (30 sec)
= **5 minutes total**
