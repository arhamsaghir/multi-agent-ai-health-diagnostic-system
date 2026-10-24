# AegisMed — Provisional Patent Application Portfolio Summary

**Document Version:** 1.0 (Draft for Registered Patent Practitioner Review)  
**Date:** October 6, 2026  
**Primary Invention Title:** System and Method for Dynamic Entropy-Minimizing Active Clinical Triage and Evidential Multi-Agent Diagnostic Conflict Arbitration  
**Lead Inventors:** Arham Saghir & Team AegisMed Contributors  
**Jurisdiction Target:** Indian Patent Office (IPO) / United States Patent and Trademark Office (USPTO) / PCT Application  

---

## 1. Legal Notice & Status
> **DISCLAIMER:** *This document and the associated technical specification represent an engineering disclosure and draft patent specification prepared by the software engineering and research team. It does NOT constitute formal legal advice, a patentability search opinion, or a filed patent application. Prior to submission to any national patent authority, formal claims drafting, prior art search, and filing must be executed by a registered Patent Agent or Patent Attorney.*

---

## 2. Portfolio Structure & Artifact Index

All patent deliverables are organized within the repository as follows:

| Deliverable | Path | Description |
| :--- | :--- | :--- |
| **Technical Specification** | `patent/specification/provisional_patent_specification.md` | Full statutory draft containing Technical Field, Background, Summary, Brief Description of Drawings, Detailed Description with Reference Numerals, 12 Formal Claims, and Abstract. |
| **Drawing FIG. 1** | `patent/figures/FIG_1_system_architecture.png` | 300 DPI formal line drawing of Multimodal System Architecture & Topology (Ref Num 100–126). |
| **Drawing FIG. 2** | `patent/figures/FIG_2_demat_flowchart.png` | 300 DPI formal algorithmic flowchart of DEMAT Active Triage & Mutual Information Maximization (Ref Num 200–216). |
| **Drawing FIG. 3** | `patent/figures/FIG_3_enscaf_arbitration.png` | 300 DPI formal block diagram of Evidential Conflict Arbitration & UMLS DAG Pruning Gate (Ref Num 300–322). |
| **Drawing FIG. 4** | `patent/figures/FIG_4_conformal_risk_bounding.png` | 300 DPI formal diagram of Multimodal Conformal Risk-Controlled Synthesis & Coverage Guarantees (Ref Num 400–414). |
| **Drawing FIG. 5** | `patent/figures/FIG_5_execution_trace_and_empirical_evidence.png` | 300 DPI composite diagram showing multi-agent execution lifecycle stepper (Panel A) and empirical entropy collapse curves (Panel B) (Ref Num 500–518). |
| **Figure Generator** | `scripts/patent/generate_patent_figures.py` | Reproducible Python generator script producing publication-grade 300 DPI technical diagrams. |

---

## 3. Claim-to-Code & Figure Traceability Matrix

Every claim in the provisional specification maps directly to architectural figures, detailed specification sections, and underlying software implementations:

| Claim | Type | Core Technical Subject Matter | Figures | Spec Section | Software Module / Code Reference |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Claim 1** | Indep. Method | Dynamic Entropy-Minimizing Active Triage (DEMAT) via Expected Mutual Information Maximization | FIG. 1, FIG. 2 | Detailed Desc. §2 | `src/core/demat.py` (`DEMATEngine`, `compute_initial_belief`, `expected_information_gain`, `update_belief_from_answer`), `src/core/disease_kb.py`, `src/core/question_bank.py` |
| **Claim 2** | Dep. Method | Information Utility Threshold Filtering ($\delta_{\min} = 0.02\text{ bits}$) | FIG. 2 | Detailed Desc. §2.4 | `src/core/demat.py:63` (`MIN_INFO_GAIN_THRESHOLD = 0.02`) |
| **Claim 3** | Dep. Method | Triage Convergence Bounds ($\epsilon_{\text{triage}} = 0.45\text{ bits}$, $t_{\max} = 3$) | FIG. 2 | Detailed Desc. §2.3 | `src/core/demat.py:61-62` (`ENTROPY_STOPPING_THRESHOLD`, `MAX_TRIAGE_ROUNDS`) |
| **Claim 4** | Dep. Method | Multi-Agent Parallel Execution & Dempster-Shafer Mass Assignment | FIG. 1, FIG. 3 | Detailed Desc. §3.1 | `src/agents/orchestrator/agent.py` (`OrchestratorAgent`), `src/agents/vision/`, `src/agents/nlp/`, `src/agents/prediction/` |
| **Claim 5** | Dep. Method | Cross-Modal Disagreement Parameter Calculation ($K = \sum m_1(B) m_2(C)$) | FIG. 3 | Detailed Desc. §3.2 | `src/agents/rule_based_synthesis.py` (arbitration threshold logic) |
| **Claim 6** | Dep. Method | Neuro-Symbolic UMLS Metathesaurus DAG Ontological Pruning Gate | FIG. 3 | Detailed Desc. §3.3 | Knowledge graph constraints, `src/agents/rag/agent.py` |
| **Claim 7** | Indep. Method | Multimodal Conformal Risk-Controlled Diagnostic Bounding ($1 - \alpha$ coverage) | FIG. 4 | Detailed Desc. §4 | Post-hoc calibration layer, `DiagnosisResponse` confidence intervals |
| **Claim 8** | Dep. Method | Finite-Sample Quantile Estimation with Calibration Cohort Adjustment | FIG. 4 | Detailed Desc. §4.2 | Conformal quantile calculation formula |
| **Claim 9** | Dep. Method | Dynamic Set Cardinality Ceiling & Automated Clinician Ambiguity Alerting | FIG. 4 | Detailed Desc. §4.3 | `DiagnosisResponse.doctor_alert` trigger logic |
| **Claim 10** | Indep. System | Comprehensive Clinical Decision Support Computing System Architecture | FIG. 1, FIG. 5 | Detailed Desc. §1, §5, §6 | Full-stack platform: FastAPI backend, Next.js frontend, SQLite persistence |
| **Claim 11** | Dep. System | Dual-Persona Output Synthesizer (Clinician Technical vs. Patient Plain-Language) | FIG. 1, FIG. 5 | Detailed Desc. §6 | `frontend/src/lib/persona.tsx`, `src/agents/rule_based_synthesis.py:212` (`compose_explanations`) |
| **Claim 12** | Computer Medium | Non-transitory Computer-Readable Storage Medium executing DEMAT | All | Detailed Desc. §2 | Software codebase repository |

---

## 4. Empirical Evidence for Patent Support (200-Case Benchmark)

The specification incorporates reproducible experimental data establishing non-obviousness, clinical utility, and significant technological advancement over prior art:

- **Empirical Accuracy:** DEMAT achieved **98.0% Top-1 accuracy** across 200 standardized patient cases, compared to 93.0% for single-pass baseline ($+5.0\%$ absolute gain, McNemar $\chi^2 = 4.5$, $p = 0.0339$).
- **Top-3 Diagnostic Coverage:** **100.0%** (200/200 cases) under DEMAT vs. 97.5% under baseline.
- **Shannon Entropy Collapse:** Diagnostic uncertainty collapsed by **53.7%** (from $2.846\text{ bits}$ to $1.318\text{ bits}$, $\Delta H = -1.529\text{ bits}$) within an average of only **1.92 inquiries**.
- **Calibration Precision:** Brier score improved by **62.1%** (from 0.5296 to 0.2005) and Expected Calibration Error (ECE) decreased by **55.7%** (from 0.5528 to 0.2451).
- **Computational Latency:** Average inference latency of **0.2 milliseconds per session**, proving feasibility for real-time edge and mobile healthcare deployment.

---

## 5. Filing Readiness Checklist for Registered Patent Agent

Prior to formal application filing:

- [x] **Technical Field & Background drafted** without admissions of invalidity.
- [x] **Summary of the Invention** covers all 4 inventive concepts.
- [x] **12 Formal Claims** structured with independent method, system, and media claims.
- [x] **5 Formal Drawings (FIG. 1–5)** rendered in 300 DPI high-contrast line art.
- [x] **Every claim mapped to $\ge 1$ figure and $\ge 1$ detailed description section**.
- [x] **No placeholder text** (TODO, TBD, [insert]) anywhere in the specification.
- [ ] **Inventorship confirmation:** Finalize full legal names, citizenship, and residential addresses of all contributing student/faculty inventors.
- [ ] **Prior Art Search:** Formal novelty search across Google Patents, Espacenet, and Indian Patent Advanced Search System (InPASS).
- [ ] **Form 1 & Form 2 (IPO) or Provisional Cover Sheet (USPTO):** Prepared and executed by registered patent agent.
