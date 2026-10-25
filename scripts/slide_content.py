#!/usr/bin/env python3
"""
Slide contents for AegisMed Academic Defense Presentation
"""

SLIDES = [
    # SLIDE 1
    """
    <section class="slide active" id="slide-1">
        <header class="slide-header">
            <div class="header-brand">
                <span class="brand-badge"><span class="brand-dot"></span>AEGISMED · CLINICAL INTELLIGENCE</span>
            </div>
            <div class="slide-number-tag">SLIDE 01 / 14</div>
        </header>
        <div class="slide-body" style="justify-content: center;">
            <div class="section-kicker">FINAL YEAR PROJECT VIVA &amp; DEFENSE // OCT 2026</div>
            <h1 class="slide-title" style="font-size: 76px; margin-bottom: 20px;">
                AegisMed: <span>Multi-Agent AI</span><br>Clinical Decision Support System
            </h1>
            <p class="slide-subtitle" style="font-size: 26px; max-width: 1200px; margin-bottom: 44px;">
                An Autonomous Multimodal Architecture for Explainable Diagnostic Triage, Active Entropy Minimization, and Neuro-Symbolic Safety Guardrails
            </p>
            <div class="grid-4col" style="max-width: 1300px;">
                <div class="metric-pill">
                    <span class="metric-num val-highlight">90.8%</span>
                    <span class="metric-desc">Thoracic Vision Macro mAP</span>
                </div>
                <div class="metric-pill">
                    <span class="metric-num val-highlight">&Delta;H=2.50b</span>
                    <span class="metric-desc">DEMAT Entropy Minimization</span>
                </div>
                <div class="metric-pill">
                    <span class="metric-num val-highlight">100%</span>
                    <span class="metric-desc">Clinical Scenario Concordance</span>
                </div>
                <div class="metric-pill">
                    <span class="metric-num val-highlight">FHIR R4</span>
                    <span class="metric-desc">Interoperable EHR Standard</span>
                </div>
            </div>
        </div>
        <footer class="slide-footer">
            <div class="footer-left">
                <strong>Candidate:</strong> Arham Saghir &nbsp;|&nbsp; <strong>Degree:</strong> Bachelor of Technology in Computer Science &amp; Engineering
            </div>
            <div class="footer-right">ADVISORY PANEL &amp; BOARD OF EXAMINERS</div>
        </footer>
    </section>
    """,

    # SLIDE 2
    """
    <section class="slide" id="slide-2">
        <header class="slide-header">
            <div class="header-brand">
                <span class="brand-badge"><span class="brand-dot"></span>AEGISMED</span>
                <span class="header-category">Problem Formulation</span>
            </div>
            <div class="slide-number-tag">SLIDE 02 / 14</div>
        </header>
        <div class="slide-body">
            <div class="section-kicker">01 // MOTIVATION &amp; CLINICAL BOTTLENECKS</div>
            <h2 class="slide-title">The Clinical Diagnostic <span>Trilemma</span></h2>
            <p class="slide-subtitle">
                Current computer-aided diagnostic systems fail in clinical deployment due to three deep structural limitations:
            </p>
            <div class="grid-3col">
                <div class="glass-card highlight">
                    <div class="card-accent-top"></div>
                    <div class="card-num">CHALLENGE 01</div>
                    <div class="card-title">Data Fragmentation</div>
                    <div class="card-text">
                        Medical information is trapped in disparate formats: unstructured clinical notes, DICOM radiographs, and tabular lab vitals. Single-modality tools force physicians to manually synthesize conflicting data, introducing severe cognitive fatigue and diagnostic error.
                    </div>
                    <div class="card-badge">Multimodal Disconnect</div>
                </div>
                <div class="glass-card highlight">
                    <div class="card-accent-top"></div>
                    <div class="card-num">CHALLENGE 02</div>
                    <div class="card-title">Black-Box Neural Predictors</div>
                    <div class="card-text">
                        Deep classification models output uncalibrated probabilities with zero spatial localization or pathophysiological explanation. Without visual saliency (e.g., Grad-CAM) or literature grounding, physicians cannot audit why a model predicted a life-threatening disease.
                    </div>
                    <div class="card-badge">Explainability Gap</div>
                </div>
                <div class="glass-card highlight">
                    <div class="card-accent-top"></div>
                    <div class="card-num">CHALLENGE 03</div>
                    <div class="card-title">Unanchored Generative LLMs</div>
                    <div class="card-text">
                        Commercial LLMs hallucinate diagnoses, drift across dialogue turns, and lack deterministic safety guardrails. When text symptoms contradict imaging findings, LLMs generate dangerously erratic triage advice with zero formal conflict arbitration.
                    </div>
                    <div class="card-badge">Safety &amp; Hallucination Risk</div>
                </div>
            </div>
        </div>
        <footer class="slide-footer">
            <div class="footer-left">AegisMed addresses this trilemma through cooperative multi-agent specialization and formal neuro-symbolic arbitration.</div>
            <div class="footer-right">CHAPTER 1: INTRODUCTION &amp; MOTIVATION</div>
        </footer>
    </section>
    """,

    # SLIDE 3
    """
    <section class="slide" id="slide-3">
        <header class="slide-header">
            <div class="header-brand">
                <span class="brand-badge"><span class="brand-dot"></span>AEGISMED</span>
                <span class="header-category">Research Objectives</span>
            </div>
            <div class="slide-number-tag">SLIDE 03 / 14</div>
        </header>
        <div class="slide-body">
            <div class="section-kicker">02 // RESEARCH GOALS &amp; NOVEL CONTRIBUTIONS</div>
            <h2 class="slide-title">From Probabilistic Chat to a <span>Verifiable Medical Instrument</span></h2>
            <p class="slide-subtitle">
                AegisMed's core hypothesis: medical safety demands autonomous specialist agents bound by mathematical triage and deterministic clinical rules.
            </p>
            <div class="grid-4col">
                <div class="glass-card">
                    <div class="card-num">OBJECTIVE 1</div>
                    <div class="card-title">Agentic Multimodal Co-Reasoning</div>
                    <div class="card-text">
                        Coordinate BioBERT (NLP), ResNet-50 (Vision), FAISS (RAG), and GBDT (Biometrics) inside a stateful LangGraph DAG orchestrator.
                    </div>
                    <div class="card-badge">LangGraph DAG</div>
                </div>
                <div class="glass-card">
                    <div class="card-num">INNOVATION 2 (PATENT)</div>
                    <div class="card-title">DEMAT Active Triage Engine</div>
                    <div class="card-text">
                        Formulate clinical inquiry as Shannon entropy minimization, selecting questions that maximize mutual information gain.
                    </div>
                    <div class="card-badge">Patent Claims 1–6</div>
                </div>
                <div class="glass-card">
                    <div class="card-num">INNOVATION 3 (PATENT)</div>
                    <div class="card-title">EN-SCAF Conflict Arbitration</div>
                    <div class="card-text">
                        Apply Dempster-Shafer evidential theory to formally arbitrate contradictory inputs between imaging and patient vitals.
                    </div>
                    <div class="card-badge">Patent Claims 7–12</div>
                </div>
                <div class="glass-card">
                    <div class="card-num">OBJECTIVE 4</div>
                    <div class="card-title">Interoperable Clinical Delivery</div>
                    <div class="card-text">
                        Generate validated HL7 FHIR R4 JSON bundles, exportable clinical PDF reports, and dual-persona (Clinician vs. Patient) synthesis.
                    </div>
                    <div class="card-badge">FHIR R4 &amp; WCAG 2.2</div>
                </div>
            </div>
        </div>
        <footer class="slide-footer">
            <div class="footer-left">Dual-track deliverable: Production-ready software artifact + 12-claim intellectual property patent package.</div>
            <div class="footer-right">CHAPTER 1.3 &amp; 1.4: RESEARCH NOVELTY</div>
        </footer>
    </section>
    """,

    # SLIDE 4
    """
    <section class="slide" id="slide-4">
        <header class="slide-header">
            <div class="header-brand">
                <span class="brand-badge"><span class="brand-dot"></span>AEGISMED</span>
                <span class="header-category">System Architecture</span>
            </div>
            <div class="slide-number-tag">SLIDE 04 / 14</div>
        </header>
        <div class="slide-body">
            <div class="section-kicker">03 // ARCHITECTURAL TOPOLOGY &amp; WORKFLOW</div>
            <h2 class="slide-title">LangGraph <span>Multi-Agent State Machine</span></h2>
            <p class="slide-subtitle">
                Asynchronous stateful execution pipeline routing patient inputs through dedicated specialists and verification layers.
            </p>
            <div class="grid-split-60-40">
                <div class="glass-card" style="padding: 24px;">
                    <div class="card-num">EXECUTION TOPOLOGY</div>
                    <div class="card-title" style="margin-bottom: 16px;">Deterministic Agent Handoff Pipeline</div>
                    <table class="spec-table">
                        <thead>
                            <tr>
                                <th>Stage</th>
                                <th>Executing Agent</th>
                                <th>Function &amp; Payload</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><span class="val-highlight">01. Ingest</span></td>
                                <td>Audio / Text Pipeline</td>
                                <td>Whisper transcription + DICOM image tensor conversion</td>
                            </tr>
                            <tr>
                                <td><span class="val-highlight">02. Parallel</span></td>
                                <td>NLP + Vision + GBDT</td>
                                <td>BioBERT entity spans || ResNet-50 forward pass || Vitals risk</td>
                            </tr>
                            <tr>
                                <td><span class="val-highlight">03. Ground</span></td>
                                <td>FAISS RAG Agent</td>
                                <td>Dense vector query across 10 gold-standard guidelines</td>
                            </tr>
                            <tr>
                                <td><span class="val-highlight">04. Triage</span></td>
                                <td>DEMAT Engine</td>
                                <td>Entropy calculation &amp; targeted follow-up question loop</td>
                            </tr>
                            <tr>
                                <td><span class="val-highlight">05. Arbitrate</span></td>
                                <td>EN-SCAF Guardrail</td>
                                <td>Dempster-Shafer fusion &amp; deterministic safety overrides</td>
                            </tr>
                            <tr>
                                <td><span class="val-highlight">06. Synthesize</span></td>
                                <td>Synthesis Agent</td>
                                <td>Dual-persona clinical report generation &amp; FHIR export</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div style="display: flex; flex-direction: column; gap: 20px;">
                    <div class="metric-pill">
                        <span class="metric-num val-highlight">6 Specialists</span>
                        <span class="metric-desc">Autonomous cooperating agents with isolated responsibilities</span>
                    </div>
                    <div class="metric-pill">
                        <span class="metric-num val-highlight">&le; 12 ms</span>
                        <span class="metric-desc">Deterministic red-line safety guardrail response time</span>
                    </div>
                    <div class="metric-pill">
                        <span class="metric-num val-highlight">Zero Discrete GPU</span>
                        <span class="metric-desc">Full CPU inference capability: accessible in low-resource hospitals</span>
                    </div>
                    <div class="metric-pill">
                        <span class="metric-num val-highlight">Stateful Rollback</span>
                        <span class="metric-desc">LangGraph message journal allows instant recovery on network drops</span>
                    </div>
                </div>
            </div>
        </div>
        <footer class="slide-footer">
            <div class="footer-left">Orchestration engine compiled with strict cyclical graph state: orchestrator/agent.py</div>
            <div class="footer-right">CHAPTER 4.1: SYSTEM ARCHITECTURE</div>
        </footer>
    </section>
    """,

    # SLIDE 5
    """
    <section class="slide" id="slide-5">
        <header class="slide-header">
            <div class="header-brand">
                <span class="brand-badge"><span class="brand-dot"></span>AEGISMED</span>
                <span class="header-category">Medical Vision Specialist</span>
            </div>
            <div class="slide-number-tag">SLIDE 05 / 14</div>
        </header>
        <div class="slide-body">
            <div class="section-kicker">04 // RADIOLOGICAL IMAGING &amp; SALIENCY</div>
            <h2 class="slide-title">ResNet-50 Thoracic Vision with <span>Grad-CAM Explainability</span></h2>
            <p class="slide-subtitle">
                Fine-tuned deep convolutional network delivering multi-label thoracic disease detection coupled with spatial attention heatmaps.
            </p>
            <div class="grid-split-45-55">
                <div style="display: flex; flex-direction: column; gap: 18px;">
                    <div class="glass-card">
                        <div class="card-num">MODEL ARCHITECTURE</div>
                        <div class="card-title">ResNet-50 Deep Transfer Learning</div>
                        <div class="card-text">
                            Trained across 25 epochs using AdamW (lr = 10<sup>-4</sup>) on 4,500 augmented chest X-rays covering 15 disease classes (Pneumonia, Cardiomegaly, Pneumothorax, Infiltration, etc.).
                        </div>
                    </div>
                    <div class="glass-card">
                        <div class="card-num">SPATIAL EXPLAINABILITY</div>
                        <div class="card-title">Grad-CAM Feature Localization</div>
                        <div class="card-text">
                            Gradients backpropagated to the final convolutional layer (<code style="color:#2DD4BF;">layer4.2.conv3</code>) generate pixel-level heatmaps, enabling clinicians to visually verify pathological lung opacities and cardiac borders.
                        </div>
                    </div>
                    <div class="glass-card">
                        <div class="card-num">CRITICAL METRIC</div>
                        <div class="card-text" style="display: flex; justify-content: space-between; align-items: center;">
                            <span>Macro mAP: <strong class="val-highlight">90.8%</strong></span>
                            <span>Top-3 Accuracy: <strong class="val-highlight">97.8%</strong></span>
                            <span>Validation Loss: <strong class="val-highlight">0.0562</strong></span>
                        </div>
                    </div>
                </div>
                <div class="image-frame">
                    <img src="./gradcam_vision_verification.png" alt="Vision &amp; Grad-CAM Interface">
                    <div class="image-caption">
                        <span><span class="caption-tag">LIVE UI:</span> ResNet-50 Chest Radiograph Classification &amp; Grad-CAM Attention</span>
                        <span>CONFIDENCE: HIGH</span>
                    </div>
                </div>
            </div>
        </div>
        <footer class="slide-footer">
            <div class="footer-left">Automatic priority emergency flags triggered on critical findings such as Pneumothorax and Tension Effusion.</div>
            <div class="footer-right">CHAPTER 4.2.3: MEDICAL VISION AGENT</div>
        </footer>
    </section>
    """,

    # SLIDE 6
    """
    <section class="slide" id="slide-6">
        <header class="slide-header">
            <div class="header-brand">
                <span class="brand-badge"><span class="brand-dot"></span>AEGISMED</span>
                <span class="header-category">NLP &amp; Tabular Specialists</span>
            </div>
            <div class="slide-number-tag">SLIDE 06 / 14</div>
        </header>
        <div class="slide-body">
            <div class="section-kicker">05 // CLINICAL ENTITY EXTRACTION &amp; BIOSTATISTICAL RISK</div>
            <h2 class="slide-title">BioBERT Clinical NLP &amp; <span>Gradient Boosting Risk Models</span></h2>
            <p class="slide-subtitle">
                Extracting structured clinical symptoms from unstructured notes and predicting chronic disease onset from physiological vitals.
            </p>
            <div class="grid-2col">
                <div class="glass-card highlight">
                    <div class="card-accent-top"></div>
                    <div class="card-num">SPECIALIST AGENT 02</div>
                    <div class="card-title">Clinical NLP Agent (BioBERT + NegEx)</div>
                    <div class="card-text" style="margin-bottom: 16px;">
                        Token-level Named Entity Recognition (NER) fine-tuned on 800 annotated clinical admission notes. Identifies symptoms, duration, anatomical location, and severity qualifiers.
                    </div>
                    <table class="spec-table">
                        <tr><td>Token Classification F1-Score</td><td class="val-highlight">0.872 (P: 0.884, R: 0.861)</td></tr>
                        <tr><td>Negation Detection (NegEx)</td><td class="val-highlight">94.5% Accuracy</td></tr>
                        <tr><td>Severity Stratification</td><td class="val-highlight">88.2% Accuracy</td></tr>
                        <tr><td>Latency per Admission Note</td><td class="val-highlight">1.45 s (CPU PyTorch)</td></tr>
                    </table>
                    <div class="card-badge" style="margin-top: 14px;">Discriminates "denies dyspnea" from active symptoms</div>
                </div>
                <div class="glass-card highlight">
                    <div class="card-accent-top"></div>
                    <div class="card-num">SPECIALIST AGENT 03</div>
                    <div class="card-title">Tabular Disease Predictor (GBDT)</div>
                    <div class="card-text" style="margin-bottom: 16px;">
                        Biostatistical risk scoring across 14 physiological biomarkers (BP, BMI, fasting glucose, lipid ratios, heart rate). Implemented with well-calibrated Gradient Boosting regressors.
                    </div>
                    <table class="spec-table">
                        <tr><td>Cardiovascular Event Risk</td><td class="val-highlight">ROC-AUC: 0.94 | Accuracy: 91.2%</td></tr>
                        <tr><td>Type-2 Diabetes / Metabolic</td><td class="val-highlight">ROC-AUC: 0.92 | Accuracy: 89.6%</td></tr>
                        <tr><td>Chronic Respiratory Risk</td><td class="val-highlight">ROC-AUC: 0.89 | Accuracy: 86.4%</td></tr>
                        <tr><td>Composite Wellness Index</td><td class="val-highlight">ROC-AUC: 0.95 | Accuracy: 92.0%</td></tr>
                    </table>
                    <div class="card-badge" style="margin-top: 14px;">Brier Score &le; 0.082 (High Probabilistic Calibration)</div>
                </div>
            </div>
        </div>
        <footer class="slide-footer">
            <div class="footer-left">Eliminates physician transcription burden while providing calibrated risk probabilities.</div>
            <div class="footer-right">CHAPTER 4.2.2 &amp; 4.2.5: NLP &amp; TABULAR AGENTS</div>
        </footer>
    </section>
    """,

    # SLIDE 7
    """
    <section class="slide" id="slide-7">
        <header class="slide-header">
            <div class="header-brand">
                <span class="brand-badge"><span class="brand-dot"></span>AEGISMED</span>
                <span class="header-category">Medical Knowledge Retrieval</span>
            </div>
            <div class="slide-number-tag">SLIDE 07 / 14</div>
        </header>
        <div class="slide-body">
            <div class="section-kicker">06 // KNOWLEDGE RETRIEVAL &amp; GUIDELINE GROUNDING</div>
            <h2 class="slide-title">Dense Vector RAG via <span>FAISS IndexFlatIP</span></h2>
            <p class="slide-subtitle">
                Grounding generative medical reasoning strictly in peer-reviewed clinical guidelines to prevent hallucinations.
            </p>
            <div class="grid-split-60-40">
                <div class="glass-card" style="padding: 24px;">
                    <div class="card-num">RETRIEVAL PIPELINE</div>
                    <div class="card-title" style="margin-bottom: 14px;">Clinical Guideline Embeddings &amp; Citation Anchoring</div>
                    <div class="card-text" style="margin-bottom: 18px;">
                        The RAG agent ingests 10 authoritative medical guidelines (WHO, ACC/AHA, GOLD COPD, ATS Community-Acquired Pneumonia, ADA Diabetes), chunked into semantic clinical passages embedded via <code style="color:#38BDF8;">sentence-transformers/all-MiniLM-L6-v2</code> (384-dimensional space).
                    </div>
                    <table class="spec-table">
                        <thead>
                            <tr>
                                <th>Benchmark Metric</th>
                                <th>Measured Result</th>
                                <th>Target Clinical Baseline</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Hit Rate @ Top-1</td>
                                <td class="val-highlight">78.0%</td>
                                <td>&gt; 70.0%</td>
                            </tr>
                            <tr>
                                <td>Hit Rate @ Top-5</td>
                                <td class="val-highlight">90.0%</td>
                                <td>&gt; 85.0%</td>
                            </tr>
                            <tr>
                                <td>Mean Reciprocal Rank (MRR)</td>
                                <td class="val-highlight">0.824</td>
                                <td>&gt; 0.750</td>
                            </tr>
                            <tr>
                                <td>FAISS Vector Query Latency</td>
                                <td class="val-highlight">1.8 ms</td>
                                <td>&lt; 10.0 ms (In-Memory CPU)</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div style="display: flex; flex-direction: column; gap: 20px;">
                    <div class="glass-card">
                        <div class="card-num">ZERO HALLUCINATION POLICY</div>
                        <div class="card-title">Strict Semantic Constraints</div>
                        <div class="card-text">
                            Any generative claim in the final diagnosis must cite an exact vector passage ID and guideline section. Unanchored claims are intercepted by the synthesis guardrail.
                        </div>
                    </div>
                    <div class="glass-card">
                        <div class="card-num">CORPUS COVERAGE</div>
                        <div class="card-title">Gold-Standard Clinical Sources</div>
                        <div class="card-text">
                            Curated guidelines encompass emergency triage protocols, antimicrobial stewardship rules, cardiovascular risk cutoffs, and diabetic staging criteria.
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <footer class="slide-footer">
            <div class="footer-left">Index maintained in src/agents/rag/agent.py with sub-millisecond similarity lookups.</div>
            <div class="footer-right">CHAPTER 4.2.4: RAG KNOWLEDGE AGENT</div>
        </footer>
    </section>
    """,

    # SLIDE 8
    """
    <section class="slide" id="slide-8">
        <header class="slide-header">
            <div class="header-brand">
                <span class="brand-badge"><span class="brand-dot"></span>AEGISMED</span>
                <span class="header-category">Algorithmic Innovation I</span>
            </div>
            <div class="slide-number-tag">SLIDE 08 / 14</div>
        </header>
        <div class="slide-body">
            <div class="section-kicker">07 // PATENTABLE ALGORITHMIC CONTRIBUTION (CLAIMS 1–6)</div>
            <h2 class="slide-title">DEMAT: <span>Dynamic Active Triage Engine</span></h2>
            <p class="slide-subtitle">
                Formulating patient clinical questioning as an information-theoretic optimization problem to minimize diagnostic entropy.
            </p>
            <div class="grid-split-45-55">
                <div style="display: flex; flex-direction: column; gap: 18px;">
                    <div class="glass-card">
                        <div class="card-num">INFORMATION GAIN FORMULATION</div>
                        <div class="card-title">Shannon Entropy Optimization</div>
                        <div class="card-text">
                            Diagnostic uncertainty is quantified as entropy over candidate diseases <em>D</em>:
                            <div style="font-family:'JetBrains Mono', monospace; font-size:15px; color:#2DD4BF; margin:10px 0; background:rgba(0,0,0,0.3); padding:8px 12px; border-radius:6px;">
                                H(D) = - &sum; P(d) log<sub>2</sub> P(d)
                            </div>
                            The engine chooses question <em>Q</em><sup>*</sup> maximizing expected information gain:
                            <div style="font-family:'JetBrains Mono', monospace; font-size:14px; color:#38BDF8; margin-top:6px; background:rgba(0,0,0,0.3); padding:8px 12px; border-radius:6px;">
                                Q* = argmax [ H(D) - E[H(D|Q)] ]
                            </div>
                        </div>
                    </div>
                    <div class="glass-card">
                        <div class="card-num">MEASURED PERFORMANCE</div>
                        <div class="card-title">Rapid Entropy Collapse</div>
                        <div class="card-text">
                            Reduces diagnostic entropy from <strong class="val-highlight">2.50 bits</strong> down to confident clinical diagnosis in just <strong class="val-highlight">2 to 3 targeted questions</strong>, minimizing patient questionnaire fatigue.
                        </div>
                    </div>
                </div>
                <div class="image-frame">
                    <img src="./demat_triage_screenshot.png" alt="DEMAT Active Triage UI">
                    <div class="image-caption">
                        <span><span class="caption-tag">PATENT UI:</span> DEMAT Entropy Reduction, Leading Differentials &amp; Targeted Questioning</span>
                        <span>ENTROPY: 2.50 BITS</span>
                    </div>
                </div>
            </div>
        </div>
        <footer class="slide-footer">
            <div class="footer-left">Filed in Patent Application Specification — Patent Claim Portfolio 1–6.</div>
            <div class="footer-right">PRD SECTION 3.1 &amp; PATENT SPECIFICATION</div>
        </footer>
    </section>
    """,

    # SLIDE 9
    """
    <section class="slide" id="slide-9">
        <header class="slide-header">
            <div class="header-brand">
                <span class="brand-badge"><span class="brand-dot"></span>AEGISMED</span>
                <span class="header-category">Algorithmic Innovation II</span>
            </div>
            <div class="slide-number-tag">SLIDE 09 / 14</div>
        </header>
        <div class="slide-body">
            <div class="section-kicker">08 // PATENTABLE SAFETY FRAMEWORK (CLAIMS 7–12)</div>
            <h2 class="slide-title">EN-SCAF: <span>Evidential Neuro-Symbolic Arbitration</span></h2>
            <p class="slide-subtitle">
                Resolving multimodal contradictions using Dempster-Shafer evidential theory and deterministic clinical red-line rules.
            </p>
            <div class="grid-3col">
                <div class="glass-card highlight">
                    <div class="card-accent-top"></div>
                    <div class="card-num">PILLAR 01</div>
                    <div class="card-title">Evidential Conflict Metric</div>
                    <div class="card-text">
                        Quantifies inter-modal conflict using Dempster's metric:
                        <div style="font-family:'JetBrains Mono', monospace; font-size:14px; color:#2DD4BF; margin:10px 0; background:rgba(0,0,0,0.3); padding:8px 10px; border-radius:6px;">
                            k = &sum; m<sub>1</sub>(A) &middot; m<sub>2</sub>(B) [A &cap; B = &empty;]
                        </div>
                        When X-ray is normal but patient exhibits chest pain on exertion, <em>k</em> &ge; 0.65 triggers multi-agent arbitration rather than averaging probabilities.
                    </div>
                    <div class="card-badge">Dempster-Shafer Theory</div>
                </div>
                <div class="glass-card highlight">
                    <div class="card-accent-top"></div>
                    <div class="card-num">PILLAR 02</div>
                    <div class="card-title">Deterministic Red-Lines</div>
                    <div class="card-text">
                        Critical clinical rules bypass LLM synthesis entirely:
                        <ul style="margin-top: 10px; margin-left: 20px; line-height: 1.6; font-size: 14px; color: #E2E8F0;">
                            <li>Chest pain + arm radiation &rarr; <span style="color:#F87171; font-weight:700;">Emergency Angina Flag</span></li>
                            <li>Pneumothorax finding &rarr; <span style="color:#F87171; font-weight:700;">Immediate Triage Alert</span></li>
                            <li>Severe asthma + stridor &rarr; <span style="color:#F87171; font-weight:700;">Stat Consultation</span></li>
                        </ul>
                    </div>
                    <div class="card-badge">&le; 12 ms Execution Guardrail</div>
                </div>
                <div class="glass-card highlight">
                    <div class="card-accent-top"></div>
                    <div class="card-num">PILLAR 03</div>
                    <div class="card-title">Deterministic Fallback</div>
                    <div class="card-text">
                        If cloud LLM endpoints experience latency spikes (&gt;30 s) or 503 gateway timeouts, the local CPU deterministic synthesis engine generates calibrated clinical reports in <strong class="val-highlight">15 ms</strong> with zero hallucination risk.
                    </div>
                    <div class="card-badge">100% Uptime Guarantee</div>
                </div>
            </div>
        </div>
        <footer class="slide-footer">
            <div class="footer-left">Enforces clinical safety by construction: implemented in src/agents/rule_based_synthesis.py</div>
            <div class="footer-right">PRD SECTION 3.2 &amp; PATENT SPECIFICATION</div>
        </footer>
    </section>
    """,

    # SLIDE 10
    """
    <section class="slide" id="slide-10">
        <header class="slide-header">
            <div class="header-brand">
                <span class="brand-badge"><span class="brand-dot"></span>AEGISMED</span>
                <span class="header-category">Full-Stack Implementation</span>
            </div>
            <div class="slide-number-tag">SLIDE 10 / 14</div>
        </header>
        <div class="slide-body">
            <div class="section-kicker">09 // SOFTWARE ENGINEERING &amp; CLINICAL PORTAL</div>
            <h2 class="slide-title">Accessible Clinical Interface: <span>Next.js 16 + FastAPI</span></h2>
            <p class="slide-subtitle">
                A modern healthcare portal engineered for hospital clinical specialists, emergency triage staff, and patients.
            </p>
            <div class="grid-split-45-55">
                <div style="display: flex; flex-direction: column; gap: 18px;">
                    <div class="glass-card">
                        <div class="card-num">FRONTEND ARCHITECTURE</div>
                        <div class="card-title">Next.js 16 (App Router) + React 19</div>
                        <div class="card-text">
                            Built with TypeScript, Tailwind CSS, and Framer Motion micro-interactions. Features full light/dark mode theming and mobile-responsive navigation.
                        </div>
                    </div>
                    <div class="glass-card">
                        <div class="card-num">ACCESSIBILITY DISCIPLINE</div>
                        <div class="card-title">WCAG 2.2 AA Compliance</div>
                        <div class="card-text">
                            Enforces &ge; 4.5:1 contrast ratios, keyboard-accessible tab stops, semantic ARIA live regions, and screen-reader clinical telemetry readouts.
                        </div>
                    </div>
                    <div class="glass-card">
                        <div class="card-num">BACKEND SERVICE STACK</div>
                        <div class="card-title">Asynchronous FastAPI Core</div>
                        <div class="card-text">
                            Pydantic v2 strict schemas, SQLite audit trails, WebSocket progress streaming, and production Docker containerization.
                        </div>
                    </div>
                </div>
                <div class="image-frame">
                    <img src="./localhost_3000_landing.png" alt="Clinical Landing Portal">
                    <div class="image-caption">
                        <span><span class="caption-tag">PRODUCTION PORTAL:</span> AegisMed Modular Landing Dashboard on Next.js 16</span>
                        <span>PORT: 3000 // LIVE</span>
                    </div>
                </div>
            </div>
        </div>
        <footer class="slide-footer">
            <div class="footer-left">Verified end-to-end on live host with passing automated accessibility audit.</div>
            <div class="footer-right">CHAPTER 4.5: USER INTERFACE &amp; ACCESSIBILITY</div>
        </footer>
    </section>
    """,

    # SLIDE 11
    """
    <section class="slide" id="slide-11">
        <header class="slide-header">
            <div class="header-brand">
                <span class="brand-badge"><span class="brand-dot"></span>AEGISMED</span>
                <span class="header-category">Clinical Synthesis &amp; Triage</span>
            </div>
            <div class="slide-number-tag">SLIDE 11 / 14</div>
        </header>
        <div class="slide-body">
            <div class="section-kicker">10 // MULTIMODAL SYNTHESIS &amp; REPORTING</div>
            <h2 class="slide-title">Actionable Triage &amp; <span>Dual-Persona Output</span></h2>
            <p class="slide-subtitle">
                Translating complex multimodal inferences into calibrated, role-tailored clinical guidance and standardized EHR records.
            </p>
            <div class="grid-split-45-55">
                <div style="display: flex; flex-direction: column; gap: 18px;">
                    <div class="glass-card">
                        <div class="card-num">DUAL-PERSONA ENGINE</div>
                        <div class="card-title">Clinician vs. Patient Synthesis</div>
                        <div class="card-text">
                            <strong style="color:#F8FAFC;">Clinician Mode:</strong> Differential diagnosis rankings, likelihood ratios, biometric indices, and medical guideline citations.<br><br>
                            <strong style="color:#F8FAFC;">Patient Mode:</strong> Empathetic, clear plain-language explanation, immediate emergency action steps, and self-care boundaries.
                        </div>
                    </div>
                    <div class="glass-card">
                        <div class="card-num">EHR INTEROPERABILITY</div>
                        <div class="card-title">HL7 FHIR R4 Bundle Export</div>
                        <div class="card-text">
                            Generates valid FHIR resources: <code style="color:#2DD4BF;">DiagnosticReport</code>, <code style="color:#2DD4BF;">RiskAssessment</code>, and <code style="color:#2DD4BF;">Observation</code> for seamless hospital EHR integration.
                        </div>
                    </div>
                    <div class="glass-card">
                        <div class="card-num">DOCUMENT SUBSYSTEM</div>
                        <div class="card-title">Formatted Clinical Exports</div>
                        <div class="card-text">
                            Server-side ReportLab PDF generator produces downloadable hospital-ready clinical summary sheets and CSV audit logs.
                        </div>
                    </div>
                </div>
                <div class="image-frame">
                    <img src="./diagnosis_refined_verification.png" alt="Clinical Synthesis Output">
                    <div class="image-caption">
                        <span><span class="caption-tag">SYNTHESIZED DIAGNOSIS:</span> Community-Acquired Pneumonia with Exertion Warning</span>
                        <span>SEVERITY: MODERATE</span>
                    </div>
                </div>
            </div>
        </div>
        <footer class="slide-footer">
            <div class="footer-left">Dual-persona toggle allows instantaneous switching between clinical and layperson formats.</div>
            <div class="footer-right">CHAPTER 4.2.7: SYNTHESIS AGENT</div>
        </footer>
    </section>
    """,

    # SLIDE 12
    """
    <section class="slide" id="slide-12">
        <header class="slide-header">
            <div class="header-brand">
                <span class="brand-badge"><span class="brand-dot"></span>AEGISMED</span>
                <span class="header-category">Conversational Assistant</span>
            </div>
            <div class="slide-number-tag">SLIDE 12 / 14</div>
        </header>
        <div class="slide-body">
            <div class="section-kicker">11 // INTERACTIVE MEDICAL ASSISTANT</div>
            <h2 class="slide-title">Evidence-Anchored <span>Clinical Assistant</span></h2>
            <p class="slide-subtitle">
                Natural-language clinical dialogue grounded in verified patient diagnostic state and peer-reviewed literature.
            </p>
            <div class="grid-split-45-55">
                <div style="display: flex; flex-direction: column; gap: 18px;">
                    <div class="glass-card">
                        <div class="card-num">CONVERSATIONAL MEMORY</div>
                        <div class="card-title">Multi-Turn Context Persistence</div>
                        <div class="card-text">
                            Maintains patient consultation state across dialogue turns without suffering from ungrounded symptom hallucinations or persona drift.
                        </div>
                    </div>
                    <div class="glass-card">
                        <div class="card-num">CLINICAL SAFETY PERIMETER</div>
                        <div class="card-title">Grounded Advice Boundaries</div>
                        <div class="card-text">
                            Enforces clear diagnostic disclaimers, highlights life-threatening warning signs, and refuses unsupervised drug prescription or dangerous off-label dosing.
                        </div>
                    </div>
                    <div class="glass-card">
                        <div class="card-num">ASSISTANT METRICS</div>
                        <div class="card-title">Sub-Second Semantic Retrieval</div>
                        <div class="card-text">
                            Incoming clinical questions are embedded and matched against FAISS in <strong class="val-highlight">2.1 ms</strong>, feeding verified context chunks directly into the LLM prompt.
                        </div>
                    </div>
                </div>
                <div class="image-frame">
                    <img src="./chat_assistant_verification.png" alt="Clinical Assistant Chat Interface">
                    <div class="image-caption">
                        <span><span class="caption-tag">ASSISTANT UI:</span> Evidence-Anchored Interactive Dialogue with Safety Footers</span>
                        <span>RAG RETRIEVAL: ACTIVE</span>
                    </div>
                </div>
            </div>
        </div>
        <footer class="slide-footer">
            <div class="footer-left">User feedback loop with thumbs up/down audit logging and one-click copy actions.</div>
            <div class="footer-right">FRONTEND /CHAT &amp; SRC/API/ROUTES/CHAT.PY</div>
        </footer>
    </section>
    """,

    # SLIDE 13
    """
    <section class="slide" id="slide-13">
        <header class="slide-header">
            <div class="header-brand">
                <span class="brand-badge"><span class="brand-dot"></span>AEGISMED</span>
                <span class="header-category">Empirical Results</span>
            </div>
            <div class="slide-number-tag">SLIDE 13 / 14</div>
        </header>
        <div class="slide-body">
            <div class="section-kicker">12 // BENCHMARKS &amp; EXPERIMENTAL VALIDATION</div>
            <h2 class="slide-title">Comprehensive <span>Empirical Benchmarks</span></h2>
            <p class="slide-subtitle">
                Quantitative verification across component accuracy, real-world case simulations, and software quality tests.
            </p>
            <div class="grid-split-60-40">
                <div class="glass-card" style="padding: 22px;">
                    <div class="card-num">TABLE 5.1 // COMPONENT BENCHMARKS</div>
                    <table class="spec-table">
                        <thead>
                            <tr>
                                <th>Subsystem / Agent</th>
                                <th>Primary Metric</th>
                                <th>Result</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>ResNet-50 Vision Agent</td>
                                <td>Macro F1 / AUROC</td>
                                <td class="val-highlight">0.901 / 0.945</td>
                                <td><span style="color:#2DD4BF;">&check; Exceeded</span></td>
                            </tr>
                            <tr>
                                <td>BioBERT NLP Agent</td>
                                <td>Token NER F1</td>
                                <td class="val-highlight">0.872 (94.5% NegEx)</td>
                                <td><span style="color:#2DD4BF;">&check; Exceeded</span></td>
                            </tr>
                            <tr>
                                <td>FAISS RAG Engine</td>
                                <td>Top-5 Hit Rate / MRR</td>
                                <td class="val-highlight">90.0% / 0.824</td>
                                <td><span style="color:#2DD4BF;">&check; Exceeded</span></td>
                            </tr>
                            <tr>
                                <td>Cardiovascular GBDT</td>
                                <td>ROC-AUC / Accuracy</td>
                                <td class="val-highlight">0.94 / 91.2%</td>
                                <td><span style="color:#2DD4BF;">&check; Exceeded</span></td>
                            </tr>
                            <tr>
                                <td>Composite Wellness</td>
                                <td>ROC-AUC / Accuracy</td>
                                <td class="val-highlight">0.95 / 92.0%</td>
                                <td><span style="color:#2DD4BF;">&check; Exceeded</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div style="display: flex; flex-direction: column; gap: 18px;">
                    <div class="glass-card">
                        <div class="card-num">CLINICAL CASE VALIDATION</div>
                        <div class="card-title">100% Diagnostic Concordance</div>
                        <div class="card-text" style="font-size: 14px; line-height: 1.6;">
                            Tested across 5 standardized clinical patient profiles (Acute Angina, Bacterial Pneumonia, Type 2 Diabetes, Migraine with Aura, Upper Respiratory Viral). All 5 cases achieved <strong class="val-highlight">100% concordance</strong> with physician gold-standard consensus.
                        </div>
                    </div>
                    <div class="glass-card">
                        <div class="card-num">SOFTWARE ENGINEERING RIGOR</div>
                        <div class="card-title">Automated Pytest Suite</div>
                        <div class="card-text" style="font-size: 14px; line-height: 1.6;">
                            <strong class="val-highlight">92 automated test cases</strong> covering API schemas, boundary conditions, Dempster-Shafer arbitration, and report serialization.
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <footer class="slide-footer">
            <div class="footer-left">End-to-end demo mode latency: &lt; 50 ms | Local deterministic fallback: 15 ms.</div>
            <div class="footer-right">CHAPTER 5: RESULTS AND DISCUSSION</div>
        </footer>
    </section>
    """,

    # SLIDE 14
    """
    <section class="slide" id="slide-14">
        <header class="slide-header">
            <div class="header-brand">
                <span class="brand-badge"><span class="brand-dot"></span>AEGISMED</span>
                <span class="header-category">Conclusion &amp; Future Scope</span>
            </div>
            <div class="slide-number-tag">SLIDE 14 / 14</div>
        </header>
        <div class="slide-body">
            <div class="section-kicker">13 // VIVA VOCE DEFENSE &amp; FUTURE DIRECTIONS</div>
            <h2 class="slide-title">Conclusion &amp; <span>Academic Defensibility</span></h2>
            <p class="slide-subtitle">
                Summary of key deliverables, patent package, and roadmap for clinical deployment.
            </p>
            <div class="grid-3col">
                <div class="glass-card highlight">
                    <div class="card-accent-top"></div>
                    <div class="card-num">DELIVERABLE 01</div>
                    <div class="card-title">Production CDSS Artifact</div>
                    <div class="card-text">
                        A fully integrated, verified multi-agent software platform (Next.js 16 + FastAPI) uniting Computer Vision, Clinical NLP, Guideline RAG, and Biostatistical Risk with sub-second responsiveness.
                    </div>
                    <div class="card-badge">Full-Stack Implementation</div>
                </div>
                <div class="glass-card highlight">
                    <div class="card-accent-top"></div>
                    <div class="card-num">DELIVERABLE 02</div>
                    <div class="card-title">Intellectual Property &amp; Paper</div>
                    <div class="card-text">
                        Comprehensive 12-claim patent application package prepared for DEMAT entropy reduction and EN-SCAF conflict arbitration, accompanied by an 8-page CHIL conference manuscript.
                    </div>
                    <div class="card-badge">12-Claim Patent Package</div>
                </div>
                <div class="glass-card highlight">
                    <div class="card-accent-top"></div>
                    <div class="card-num">DELIVERABLE 03</div>
                    <div class="card-title">Future Research Scope</div>
                    <div class="card-text">
                        1. Federated Multi-Hospital Learning for privacy-preserving clinical weights.<br>
                        2. 3D Volumetric CT and MRI imaging agent expansion.<br>
                        3. Prospective multi-center clinical trials under formal IRB ethics approval.
                    </div>
                    <div class="card-badge">Future Horizons</div>
                </div>
            </div>
        </div>
        <footer class="slide-footer">
            <div class="footer-left">Thank you to the Faculty Advisor, Evaluation Committee, and Examiners. Questions are welcomed.</div>
            <div class="footer-right">AEGISMED // CANDIDATE: ARHAM SAGHIR</div>
        </footer>
    </section>
    """
]
