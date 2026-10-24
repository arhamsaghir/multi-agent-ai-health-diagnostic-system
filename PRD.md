# Product Requirements Document (PRD)

## Project Title: Multi-Agent AI Clinical Diagnostic & Triage System (AegisMed)
**Document Version:** 1.0.0  
**Status:** Approved for Implementation & Patent Development  
**Lead Architect:** Arham Saghir  
**Target Milestone:** Production-Grade Clinical Decision Support System (CDSS) & Patent Specification  

---

### Executive Summary & Vision Statement

Modern clinical diagnostic tools suffer from a fatal trilemma:
1. **Shallow Rule-Based Triage:** Rigid decision trees cannot capture complex, nuanced patient presentations.
2. **Black-Box Deep Learning:** Monolithic vision or classification models output uncalibrated probabilities with zero spatial or pathophysiological explainability.
3. **Unanchored Generative LLMs:** Conversational medical chatbots hallucinate diagnoses, provide conflicting advice across dialogue turns, and exhibit catastrophic safety failures when multimodal inputs contradict each other.

**AegisMed** is a patent-oriented, production-ready, multi-agent Clinical Decision Support System (CDSS) designed to solve this trilemma. By pairing domain-specific specialist agents (Computer Vision, Clinical NLP, Biostatistical Risk Scoring, FAISS Literature RAG) with a mathematically verified **Dynamic Entropy-Minimizing Active Triage (DEMAT)** engine and an **Evidential Neuro-Symbolic Conflict Arbitration Framework (EN-SCAF)**, AegisMed transforms AI healthcare from speculative generative chat into a deterministic, uncertainty-bounded medical instrument.

---

### Table of Contents
1. [Target Personas & Clinical User Journeys](#1-target-personas--clinical-user-journeys)
2. [Product Scope & System Boundaries](#2-product-scope--system-boundaries)
3. [Core Algorithmic Innovations (Patentable Architecture)](#3-core-algorithmic-innovations-patentable-architecture)
4. [Functional Requirements & Specialist Agent Specifications](#4-functional-requirements--specialist-agent-specifications)
5. [Frontend & Clinical User Experience (UX)](#5-frontend--clinical-user-experience-ux)
6. [Data Model, Persistence & Interoperability](#6-data-model-persistence--interoperability)
7. [Non-Functional, Latency & Reliability Requirements](#7-non-functional-latency--reliability-requirements)
8. [Regulatory, Safety & Compliance Framework](#8-regulatory-safety--compliance-framework)
9. [Patent Claims & Intellectual Property (IP) Mapping](#9-patent-claims--intellectual-property-ip-mapping)
10. [Release Roadmap & Phased Execution Plan](#10-release-roadmap--phased-execution-plan)

---

### 1. Target Personas & Clinical User Journeys

#### Persona 1: Dr. Priya Sharma (Emergency Department Triage Physician)
* **Goal:** Rapidly categorize acute patient presentations into Emergency Severity Index (ESI Levels 1–5), identify life-threatening "don't-miss" conditions, and order high-yield diagnostic workups in under 90 seconds.
* **Pain Points:** High cognitive load during peak hours, missing subtle radiological findings on chest X-rays, alert fatigue from naive keyword systems.
* **User Journey:**
  1. Patient presents to ED triage; Dr. Sharma scans the patient wristband or uploads chest X-ray + presenting vitals.
  2. The system executes the multimodal pipeline in <2.5 seconds.
  3. The **Clinician Dashboard** highlights an overlaid Grad-CAM heatmap showing left basilar lung consolidation and an automated ICD-10 differential list ranked with Dempster-Shafer consensus scores.
  4. Dr. Sharma clicks "Export FHIR Bundle" directly into the hospital EHR.

#### Persona 2: Rajesh Kumar (Rural/Remote Patient)
* **Goal:** Understand whether his chest discomfort and fatigue require an immediate 40km trip to a district hospital or can be managed with local primary care.
* **Pain Points:** High medical anxiety, inability to interpret complex lab values, lack of immediate access to specialists.
* **User Journey:**
  1. Opens the mobile-responsive web portal and speaks in colloquial language: *"Chest feels heavy since morning, pain spreads to my left neck."*
  2. The **DEMAT Engine** detects high clinical entropy between *Angina Pectoris* and *Gastroesophageal Reflux* and prompts a single high-gain question: *"Does the pain worsen during physical movement or when lying flat?"*
  3. Upon receiving the response, the system identifies an emergency red flag, sounds an audible alert, renders a high-urgency **Safety Warning**, and produces an emergency contact checklist.

---

### 2. Product Scope & System Boundaries

#### In-Scope
* Multimodal symptom triaging spanning free-text clinical notes, voice transcripts, tabular physiological vitals, and chest radiograph imaging (DICOM/PNG).
* Mathematical active question selection minimizing Shannon entropy over differential diagnoses.
* Neuro-symbolic validation filtering LLM hallucinated diagnoses against the Unified Medical Language System (UMLS) and SNOMED-CT knowledge graphs.
* Statistically bounded uncertainty quantification using Split Conformal Prediction.
* Standardized healthcare interoperability via HL7 FHIR Release 4 JSON schemas.
* Dual-persona interface (Patient Plain-Language vs. Clinician Diagnostic Station).

#### Out-of-Scope (Version 1.0–2.0)
* Autonomous pharmacological prescribing without human-in-the-loop clinician sign-off.
* Direct device driver integration with hardware bedside monitors (ICU telemetry streaming).
* Primary surgical planning and 3D organ volumetric segmentation.

---

### 3. Core Algorithmic Innovations (Patentable Architecture)

```
                            PATIENT PRESENTATION
                         (Text, Image, Vitals, Voice)
                                      │
                                      ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │  INVENTION 1: Dynamic Entropy-Minimizing Active Triage (DEMAT)   │
    │  Initial Prior P(D) ──> Calculate H(D) ──> Select Argmax I(D;Q) │
    └─────────────────────────────────┬────────────────────────────────┘
                                      │ (If H(D) > Threshold)
                                      ▼
                        Targeted Clarification Loop
                                      │
                                      ▼ (If H(D) <= Threshold)
    ┌──────────────────────────────────────────────────────────────────┐
    │  PARALLEL MULTI-AGENT EXECUTION                                  │
    │  ├─ NLP Specialist: BioBERT Entity & Attribute Extractor         │
    │  ├─ Vision Specialist: ResNet-50 + Grad-CAM Saliency Engine      │
    │  ├─ Predictive Risk: GradientBoosting + Longitudinal LSTM        │
    │  └─ Knowledge Specialist: FAISS Dense Clinical Guideline RAG     │
    └─────────────────────────────────┬────────────────────────────────┘
                                      │
                                      ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │  INVENTION 2: Evidential Neuro-Symbolic Arbiter (EN-SCAF)        │
    │  ├─ Dempster-Shafer Mass Assignment: m_nlp, m_vis, m_risk       │
    │  ├─ Orthogonal Conflict Discounting: K = Sum(B cap C = Empty)    │
    │  └─ UMLS Knowledge Graph Hard Logic Pruning Gate                 │
    └─────────────────────────────────┬────────────────────────────────┘
                                      │
                                      ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │  INVENTION 3: Multimodal Conformal Risk-Controlled Synthesis    │
    │  Non-conformity Score s(X, Y) ──> Coverage Guarantee >= (1 - a) │
    └─────────────────────────────────┬────────────────────────────────┘
                                      │
                                      ▼
                             CLINICAL DELIVERABLE
              (Dual-Mode UI, FHIR R4 Bundle, Certified PDF)
```

#### 3.1. Dynamic Entropy-Minimizing Active Triage (DEMAT) Engine
* **Mathematical Foundation:** Let $D = \{d_1, d_2, \dots, d_N\}$ denote the set of candidate medical conditions. The system models the current diagnostic state as a categorical probability distribution $P(D \mid \mathbf{x})$.
* **Entropy Metric:** The diagnostic ambiguity is quantified via Shannon Entropy:
  $$H(D) = -\sum_{i=1}^N P(d_i \mid \mathbf{x}) \log_2 P(d_i \mid \mathbf{x})$$
* **Information Gain Optimization:** Given candidate clinical questions/tests $Q = \{q_1, \dots, q_M\}$ associated with observable outcomes $A_q$, the engine selects:
  $$q^* = \arg\max_{q \in Q} I(D; A_q) = \arg\max_{q \in Q} \left[ H(D) - \sum_{a \in A_q} P(A_q = a) H(D \mid A_q = a) \right]$$
* **Stopping Criteria:** The interrogation halts when $H(D) \le \epsilon_{\text{triage}}$ ($0.45\text{ bits}$) or when round count $t \ge 3$, preventing cognitive fatigue.

#### 3.2. Evidential Neuro-Symbolic Conflict Arbitration Framework (EN-SCAF)
* **Belief Mass Formulation:** Each specialist agent $k \in \{\text{NLP}, \text{Vision}, \text{Prediction}\}$ maps its inference to a Dempster-Shafer belief mass function $m_k: 2^\Theta \to [0, 1]$, where $\sum_{A \subseteq \Theta} m_k(A) = 1$.
* **Conflict Coefficient ($K$):** Cross-agent disagreement is mathematically quantified:
  $$K = \sum_{B \cap C = \emptyset} m_{\text{vision}}(B) \cdot m_{\text{clinical}}(C)$$
* **Symbolic Graph Validation:** If $K > 0.40$ (indicating irreconcilable disagreement), candidate hypotheses are projected onto the **UMLS Metathesaurus Knowledge Graph**. Hard biological axioms (e.g., *Ischemic heart disease cannot be causally explained by isolated bacterial pharyngitis*) prune non-conforming nodes prior to LLM narrative generation.

#### 3.3. Multimodal Conformal Risk-Controlled Synthesis (MCRC-DS)
* **Statistical Guarantee:** Rather than outputting a single point prediction, AegisMed outputs a conformal prediction set $\mathcal{C}(\mathbf{X}_{\text{new}})$ that guarantees:
  $$\mathbb{P}\left(Y_{\text{true}} \in \mathcal{C}(\mathbf{X}_{\text{new}})\right) \ge 1 - \alpha$$
  where $\alpha = 0.05$ represents a 95% statistical safety coverage bound.

---

### 4. Functional Requirements & Specialist Agent Specifications

#### 4.1. Vision Specialist Agent (`src/agents/vision/`)
* **FR-VIS-01:** Support single-frame and multi-frame 8-bit and 16-bit medical scans (Chest X-Ray, CT slice) across JPEG, PNG, and DICOM standards.
* **FR-VIS-02:** Execute deep convolutional inference over 15 distinct pulmonary and cardiothoracic pathologies (Atelectasis, Cardiomegaly, Effusion, Infiltration, Mass, Nodule, Pneumonia, Pneumothorax, Consolidation, Edema, Emphysema, Fibrosis, Pleural Thickening, Hernia, Normal).
* **FR-VIS-03 (Explainability Engine):** Compute Gradient-weighted Class Activation Mapping (Grad-CAM) at the final convolutional layer (`layer4` of ResNet-50).
  * Generate a normalized $224 \times 224$ float32 attention heatmap:
    $$L_{\text{Grad-CAM}}^c = \text{ReLU}\left(\sum_k \alpha_k^c A^k\right), \quad \alpha_k^c = \frac{1}{Z}\sum_i \sum_j \frac{\partial Y^c}{\partial A_{i,j}^k}$$
  * Blend heatmap with original scan using a jet colormap at 45% alpha opacity and return as base64 data URI to the client.

#### 4.2. Clinical NLP Agent (`src/agents/nlp/`)
* **FR-NLP-01:** Tokenize and extract biomedical Named Entities using pre-trained BioBERT (`dmis-lab/biobert-v1.1`).
* **FR-NLP-02:** Extract semantic assertions:
  * Entity Class: Symptom, Anatomical Site, Severity, Temporal Duration, Negation Status.
  * Negation Detection: Identify negated symptoms (e.g., *"denies shortness of breath"*, *"no history of fever"*) using dependency parse trees.
* **FR-NLP-03 (Fallback Rule Extractor):** If GPU/BioBERT inference is degraded, automatically fall back to deterministic regex tokenizers mapping against 12 anatomical systems without interrupting the request.

#### 4.3. Biostatistical Prediction Agent (`src/agents/prediction/`)
* **FR-PRED-01:** Ingest structured physiological vitals: Age, Sex, BMI, Systolic BP, Diastolic BP, Heart Rate, Respiratory Rate, Oxygen Saturation ($\text{SpO}_2$), Temperature, and Family History flags.
* **FR-PRED-02:** Execute pre-trained scikit-learn/XGBoost Gradient Boosting ensembles to compute disease-specific odds ratios and risk scores across Cardiovascular, Respiratory, Metabolic, and Neurological domains.

#### 4.4. Literature RAG Agent (`src/agents/rag/`)
* **FR-RAG-01:** Maintain an on-disk dense vector index (`data/vector_store/medical_knowledge.faiss`) using `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional embeddings).
* **FR-RAG-02:** Scale document store from baseline to 5,000+ verified clinical summaries (Gold-standard clinical practice guidelines: AHA/ACC, GOLD, ATS/IDSA, WHO protocols).
* **FR-RAG-03:** Enforce cosine similarity threshold $\ge 0.65$; return top-5 retrieved passages with strict source provenance (DOI, Guideline Organization, Publication Year).

#### 4.5. Orchestrator & Synthesis Engine (`src/agents/orchestrator/`, `src/agents/synthesis/`)
* **FR-SYN-01:** Support multi-model routing prioritizing Gemini 3.8 Flash via O‍mniroute / OpenRouter with sub-second execution.
* **FR-SYN-02:** Enforce strict Pydantic JSON schema output parsing:
  ```json
  {
    "primary_diagnosis": "string",
    "icd10_code": "string",
    "confidence_score": "float [0.0 - 1.0]",
    "conformal_set": ["string"],
    "severity": "critical | high | moderate | low",
    "triage_category": "ESI-1 | ESI-2 | ESI-3 | ESI-4 | ESI-5",
    "doctor_alert": "boolean",
    "differential_diagnoses": [
      {"condition": "string", "icd10": "string", "confidence": "float", "rationale": "string"}
    ],
    "evidence_citations": [{"source": "string", "excerpt": "string"}],
    "red_flags": ["string"],
    "recommended_actions": ["string"],
    "patient_explanation": "string",
    "clinician_summary": "string"
  }
  ```
* **FR-SYN-03:** Automatic failover to `RuleBasedSynthesizer` upon network timeout ($>30\text{s}$), HTTP 429, or invalid JSON syntax.

---

### 5. Frontend & Clinical User Experience (UX)

The user interface is built on Next.js 16 (App Router), Tailwind CSS v4, Lucide React, and Framer Motion.

#### 5.1. Live Multi-Agent Execution Stepper
* When a user clicks "Analyze Symptoms & Scans", the UI replaces the static loading spinner with an animated **Agent DAG Workflow Visualizer**:
  * Step 1: `NLP Specialist` (Pulsing green ring; displays badge: *"3 symptoms parsed, Negation checked"*).
  * Step 2: `Vision Specialist` (Renders miniature scan thumbnail; displays badge: *"ResNet-50 Grad-CAM computed"*).
  * Step 3: `Predictive Risk` (Displays badge: *"Vitals mapped to risk curve"*).
  * Step 4: `RAG Retrieval` (Displays badge: *"FAISS retrieved 5 clinical papers"*).
  * Step 5: `Arbitration & Synthesis` (Displays badge: *"Dempster-Shafer consensus reached"*).

#### 5.2. Dual-Mode View Switcher (Patient vs. Clinician)
* **Mode Toggle:** A sticky header switch allowing instant toggle between **"Patient Friendly"** and **"Clinician Diagnostic"** views.
  * **Patient View:** 
    * Severity Gauge (Low / Moderate / High / Critical).
    * Plain-language breakdown without medical jargon.
    * What to do next & emergency call triggers.
  * **Clinician View:**
    * Tabular Differential Diagnoses with ICD-10 codes and confidence distributions.
    * Saliency Map with interactive zoom and Grad-CAM opacity slider ($0\% \to 100\%$).
    * Diagnostic Workup Order list (e.g., *"Order CBC, Troponin-I serial markers, 12-lead ECG"*).
    * Evidential mass distribution chart and agent agreement metrics.

#### 5.3. One-Click Clinical PDF Report Exporter
* Client-side and server-side PDF generator producing an official **AegisMed Clinical Diagnostic Summary**:
  * Includes hospital/clinic header, patient demographic box, vitals grid, X-ray thumbnail with Grad-CAM overlay, differential table, doctor sign-off block, and mandatory legal disclaimers.

---

### 6. Data Model, Persistence & Interoperability

#### 6.1. SQLite Persistence Schema (`data/diagnostic.db`)
```sql
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    user_input TEXT NOT NULL,
    symptoms_json TEXT NOT NULL,
    image_path TEXT,
    patient_history_json TEXT,
    status TEXT DEFAULT 'completed',
    triage_entropy REAL,
    entropy_rounds INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS diagnoses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL,
    condition_name TEXT NOT NULL,
    icd10_code TEXT,
    confidence REAL NOT NULL,
    severity TEXT NOT NULL,
    conformal_bound REAL,
    rationale TEXT
);

CREATE TABLE IF NOT EXISTS agent_outputs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL,
    output_json TEXT NOT NULL,
    execution_time_ms REAL NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    action TEXT NOT NULL,
    actor TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    checksum_sha256 TEXT NOT NULL
);
```

#### 6.2. HL7 FHIR R4 Export Format
The `/api/history/{session_id}/fhir` endpoint returns a standardized FHIR JSON `Bundle`:
* `Resource: Patient` (Vitals and demographic details).
* `Resource: Observation` (Extracted symptoms, $\text{SpO}_2$, Blood Pressure).
* `Resource: Media / DiagnosticReport` (Chest X-ray metadata and Grad-CAM findings).
* `Resource: Condition` (Primary diagnosis and ranked differentials coded in ICD-10 and SNOMED-CT).

---

### 7. Non-Functional, Latency & Reliability Requirements

| Metric / Attribute | Production Target | Validation Method |
| :--- | :--- | :--- |
| **End-to-End Latency (Cached)** | $< 800\text{ ms}$ | Automated benchmark via Locust / pytest |
| **End-to-End Latency (Full Pipeline)** | $< 2,500\text{ ms}$ (with Gemini Flash) | Synthetic load test over 50 concurrent requests |
| **API Availability / Uptime** | $99.95\%$ | Monitored through `/health` health check probes |
| **Failover Guarantee** | $100\%$ zero-crash fallback | Chaos testing: kill OpenRouter API $\to$ assert Rule-based output |
| **Grad-CAM Generation Latency** | $< 350\text{ ms}$ on CPU, $< 45\text{ ms}$ on CUDA | Tensor profiling during image upload pipeline |
| **TypeScript Type Safety** | 0 build errors (`tsc --noEmit`) | CI pre-commit hook enforcement |
| **Unit & Integration Test Coverage** | $\ge 90\%$ code path coverage | Automated pytest test runner |

---

### 8. Regulatory, Safety & Compliance Framework

#### 8.1. Software as a Medical Device (SaMD) Classification
* **Regulatory Context:** Designed under **FDA 21 CFR Part 820** and **EU MDR 2017/745 (Class IIa/IIb SaMD)** guidelines as a Clinical Decision Support System.
* **Non-Autonomous Principle:** The system operates strictly as decision support; every recommendation must feature human-in-the-loop validation with an explicit physician sign-off step.

#### 8.2. Medical Disclaimers & Emergency Guardrails
* **Red-Flag Interceptor:** If input tokens match acute emergency keywords (*"chest crushing pain"*, *"cannot breathe"*, *"coughing blood"*, *"one-sided facial droop"*), the system bypasses standard queues, renders an immediate red emergency banner with local ambulance dialing links, and sets `doctor_alert: true`.
* **Universal Disclaimer:** Every UI page and PDF export mandates:
  > *"AegisMed is an AI-powered clinical decision support system designed for triage and educational assistance. It does not replace independent clinical judgment or physical examination by a licensed medical practitioner."*

#### 8.3. Data Privacy & Cryptographic Integrity
* **De-identification:** All patient names and phone numbers are stripped via HIPAA Safe Harbor de-identification rules before vectorization or LLM prompt formatting.
* **Audit Trail:** Every write operation is stamped with a SHA-256 hash checksum in `audit_logs` to ensure forensic non-repudiation.

---

### 9. Patent Claims & Intellectual Property (IP) Mapping

| Claim Identifier | Title / Technical Focus | Core Inventive Step | Target Specification Section |
| :--- | :--- | :--- | :--- |
| **Claim 1 (Independent)** | **Dynamic Entropy-Minimizing Active Triage (DEMAT)** | Sequential maximization of expected mutual information $I(D; A_q)$ over directed medical ontologies to halt diagnostic interrogation at minimum entropy. | Method & Apparatus Claims |
| **Claim 2 (Dependent)** | **Dempster-Shafer Orthogonal Multi-Agent Conflict Discounting** | Mathematical formulation of cross-agent disagreement parameter $K$ between pixel tensors and linguistic representations. | Method Claims |
| **Claim 3 (Dependent)** | **Neuro-Symbolic DAG Pruning Gate** | Hard constraint logic evaluation using UMLS DAG paths to prune impossible clinical co-occurrences prior to natural language synthesis. | System & Memory Claims |
| **Claim 4 (Independent)** | **Multimodal Conformal Risk-Controlled Diagnostic Bounding** | Generation of dynamically sized differential diagnosis sets with provable $1 - \alpha$ frequentist coverage over multimodal patient inputs. | Software Media & Method Claims |

---

### 10. Release Roadmap & Phased Execution Plan

```
┌────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: ALGORITHMIC HARDENING & GRAD-CAM (Weeks 1–4)                  │
│ • Implement PyTorch Grad-CAM hook on ResNet-50                         │
│ • Wire interactive side-by-side heatmap slider in /vision              │
│ • Connect Gemini 3.8 Flash via O‍mniroute endpoint                      │
│ • Unit tests for DEMAT Shannon entropy calculator                      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: VISUAL MULTI-AGENT PIPELINE & DUAL-MODE UI (Weeks 5–8)        │
│ • Implement animated execution stepper in /diagnosis                   │
│ • Build Clinician vs. Patient persona toggle switch                    │
│ • Expand RAG FAISS store from 10 to 500+ curated disease summaries     │
│ • Deliver client/server PDF Medical Report generator                   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: PROVISIONAL PATENT FILING & RESEARCH BENCHMARK (Weeks 9–14)   │
│ • Benchmark DEMAT against MIMIC-IV-CXR and MedQA                       │
│ • Draft formal technical specification & patent diagrams               │
│ • Submit Provisional Patent Application to Patent Office (IPO / USPTO) │
│ • Submit research paper to academic conference (CHIL / MICCAI)         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ PHASE 4: PRODUCTION CLINICAL PILOT & FHIR INTEGRATION (Months 4–8)     │
│ • Implement bidirectional HL7 FHIR R4 Bundle import/export             │
│ • Package containerized on-premise Docker stack with TensorRT INT8     │
│ • Execute retrospective IRB-approved hospital data validation          │
│ • File global PCT International Patent Application                     │
└────────────────────────────────────────────────────────────────────────┘
```

---

### Approval & Sign-Off

| Stakeholder | Role | Date | Signature |
| :--- | :--- | :--- | :--- |
| **Arham Saghir** | Lead System Architect & Developer | 2026-10-04 | *[Signed electronically]* |
| **Academic Supervisor** | Department of Computer Science & Engineering | Pending | `_______________________` |
| **Clinical Advisory Board** | Medical Evaluation & Validation Lead | Pending | `_______________________` |
| **Registered Patent Agent** | Intellectual Property Law Firm | Pending | `_______________________` |
