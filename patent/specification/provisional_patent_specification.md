# PROVISIONAL PATENT APPLICATION SPECIFICATION

**NOTICE:** *THIS IS A DRAFT TECHNICAL SPECIFICATION PREPARED FOR REVIEW AND REVISION BY A REGISTERED PATENT ATTORNEY OR PATENT AGENT. IT DOES NOT CONSTITUTE FORMAL LEGAL ADVICE OR A FILED APPLICATION. FORMAL LEGAL OPINION AND FILING IN THE TARGET JURISDICTION (E.G., USPTO, IPO, PCT) MUST BE CONDUCTED BY LICENSED PATENT PRACTITIONERS.*

---

## TITLE OF THE INVENTION
**SYSTEM AND METHOD FOR DYNAMIC ENTROPY-MINIMIZING ACTIVE CLINICAL TRIAGE AND EVIDENTIAL MULTI-AGENT DIAGNOSTIC CONFLICT ARBITRATION**

---

## INVENTORS
- Arham Saghir
- Team AegisMed Contributors

---

## CROSS-REFERENCE TO RELATED APPLICATIONS
This application claims the benefit of and priority to prior technical disclosures and prototypes developed under the AegisMed Clinical Decision Support System research initiative.

---

## TECHNICAL FIELD
The present invention relates generally to artificial intelligence, information theory, and clinical decision support systems (CDSS). More particularly, the invention relates to computer-implemented methods, non-transitory computer-readable media, and system architectures for active, adaptive clinical triage using information-theoretic Shannon entropy minimization, evidential neuro-symbolic multi-agent conflict arbitration via Dempster-Shafer theory, ontological knowledge graph constraint validation, and distribution-free conformal risk bounding.

---

## BACKGROUND OF THE INVENTION
Diagnostic errors represent one of the most critical challenges in modern healthcare, contributing to substantial preventable morbidity, prolonged hospitalizations, and escalated healthcare costs worldwide. In acute settings, emergency department triage physicians face overwhelming cognitive workloads, compressed decision windows, and fragmented multimodal data encompassing free-text clinical notes, physiological telemetry, radiological images, and laboratory assays.

Recent advances in artificial intelligence have produced deep neural networks and Large Language Models (LLMs) capable of extracting clinical named entities and generating medical summaries. However, deploying conventional AI models in high-stakes clinical decision support is fundamentally compromised by three critical technological failure modes:

1. **Passive One-Shot Ingestion and High Diagnostic Ambiguity:** Conventional AI systems operate on passive, static single-turn prompts. When presented with ambiguous, incomplete, or overlapping symptom presentations (for example, acute retrosternal chest pain that could indicate ischemic coronary artery disease, gastroesophageal reflux, or acute pneumonia), static systems either guess prematurely or output broad, non-actionable lists. Existing systems lack an active, information-theoretically guided questioning loop capable of sequentially acquiring the most discriminative missing clinical observations to mathematically collapse diagnostic entropy.
2. **Uncalibrated Multimodal Disagreements and Hallucinatory Drift:** Real-world diagnostic data is inherently multimodal. In a clinical consultation, a computer vision model evaluating a chest radiograph may detect subtle basilar opacities indicating pneumonia, while a natural language processing model evaluating a patient's chief complaint of epigastric burning may suggest gastroesophageal reflux disease. Conventional multimodal ensembles rely on unweighted majority voting, linear score averaging, or end-to-end black-box transformers. When specialized agents produce conflicting inferences, these conventional approaches obscure the disagreement, resulting in ungrounded generative summaries or dangerous false consensus. Furthermore, conventional LLMs generate syntactically fluent but biologically impossible diagnostic combinations without formal ontological grounding.
3. **Absence of Frequentist Risk Bounding and Uncertainty Quantification:** Conventional deep learning models produce uncalibrated softmax scores that convey a false sense of certainty. In clinical medicine, a point prediction accompanied by a 92% softmax probability may fail to reflect out-of-distribution uncertainty or underlying ambiguity. Current systems lack a mathematically rigorous, distribution-free statistical guarantee that bounds the probability of excluding the true underlying pathology.

Consequently, there exists an acute, unmet need in the art for an intelligent, mathematically grounded clinical decision support architecture that actively interrogates diagnostic presentations to minimize Shannon entropy, quantifies and arbitrates multimodal agent disagreements using evidential reasoning and ontological knowledge graphs, and provides provable frequentist risk-controlled coverage over diagnostic differentials.

---

## SUMMARY OF THE INVENTION
The present invention addresses the foregoing technical deficiencies by providing an integrated, multimodal Clinical Decision Support System (CDSS) termed **AegisMed**. The system incorporates four interconnected, patentable inventive frameworks:

1. **Dynamic Entropy-Minimizing Active Triage (DEMAT):** An information-theoretic algorithmic engine that models the diagnostic state as a categorical probability distribution over a comprehensive clinical condition universe. DEMAT calculates the exact Shannon diagnostic entropy $H(D)$ of the differential. When entropy exceeds a convergence threshold, DEMAT evaluates a repository of candidate clinical inquiries and computes the Expected Mutual Information Gain $I(D; A_q)$ for each inquiry. DEMAT automatically selects and presents the query $q^* = \arg\max I(D; A_q)$ that yields the maximal expected collapse in diagnostic ambiguity, receives the observation, performs a Bayesian belief update, and halts upon achieving high-certainty convergence.
2. **Evidential Neuro-Symbolic Conflict Arbitration Framework (EN-SCAF):** A multi-agent consensus architecture that models specialist inferences (e.g., Computer Vision saliency tensors, Clinical NLP extracted findings, Biostatistical risk scores) as independent Dempster-Shafer belief mass assignments over a power set of medical hypotheses. EN-SCAF explicitly computes a cross-modal orthogonal conflict parameter $K$. When $K$ exceeds an empirically determined conflict threshold ($K > 0.40$), indicating severe inter-agent discordance, EN-SCAF invokes a neuro-symbolic knowledge graph gate.
3. **Ontological Knowledge Graph Pruning Gate:** A symbolic validation layer that projects disputed hypotheses onto directed acyclic graph (DAG) ontological paths of biomedical ontologies (e.g., UMLS Metathesaurus, SNOMED-CT, ICD-10). The pruning gate enforces hard biological axioms (e.g., verifying that acute unilateral pulmonary consolidation cannot be causally explained by uncomplicated peptic ulcer disease), eliminating biologically implausible hypotheses prior to generative synthesis. Concordant masses are combined using Dempster's rule of combination to produce an evidential consensus differential.
4. **Multimodal Conformal Risk-Controlled Synthesis (MCRC-DS):** A post-hoc distribution-free calibration layer that maps evidential consensus outputs to dynamically sized prediction sets $\mathcal{C}(\mathbf{x})$. Using non-conformity scores calibrated over held-out patient cohorts, MCRC-DS guarantees with provable finite-sample validity that the true diagnosis is contained within the output set with probability at least $1 - \alpha$ (e.g., 95% formal statistical coverage guarantee).

In empirical evaluation across 200 standardized clinical presentation cases, DEMAT achieved a **98.0% Top-1 diagnostic accuracy** (compared to 93.0% for single-pass ablation, $p = 0.0339$), **100.0% Top-3 differential coverage**, and an average **53.7% collapse in Shannon diagnostic entropy** (from 2.846 bits to 1.318 bits) within an average of only **1.92 inquiries per session** and an inference latency of **0.2 milliseconds**.

---

## BRIEF DESCRIPTION OF THE DRAWINGS
The accompanying drawings, which are incorporated in and constitute a part of this specification, illustrate embodiments of the invention and, together with the description, serve to explain the technical principles of the invention.

- **FIG. 1** is a high-level system architecture and network topology diagram illustrating the client computing device, edge API gateway, DEMAT engine, central multi-agent orchestrator, specialist agents, evidential conflict arbiter (EN-SCAF), conformal bounding layer, and dual-persona interface generator, according to an embodiment of the present invention.
- **FIG. 2** is a detailed algorithmic flowchart depicting the Dynamic Entropy-Minimizing Active Triage (DEMAT) state progression, illustrating prior belief construction, Shannon entropy calculation, mutual information gain maximization, adaptive inquiry selection, and Bayesian posterior updating.
- **FIG. 3** is an architectural block diagram and flow diagram illustrating the Evidential Neuro-Symbolic Conflict Arbitration Framework (EN-SCAF), including Dempster-Shafer belief mass assignment, conflict parameter $K$ computation, and the UMLS ontological DAG pruning gate.
- **FIG. 4** is a schematic diagram illustrating the Multimodal Conformal Risk-Controlled Synthesis framework, showing offline calibration quantile estimation, online non-conformity evaluation, and dynamically sized set inclusion with $1 - \alpha$ coverage guarantees.
- **FIG. 5** is a dual-panel composite diagram comprising Panel A illustrating a real-world multi-agent execution stepper trace across specialist nodes and Grad-CAM saliency heatmaps, and Panel B illustrating empirical experimental evidence including the Shannon entropy collapse curve and calibration reliability comparison.

---

## DETAILED DESCRIPTION OF THE PREFERRED EMBODIMENTS

### 1. Overall System Architecture (FIG. 1)
Referring to **FIG. 1**, the overall multimodal clinical decision support system **100** comprises a client computing device **102** communicatively coupled to an API edge gateway and router **106** over a secure communication network. The client device **102** may comprise a clinician workstation, hospital terminal, or mobile device presenting a responsive graphical interface.

A patient presentation **104** is submitted via the client device **102**, encompassing one or more multimodal data streams: unstructured clinical narrative text (e.g., chief complaint, history of present illness), medical imaging files (e.g., DICOM, PNG, or JPEG chest radiographs), physiological vitals and biometric telemetry (e.g., blood pressure, heart rate, oxygen saturation, BMI, age, gender), and optional acoustic voice transcripts.

The API edge gateway **106** receives the presentation payload, validates schema structures, and routes the clinical text and vitals to the **Dynamic Entropy-Minimizing Active Triage (DEMAT) Engine 108**. The DEMAT Engine **108** establishes a baseline categorical probability distribution over a predefined clinical disease database and coordinates adaptive clarification cycles before or in parallel with deep specialist invocation.

Upon triage convergence, the session state is dispatched to the **Central Multi-Agent Task Orchestrator 110**. In a preferred embodiment, the orchestrator **110** is implemented using a cyclic directed graph runtime (e.g., LangGraph `StateGraph`) managing parallel execution threads across domain-specific specialist agents:
- **Clinical NLP Specialist Agent 112:** Utilizes a domain-adapted language model (e.g., BioBERT, ClinicalBERT) fine-tuned on clinical named entity recognition (NER) to extract standardized symptom tokens, anatomical locations, severity modifiers, and temporal onset attributes.
- **Medical Computer Vision Specialist Agent 114:** Utilizes a deep convolutional neural network or vision transformer (e.g., ResNet-50 pre-trained on NIH ChestX-ray14) to classify pathological radiographic findings and generates spatial explanation heatmaps using a Gradient-Weighted Class Activation Mapping (Grad-CAM) hook on the final convolutional layer.
- **Biostatistical Predictive Risk Agent 116:** Utilizes gradient-boosted decision trees (e.g., XGBoost, LightGBM) calibrated on longitudinal clinical cohorts to evaluate multi-organ risk profiles and disease-specific susceptibility indices.
- **Clinical Guideline RAG Agent 118:** Utilizes dense semantic vector embeddings (e.g., sentence-transformers) indexed in a FAISS vector database containing 500+ verified clinical practice guidelines (e.g., ACC/AHA, GOLD, IDSA) to retrieve grounded evidence citations.

The outputs from specialist agents **112**, **114**, **116**, and **118** are aggregated and fed into the **Evidential Neuro-Symbolic Arbiter (EN-SCAF) 120**. EN-SCAF **120** reconciles multimodal disagreements, filters biologically inconsistent hypotheses via ontological constraints, and passes the consensus to the **Multimodal Conformal Risk-Controlled Synthesis Layer 122** for uncertainty bounding. Final outputs are formatted by the **Dual-Persona Interface Generator 124**, producing tailored technical views for clinicians and plain-language summaries for patients, and persisted in database **126**.

---

### 2. Dynamic Entropy-Minimizing Active Triage (DEMAT) Engine (FIG. 2)
Referring to **FIG. 2**, the Dynamic Entropy-Minimizing Active Triage engine executes an iterative, information-theoretically bounded interrogation method **200**.

#### 2.1. Prior Belief Formulation (202)
Upon receiving the presentation, the engine initializes a categorical prior belief distribution $P(D)$ over a disease universe $\Theta = \{d_1, d_2, \dots, d_N\}$ comprising $N$ distinct clinical conditions (e.g., $N=15$ conditions spanning cardiovascular, respiratory, gastrointestinal, neurological, endocrine, dermatological, and musculoskeletal pathologies):
$$P(d_i) = \frac{S(d_i)}{\sum_{j=1}^N S(d_j)}$$
where $S(d_i) = s_0 + \sum_{w \in \mathbf{x}} \mathbb{I}(w \in \text{Symptoms}(d_i)) \cdot \omega_w + \text{VitalsScore}(d_i, \text{vitals})$, where $s_0$ is a uniform prior smoothing parameter (e.g., $0.10$), and $\omega_w$ represents clinical symptom specificity weights.

#### 2.2. Shannon Diagnostic Entropy Quantification (204)
The engine quantifies total diagnostic ambiguity in the current differential by evaluating the Shannon diagnostic entropy $H(D)$ in bits:
$$H(D) = -\sum_{i=1}^N P(d_i) \log_2 P(d_i)$$
When belief is completely dispersed (maximal uncertainty), $H(D) = \log_2(N)$ bits. When diagnosis is fully determined, $H(D) = 0.0$ bits.

#### 2.3. Convergence Gate & Stopping Criteria (206)
The engine evaluates whether the diagnostic state has converged:
$$\text{Converged} \iff H(D) \le \epsilon_{\text{triage}} \quad \text{OR} \quad t \ge t_{\max}$$
In a preferred embodiment, $\epsilon_{\text{triage}} = 0.45\text{ bits}$ (representing high confidence concentrated in 1–2 conditions), and $t_{\max} = 3$ rounds, enforcing a strict boundary against patient cognitive fatigue. If converged (**208**), the engine outputs the focused differential to the orchestrator **110**.

#### 2.4. Mutual Information Gain Optimization (210, 212)
If $H(D) > \epsilon_{\text{triage}}$, the engine queries a clinical question bank comprising candidate inquiries $Q = \{q_1, q_2, \dots, q_M\}$, each inquiry $q$ having discrete observable outcomes $A_q = \{a_1, \dots, a_k\}$ and calibrated likelihood tables $P(A_q = a \mid d_i)$.

For each unasked inquiry $q \notin \text{Asked}$, the engine computes the Expected Mutual Information Gain $I(D; A_q)$:
$$I(D; A_q) = H(D) - \mathbb{E}_{a \sim A_q}[H(D \mid A_q = a)] = H(D) - \sum_{a \in A_q} P(A_q = a) H(D \mid A_q = a)$$
where the marginal outcome probability is:
$$P(A_q = a) = \sum_{i=1}^N P(A_q = a \mid d_i) P(d_i)$$
and the conditional posterior entropy is calculated over the Bayesian posterior:
$$P(d_i \mid A_q = a) = \frac{P(A_q = a \mid d_i) P(d_i)}{P(A_q = a)}$$
The engine selects the optimal question **212**:
$$q^* = \arg\max_{q \in Q \setminus \text{Asked}} I(D; A_q)$$
If $\max_q I(D; A_q) < \delta_{\min}$ (e.g., $0.02\text{ bits}$), interrogation halts early due to marginal utility exhaustion.

#### 2.5. Patient Response & Bayesian Belief Update (214, 216)
The selected question $q^*$ is presented to the user **214**. Upon observing response $a^* \in A_{q^*}$, the engine performs the Bayesian belief update **216**:
$$P_{t+1}(d_i) = \frac{P(A_{q^*} = a^* \mid d_i) P_t(d_i)}{\sum_{j=1}^N P(A_{q^*} = a^* \mid d_j) P_t(d_j)}$$
The engine recomputes $H_{t+1}(D)$ and loops back to convergence check **206**.

---

### 3. Evidential Neuro-Symbolic Conflict Arbitration Framework (EN-SCAF) (FIG. 3)
Referring to **FIG. 3**, EN-SCAF **300** arbitrates conflicting outputs from multimodal agents.

#### 3.1. Dempster-Shafer Belief Mass Assignment (302, 304, 306)
Each agent $k \in \{\text{vision}, \text{nlp}, \text{risk}\}$ maps its internal score vector to a basic belief assignment (mass function) $m_k: 2^\Theta \to [0, 1]$ satisfying:
$$m_k(\emptyset) = 0 \quad \text{and} \quad \sum_{A \subseteq \Theta} m_k(A) = 1$$
Mass allocated to composite sets represents epistemic uncommitted uncertainty.

#### 3.2. Orthogonal Conflict Parameter ($K$) Calculation (308)
The cross-modal disagreement between distinct agent modalities (e.g., Vision mass $m_{\text{vis}}$ and NLP mass $m_{\text{nlp}}$) is quantified via the orthogonal conflict parameter $K$:
$$K = \sum_{B \cap C = \emptyset} m_{\text{vis}}(B) \cdot m_{\text{nlp}}(C)$$
$K = 0$ indicates perfect agreement; $K \to 1$ indicates total contradiction.

#### 3.3. Decision Threshold & UMLS Ontological DAG Pruning Gate (310, 312)
If $K \le 0.40$, evidence is deemed concordant and combined directly via Dempster's rule **320**.
If $K > 0.40$ (**310**), the engine halts automatic fusion and passes candidate hypotheses to the **UMLS Ontological DAG Pruning Gate 312**.

The pruning gate traverses the Unified Medical Language System (UMLS) Metathesaurus and SNOMED-CT directed acyclic graphs. The gate evaluates hard biological axioms and ontological consistency:
1. **Etiological Incompatibility:** For a patient with isolated radiographic basilar consolidation and acute dyspnea, candidate hypotheses asserting isolated gastrointestinal conditions (e.g., uncomplicated GERD) as the primary explanation for pulmonary opacification are pruned due to null path connectivity in the pulmonary pathology sub-graph.
2. **Co-Occurrence Verification:** Multi-label differential pairs $(d_i, d_j)$ are checked against clinical co-occurrence matrices. Pairs violating physiological plausibility are pruned.

#### 3.4. Dempster Combination Rule (320, 322)
After pruning inconsistent candidate hypotheses, remaining concordant evidence masses are fused via Dempster's orthogonal rule of combination:
$$m_{1 \oplus 2}(A) = \frac{1}{1 - K} \sum_{B \cap C = A} m_1(B) \cdot m_2(C) \quad \text{for } A \neq \emptyset$$
The fused masses are transformed into the pignistic probability distribution $\text{BetP}(d_i) = \sum_{d_i \in A} \frac{m(A)}{|A|}$, yielding the unified consensus differential **322**.

---

### 4. Multimodal Conformal Risk-Controlled Synthesis (FIG. 4)
Referring to **FIG. 4**, the conformal synthesis layer **400** provides distribution-free, finite-sample statistical safety bounds.

#### 4.1. Non-Conformity Scoring (404)
Given a calibration dataset $\mathcal{D}_{\text{cal}} = \{(\mathbf{x}_i, y_i)\}_{i=1}^n$ of $n$ held-out patient cases independent of model training, the non-conformity scoring engine evaluates how unusual true label $y_i$ is relative to the model's predicted probability $\hat{P}(y \mid \mathbf{x}_i)$:
$$S(\mathbf{x}_i, y_i) = 1 - \hat{P}(y_i \mid \mathbf{x}_i)$$

#### 4.2. Conformal Quantile Estimation (406)
Given a user-defined error budget $\alpha \in (0, 1)$ (e.g., $\alpha = 0.05$ for 95% confidence coverage), the calibrated conformal cutoff quantile $\hat{q}$ is calculated with finite-sample adjustment:
$$\hat{q} = \text{Quantile}_{\frac{\lceil (n + 1)(1 - \alpha) \rceil}{n}}\left( \{S(\mathbf{x}_i, y_i)\}_{i=1}^n \right)$$

#### 4.3. Dynamic Prediction Set Inclusion (410, 412)
At inference time for a new patient query $\mathbf{x}_{\text{new}}$, the engine computes non-conformity scores for all candidate conditions in $\Theta$ and constructs the dynamically sized prediction set:
$$\mathcal{C}(\mathbf{x}_{\text{new}}) = \{y \in \Theta : S(\mathbf{x}_{\text{new}}, y) \le \hat{q}\} = \{y \in \Theta : \hat{P}(y \mid \mathbf{x}_{\text{new}}) \ge 1 - \hat{q}\}$$
By the exchangeability of calibration and test distributions, the set $\mathcal{C}(\mathbf{x}_{\text{new}})$ guarantees:
$$\mathbb{P}\left(Y_{\text{true}} \in \mathcal{C}(\mathbf{x}_{\text{new}})\right) \ge 1 - \alpha$$
When presentation evidence is decisive, $|\mathcal{C}(\mathbf{x}_{\text{new}})| = 1$ (a single definitive diagnosis). When presentation evidence is ambiguous, $|\mathcal{C}|$ automatically expands to contain all plausible candidates, preventing premature exclusion of true pathology. If $|\mathcal{C}| \ge N_{\text{alert}}$, an automated clinician alert is triggered (**414**).

---

### 5. Empirical Experimental Evidence & Benchmark Results (FIG. 5)
Referring to **FIG. 5**, the system was evaluated on a comprehensive benchmark of $N = 200$ standardized clinical presentation cases across 15 diseases:

#### 5.1. Benchmark Evaluation Table
The table below documents the empirical comparison between **Arm 1 (Full DEMAT Adaptive Triage)** and **Arm 2 (Single-Pass Ablation Baseline)**:

| Metric | Arm 1: Full DEMAT Triage | Arm 2: Single-Pass Baseline | Delta (DEMAT vs. Baseline) | Statistical Significance |
| :--- | :---: | :---: | :---: | :---: |
| **Top-1 Diagnostic Accuracy** | **98.0%** (196/200) | 93.0% (186/200) | **+5.0%** | **$p = 0.0339$** ($\chi^2 = 4.5$) |
| **Top-3 Differential Coverage** | **100.0%** (200/200) | 97.5% (195/200) | **+2.5%** | — |
| **Top-5 Differential Coverage** | **100.0%** (200/200) | 100.0% (200/200) | +0.0% | — |
| **Shannon Diagnostic Entropy ($H$)** | **1.318 bits** | 2.846 bits | **-1.529 bits (-53.7%)** | — |
| **Brier Calibration Score (lower=better)** | **0.2005** | 0.5296 | **-0.3291 (-62.1%)** | — |
| **Expected Calibration Error (ECE)** | **0.2451** | 0.5528 | **-0.3077 (-55.7%)** | — |
| **Mean Questions Asked** | **1.92 questions** | 0.00 | +1.92 inquiries | — |
| **Mean Inference Latency** | **0.2 ms** | 0.1 ms | +0.1 ms | — |

#### 5.2. Clinical Differentiation Analysis
- **Cardiovascular Disease vs. Angina/GERD:** Under single-pass baseline, cardiovascular accuracy was only 42.9% due to symptomatic overlap with acid reflux and musculoskeletal chest discomfort. DEMAT active questioning achieved **100.0% accuracy** (+57.1% gain) by identifying physical exertion triggers and positional dependencies.
- **Pneumonia vs. Bronchitis/Asthma:** Baseline accuracy of 57.1% improved to **100.0% in DEMAT** (+42.9% gain) by dynamically interrogating sputum characteristics and focal wheezing.
- **Entropy Collapse Curve (516):** As shown in FIG. 5 Panel B, mean entropy drops precipitously from $2.846\text{ bits}$ at $t=0$, to $1.952\text{ bits}$ at $t=1$, to $1.318\text{ bits}$ at $t=2$ (-53.7% reduction).

---

## CLAIMS

What is claimed is:

### Claim 1 (Independent Method Claim)
A computer-implemented method for dynamic entropy-minimizing active clinical triage, comprising:
- receiving, by one or more processors, a multimodal patient presentation comprising unstructured clinical text and physiological parameters;
- mapping extracted clinical findings from the patient presentation to an initial categorical probability distribution $P_0(D)$ over a universe of clinical conditions $\Theta$;
- calculating, by the one or more processors, a Shannon diagnostic entropy $H(D) = -\sum_{i=1}^N P(d_i) \log_2 P(d_i)$ of the probability distribution;
- determining whether the Shannon diagnostic entropy $H(D)$ satisfies a predetermined convergence threshold $\epsilon_{\text{triage}}$;
- in response to determining that the Shannon diagnostic entropy exceeds the convergence threshold:
  - evaluating a plurality of candidate clinical inquiries $Q$, wherein each candidate inquiry $q \in Q$ is associated with a plurality of discrete observable outcomes $A_q$ and a calibrated likelihood matrix $P(A_q \mid d_i)$;
  - computing an Expected Mutual Information Gain $I(D; A_q) = H(D) - \sum_{a \in A_q} P(A_q = a) H(D \mid A_q = a)$ for each candidate inquiry;
  - selecting and presenting to a client device an optimal inquiry $q^* = \arg\max_{q \in Q} I(D; A_q)$;
  - receiving an observed clinical outcome $a^* \in A_{q^*}$;
  - updating the categorical probability distribution via Bayesian inference to produce a posterior distribution $P_{t+1}(d_i) \propto P(A_{q^*} = a^* \mid d_i) P_t(d_i)$; and
  - repeating the calculation of Shannon diagnostic entropy until the convergence threshold is satisfied or a maximum inquiry round limit is reached; and
- outputting a focused differential diagnosis set corresponding to the converged probability distribution.

### Claim 2 (Dependent Method Claim)
The method of claim 1, wherein selecting the optimal inquiry comprises filtering out inquiries having an Expected Mutual Information Gain below a minimum information utility threshold $\delta_{\min} = 0.02\text{ bits}$.

### Claim 3 (Dependent Method Claim)
The method of claim 1, wherein the convergence threshold $\epsilon_{\text{triage}}$ is approximately $0.45\text{ bits}$, and wherein the maximum inquiry round limit is 3 inquiries.

### Claim 4 (Dependent Method Claim)
The method of claim 1, further comprising:
- executing a plurality of specialist agents in parallel on the patient presentation, the specialist agents comprising a computer vision agent evaluating medical images, a natural language processing agent evaluating clinical text, and a predictive risk agent evaluating physiological vitals;
- assigning, for each specialist agent $k$, a Dempster-Shafer basic belief assignment $m_k: 2^\Theta \to [0, 1]$ over a power set of clinical hypotheses; and
- calculating an orthogonal cross-agent conflict parameter:
  $$K = \sum_{B \cap C = \emptyset} m_{\text{vis}}(B) \cdot m_{\text{nlp}}(C)$$
  quantifying disagreement between image evidence and linguistic evidence.

### Claim 5 (Dependent Method Claim)
The method of claim 4, further comprising:
- comparing the conflict parameter $K$ against a conflict threshold $K_{\text{threshold}} = 0.40$;
- in response to $K \le K_{\text{threshold}}$, combining concordant belief masses via Dempster's orthogonal rule of combination:
  $$m(A) = \frac{1}{1 - K} \sum_{B \cap C = A} m_{\text{vis}}(B) \cdot m_{\text{nlp}}(C) \quad \text{for } A \neq \emptyset$$; and
- in response to $K > K_{\text{threshold}}$, routing candidate hypotheses to a neuro-symbolic knowledge graph pruning gate prior to combination.

### Claim 6 (Dependent Method Claim)
The method of claim 5, wherein routing to the neuro-symbolic knowledge graph pruning gate comprises:
- projecting conflicting hypotheses onto directed acyclic graph (DAG) ontological paths of a biomedical knowledge graph comprising at least one of the Unified Medical Language System (UMLS) Metathesaurus, SNOMED-CT, or ICD-10 ontologies;
- evaluating biological compatibility axioms between radiological image findings and clinical textual findings; and
- pruning candidate hypotheses that lack valid ontological path support.

### Claim 7 (Independent Method Claim)
A computer-implemented method for multimodal risk-controlled diagnostic bounding, comprising:
- generating, by one or more processors, a multimodal consensus probability distribution $\hat{P}(y \mid \mathbf{x})$ over a clinical condition universe $\Theta$ for a patient presentation $\mathbf{x}$;
- evaluating a non-conformity score $S(\mathbf{x}, y) = 1 - \hat{P}(y \mid \mathbf{x})$ for each candidate condition $y \in \Theta$;
- retrieving a calibrated conformal quantile cutoff $\hat{q}$ determined over a held-out calibration dataset of patient presentations $\{(\mathbf{x}_i, y_i)\}_{i=1}^n$ for a specified error tolerance $\alpha$;
- constructing a dynamically sized differential diagnosis set:
  $$\mathcal{C}(\mathbf{x}) = \{y \in \Theta : S(\mathbf{x}, y) \le \hat{q}\} = \{y \in \Theta : \hat{P}(y \mid \mathbf{x}) \ge 1 - \hat{q}\}$$; and
- outputting the dynamically sized differential diagnosis set, wherein the differential diagnosis set satisfies a finite-sample frequentist coverage guarantee:
  $$\mathbb{P}\left(Y_{\text{true}} \in \mathcal{C}(\mathbf{x})\right) \ge 1 - \alpha$$
  free of parametric distributional assumptions.

### Claim 8 (Dependent Method Claim)
The method of claim 7, wherein the calibrated conformal quantile cutoff $\hat{q}$ is computed as:
$$\hat{q} = \text{Quantile}_{\frac{\lceil (n + 1)(1 - \alpha) \rceil}{n}}\left( \{S(\mathbf{x}_i, y_i)\}_{i=1}^n \right)$$
where $n$ is the number of calibration samples and $\alpha = 0.05$, providing a 95% statistical coverage guarantee.

### Claim 9 (Dependent Method Claim)
The method of claim 7, further comprising monitoring a cardinality $|\mathcal{C}(\mathbf{x})|$ of the differential diagnosis set, and triggering an automated clinician alert in response to the cardinality exceeding a predetermined diagnostic ambiguity ceiling.

### Claim 10 (Independent System Claim)
A clinical decision support computing system, comprising:
- one or more processors; and
- one or more non-transitory computer-readable storage media storing instructions that, when executed by the one or more processors, cause the system to perform operations comprising:
  - receiving a patient presentation comprising unstructured text, physiological vitals, and a medical image;
  - constructing a prior categorical probability distribution $P_0(D)$ over a universe of clinical conditions $\Theta$;
  - computing a Shannon diagnostic entropy $H(D) = -\sum P(d_i) \log_2 P(d_i)$;
  - in response to $H(D)$ exceeding a triage threshold, iteratively identifying and presenting an inquiry $q^* = \arg\max I(D; A_q)$ maximizing Expected Mutual Information Gain and updating the probability distribution via Bayesian inference until $H(D)$ falls below the triage threshold;
  - dispatching the patient presentation to a plurality of specialist agents operating in parallel, including a computer vision agent generating a Grad-CAM saliency tensor and an NLP agent extracting clinical named entities;
  - assigning Dempster-Shafer belief mass functions to outputs of each specialist agent;
  - evaluating an orthogonal conflict parameter $K = \sum_{B \cap C = \emptyset} m_1(B) m_2(C)$;
  - in response to $K$ exceeding a conflict threshold, filtering candidate hypotheses against a biomedical ontology knowledge graph; and
  - synthesizing a dual-persona clinical report presenting a clinician interface displaying the Grad-CAM saliency tensor and ICD-10 differential, and a patient interface displaying a plain-language summary and urgent red-flag warnings.

### Claim 11 (Dependent System Claim)
The system of claim 10, wherein the operations further comprise constructing a dynamically sized conformal prediction set $\mathcal{C}(\mathbf{x})$ guaranteeing $\mathbb{P}(Y_{\text{true}} \in \mathcal{C}(\mathbf{x})) \ge 0.95$.

### Claim 12 (Non-Transitory Computer-Readable Medium Claim)
A non-transitory computer-readable storage medium storing instructions that, when executed by one or more processors, cause the one or more processors to perform operations comprising the method of claim 1.

---

## ABSTRACT
A multimodal Clinical Decision Support System (CDSS) termed AegisMed and associated computer-implemented methods for active diagnostic triage and multi-agent conflict arbitration are disclosed. An initial patient presentation is evaluated by a Dynamic Entropy-Minimizing Active Triage (DEMAT) engine that calculates Shannon diagnostic entropy $H(D)$ over a condition universe. When entropy exceeds a convergence threshold, DEMAT evaluates candidate clinical inquiries and selects the inquiry $q^* = \arg\max I(D; A_q)$ that maximizes Expected Mutual Information Gain, sequentially collapsing diagnostic ambiguity prior to deep multi-agent dispatch. Parallel specialist agents (Computer Vision with Grad-CAM saliency heatmaps, Clinical NLP, Biostatistical Risk, and RAG guidelines) produce inferences mapped to Dempster-Shafer belief masses. An Evidential Neuro-Symbolic Arbiter (EN-SCAF) computes an orthogonal conflict parameter $K$; when $K > 0.40$, candidate hypotheses are filtered against a biomedical ontology DAG pruning gate before Dempster combination. A conformal synthesis layer provides $1 - \alpha$ distribution-free coverage guarantees.
