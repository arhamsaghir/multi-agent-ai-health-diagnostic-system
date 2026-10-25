"""
Generate the complete AEGISMED_PROJECT_VIVA_PREPARATION_GUIDE.docx
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def create_document():
    doc = docx.Document()
    
    # Page setup - Margins 1 inch (1440 twips)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.different_first_page_header_footer = False
        
        # Configure Header and Footer
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("AegisMed — B.Tech Final Year Project Viva Voce Defense Guide")
        hrun.font.name = "Calibri"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGBColor(0x71, 0x80, 0x96)
        
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("Department of Computer Science & Engineering | Confidential Academic Document")
        frun.font.name = "Calibri"
        frun.font.size = Pt(8.5)
        frun.font.color.rgb = RGBColor(0x71, 0x80, 0x96)

    # Styling helper functions
    def set_cell_background(cell, hex_color):
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        cell._tc.get_or_add_tcPr().append(shading)

    def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
        tcMar = parse_xml(
            f'<w:tcMar {nsdecls("w")}>'
            f'<w:top w:w="{top}" w:type="dxa"/>'
            f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
            f'<w:left w:w="{left}" w:type="dxa"/>'
            f'<w:right w:w="{right}" w:type="dxa"/>'
            f'</w:tcMar>'
        )
        cell._tc.get_or_add_tcPr().append(tcMar)

    def set_cell_border_left_only(cell, color="0D74CE", sz="36"):
        borders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'<w:top w:val="none"/>'
            f'<w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:bottom w:val="none"/>'
            f'<w:right w:val="none"/>'
            f'</w:tcBorders>'
        )
        cell._tc.get_or_add_tcPr().append(borders)

    def set_table_light_borders(table, border_color="CBD5E0"):
        tblPr = table._tbl.tblPr
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="single" w:sz="6" w:space="0" w:color="{border_color}"/>'
            f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="{border_color}"/>'
            f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{border_color}"/>'
            f'<w:left w:val="none"/>'
            f'<w:right w:val="none"/>'
            f'<w:insideV w:val="none"/>'
            f'</w:tblBorders>'
        )
        tblPr.append(borders)

    def add_callout(title_text, body_text, bg_color="F0F7FF", border_color="0D74CE"):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        tbl.columns[0].width = Inches(6.5)
        
        cell = tbl.cell(0, 0)
        set_cell_background(cell, bg_color)
        set_cell_border_left_only(cell, color=border_color, sz="36")
        set_cell_margins(cell, top=140, bottom=140, left=200, right=180)
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        run_title = p.add_run(f"📌 {title_text}\n")
        run_title.bold = True
        run_title.font.name = "Calibri"
        run_title.font.size = Pt(10.5)
        run_title.font.color.rgb = RGBColor(0x16, 0x20, 0x32)
        
        run_body = p.add_run(body_text)
        run_body.font.name = "Calibri"
        run_body.font.size = Pt(10)
        run_body.font.color.rgb = RGBColor(0x2D, 0x37, 0x48)
        
        p_after = doc.add_paragraph()
        p_after.paragraph_format.space_before = Pt(0)
        p_after.paragraph_format.space_after = Pt(4)

    def format_table(col_widths, headers, rows_data):
        table = doc.add_table(rows=1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_light_borders(table)
        
        for i, w in enumerate(col_widths):
            table.columns[i].width = Inches(w)
            
        hdr_cells = table.rows[0].cells
        for i, h in enumerate(headers):
            hdr_cells[i].text = h
            set_cell_background(hdr_cells[i], "162032")
            set_cell_margins(hdr_cells[i], top=120, bottom=120, left=120, right=120)
            p = hdr_cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            for run in p.runs:
                run.font.bold = True
                run.font.name = "Calibri"
                run.font.size = Pt(9.5)
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                
        trPr = table.rows[0]._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

        for r_idx, row_data in enumerate(rows_data):
            row = table.add_row()
            r_trPr = row._tr.get_or_add_trPr()
            r_trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
            
            bg_col = "F7FAFC" if r_idx % 2 == 1 else "FFFFFF"
            for c_idx, val in enumerate(row_data):
                cell = row.cells[c_idx]
                cell.text = str(val)
                set_cell_background(cell, bg_col)
                set_cell_margins(cell, top=90, bottom=90, left=120, right=120)
                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.15
                for run in p.runs:
                    run.font.name = "Calibri"
                    run.font.size = Pt(9.5)
                    run.font.color.rgb = RGBColor(0x2D, 0x37, 0x48)
                    if c_idx == 0:
                        run.font.bold = True
        p_sp = doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(0)
        p_sp.paragraph_format.space_after = Pt(4)

    def add_h1(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(16)
        h.paragraph_format.space_after = Pt(4)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.bold = True
        r.font.name = "Calibri"
        r.font.size = Pt(13.5)
        r.font.color.rgb = RGBColor(0x16, 0x20, 0x32)
        return h

    def add_h2(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(12)
        h.paragraph_format.space_after = Pt(3)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.bold = True
        r.font.name = "Calibri"
        r.font.size = Pt(11.5)
        r.font.color.rgb = RGBColor(0x0D, 0x74, 0xCE)
        return h

    def add_h3(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(8)
        h.paragraph_format.space_after = Pt(2)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.bold = True
        r.font.name = "Calibri"
        r.font.size = Pt(10.5)
        r.font.color.rgb = RGBColor(0x2C, 0x3E, 0x50)
        return h

    def add_p(text, bold_prefix=None):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.bold = True
            r_pre.font.name = "Calibri"
            r_pre.font.size = Pt(10)
            r_pre.font.color.rgb = RGBColor(0x16, 0x20, 0x32)
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(0x2D, 0x37, 0x48)
        return p

    def add_bullet(text, bold_prefix=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.bold = True
            r_pre.font.name = "Calibri"
            r_pre.font.size = Pt(10)
            r_pre.font.color.rgb = RGBColor(0x16, 0x20, 0x32)
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(0x2D, 0x37, 0x48)
        return p

    def add_qa(q_num, question, answer_bullets):
        add_h3(f"Q{q_num}: {question}")
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.columns[0].width = Inches(6.5)
        cell = tbl.cell(0, 0)
        set_cell_background(cell, "FBFDFF")
        set_cell_border_left_only(cell, color="0D74CE", sz="24")
        set_cell_margins(cell, top=100, bottom=100, left=160, right=140)
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        r_hdr = p.add_run("Recommended Defense Response:")
        r_hdr.font.bold = True
        r_hdr.font.name = "Calibri"
        r_hdr.font.size = Pt(9.5)
        r_hdr.font.color.rgb = RGBColor(0x0D, 0x74, 0xCE)
        
        for b_title, b_content in answer_bullets:
            bp = cell.add_paragraph()
            bp.paragraph_format.space_before = Pt(2)
            bp.paragraph_format.space_after = Pt(2)
            bp.paragraph_format.line_spacing = 1.15
            r_btitle = bp.add_run(f"• {b_title}: ")
            r_btitle.font.bold = True
            r_btitle.font.name = "Calibri"
            r_btitle.font.size = Pt(9.5)
            r_btitle.font.color.rgb = RGBColor(0x16, 0x20, 0x32)
            
            r_btext = bp.add_run(b_content)
            r_btext.font.name = "Calibri"
            r_btext.font.size = Pt(9.5)
            r_btext.font.color.rgb = RGBColor(0x2D, 0x37, 0x48)
            
        p_sp = doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(0)
        p_sp.paragraph_format.space_after = Pt(4)

    # ==================== DOCUMENT HEADER BLOCK ====================
    # Title Block Table
    t_title = doc.add_table(rows=1, cols=1)
    t_title.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_cell = t_title.cell(0, 0)
    set_cell_background(t_cell, "162032")
    set_cell_margins(t_cell, top=200, bottom=200, left=240, right=240)
    
    tp = t_cell.paragraphs[0]
    tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tr1 = tp.add_run("AEGISMED: MULTI-AGENT CLINICAL DECISION SUPPORT SYSTEM\n")
    tr1.font.bold = True
    tr1.font.name = "Calibri"
    tr1.font.size = Pt(16)
    tr1.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    
    tr2 = tp.add_run("Comprehensive B.Tech Project Viva Voce Defense Preparation Document\n")
    tr2.font.name = "Calibri"
    tr2.font.size = Pt(12)
    tr2.font.color.rgb = RGBColor(0x63, 0xB3, 0xED)
    
    tr3 = tp.add_run("Candidate: Arham Saghir | Department of Computer Science & Engineering | Academic Year 2026-2027")
    tr3.font.name = "Calibri"
    tr3.font.size = Pt(9.5)
    tr3.font.color.rgb = RGBColor(0xCB, 0xD5, 0xE0)

    p_init = doc.add_paragraph()
    p_init.paragraph_format.space_before = Pt(6)
    p_init.paragraph_format.space_after = Pt(4)

    # Executive Opening Callout
    add_callout(
        "Executive Viva Strategy & 60-Second Opening Pitch",
        "Professors evaluate final-year AI projects on three criteria: (1) Did you build an actual engineering system rather than an API wrapper? (2) Is there verifiable mathematical and algorithmic novelty? (3) Do you understand clinical safety and failure boundaries?\n\n"
        "Your 60-Second Pitch: 'Current medical AI systems are passive, monolithic models that guess diagnoses in one pass. They fail in clinical practice because symptoms are ambiguous, imaging and notes often contradict each other, and neural networks hallucinate without statistical bounds. In AegisMed, we replace passive one-shot guessing with an active, multi-agent clinical decision support system. We introduce four key contributions: (1) DEMAT, which uses Shannon entropy and mutual information gain to ask the most informative clarifying question; (2) EN-SCAF, which uses Dempster-Shafer theory to catch and arbitrate cross-modal contradictions between chest X-rays and symptoms; (3) an Ontological Pruning Gate backed by UMLS/SNOMED-CT; and (4) Conformal Risk Bounding providing 95% statistical coverage guarantees. Across our 200-case empirical benchmark, DEMAT improved Top-1 accuracy from 93.0% to 98.0% (p = 0.0339) and collapsed diagnostic entropy by 53.7% in under two questions on average.'"
    )

    # ==================== 1. RESEARCH PROGRESS ====================
    add_h1("1. Research Progress")
    
    add_h2("1.1 The Clinical Diagnostic Problem & Motivation")
    add_p("Modern clinical environments face severe cognitive overload, physician burnout, and data fragmentation. Diagnostic errors contribute to roughly 10% of patient deaths and up to 17% of adverse hospital events. Patients present with overlapping, incomplete symptoms across disparate modalities: raw electronic health notes (unstructured text), chest radiographs (imaging), and vital signs (structured tabular data). Existing AI diagnostic systems fail because they treat medical diagnosis as an isolated, single-pass pattern recognition problem rather than a dynamic, iterative clinical differential investigation.")

    add_h2("1.2 Three Structural Failures in Current Medical AI")
    add_bullet("Clinical data is partitioned across siloed software systems. Text notes, radiological DICOM/PNG scans, and laboratory vitals are rarely synthesized jointly. Clinicians must manually reconcile conflicting AI outputs.", "Failure 1: Data Fragmentation & Modality Silos — ")
    add_bullet("Human patients present with incomplete symptom descriptions. A patient reporting 'chest tightness and shortness of breath' could have acute coronary syndrome, pneumonia, pulmonary embolism, or GERD. A standard one-pass model guesses based on static priors. A human physician immediately asks targeted clarifying questions to eliminate competing differentials.", "Failure 2: Passive One-Shot Ingestion (The Ambiguity Trap) — ")
    add_bullet("Deep neural networks output uncalibrated softmax confidence scores without statistical coverage guarantees. When vision models and clinical notes disagree (e.g., clear pneumonia on imaging but patient only notes ankle pain), end-to-end models hallucinate synthetic justifications rather than escalating to a physician.", "Failure 3: The 'Black Box' & Unbounded Risk Problem — ")

    add_h2("1.3 Research Objectives")
    add_bullet("To design and deploy a cooperative multi-agent architecture where specialist agents (BioBERT for clinical NLP, PyTorch ResNet for radiography, Gradient Boosting for structured vitals, FAISS for clinical guidelines) communicate through a stateful orchestrator.", "Objective 1: Multi-Agent Council — ")
    add_bullet("To formalize Dynamic Entropy-Minimizing Active Triage (DEMAT), using Shannon entropy and mutual information gain to iteratively select the single most informative clarifying question.", "Objective 2: Active Information-Theoretic Triage — ")
    add_bullet("To implement the Evidential Neuro-Symbolic Conflict Arbitration Framework (EN-SCAF), using Dempster-Shafer theory to quantify cross-modal conflict K and trigger safety escalations when K > 0.40.", "Objective 3: Evidential Conflict Arbitration — ")
    add_bullet("To integrate layer4 Grad-CAM saliency heatmaps for chest radiographs and verifiable citation provenance for clinical guideline retrieval.", "Objective 4: Clinical Explainability & Grounding — ")
    add_bullet("To deliver a production-ready system compliant with HL7 FHIR R4B interoperability standards and featuring dual clinician/patient personas.", "Objective 5: Standards Compliance & Interface Dualism — ")

    add_h2("1.4 Research Questions")
    add_bullet("Can dynamic active questioning grounded in mutual information gain significantly improve diagnostic accuracy and calibration compared to passive single-pass ingestion?", "RQ1 (Active Inquiry): ")
    add_bullet("Can evidential belief mass combinations mathematically detect and arbitrate contradictions between radiological imaging and clinical text?", "RQ2 (Conflict Arbitration): ")
    add_bullet("Can distribution-free conformal prediction bounds provide provable 95% coverage guarantees without rendering prediction sets clinically useless?", "RQ3 (Risk Bounding): ")

    add_h2("1.5 Project Milestone Status (Work Completed to Date)")
    format_table(
        [1.2, 1.8, 2.3, 1.2],
        ["Project Phase", "Core Focus Area", "Delivered Artifacts & Capabilities", "Status"],
        [
            ["Phase 1", "Foundation & Core Models", "ResNet-18/50 architecture auto-detection; BioBERT NLP entity extraction; Grad-CAM engine; DEMAT core math; FastAPI backend & Next.js portal.", "COMPLETE (Verified)"],
            ["Phase 2", "Multi-Agent Coordination & UX", "LangGraph orchestrator; Server-Sent Events (SSE) execution stepper; Clinician/Patient dual-mode toggle; 500-guideline FAISS corpus; One-click ReportLab PDF generation.", "COMPLETE (Verified)"],
            ["Phase 3", "Empirical Benchmarking & IP", "200-case comparative clinical benchmark; 12-claim Provisional Patent Specification + 5 figures; 8-page ACM CHIL paper draft; Full FHIR R4B endpoints; 133+ passing automated tests.", "COMPLETE (Verified)"],
            ["Phase 4", "Clinical Trials & Deployment", "Retrospective cohort validation on credentialed MIMIC-IV dataset; PACS/DICOM listener; Statutory patent filing at Indian Patent Office (IPO) / USPTO.", "ROADMAP (Planned)"]
        ]
    )

    # ==================== 2. RESEARCH DESIGN ====================
    add_h1("2. Research Design & Architectural Innovations")
    
    add_h2("2.1 System Architecture Overview")
    add_p("AegisMed uses a stateful, directed multi-agent graph (built on LangGraph design patterns) rather than a sequential chain. When patient inputs arrive, the Orchestrator initiates parallel execution across specialized sensory agents. Execution events stream in real time to the frontend via Server-Sent Events (SSE).")

    format_table(
        [1.4, 1.6, 2.3, 1.2],
        ["Specialist Agent", "Underlying Technology", "Clinical Responsibility", "Output Data Type"],
        [
            ["Clinical NLP", "BioBERT (emrqa/clinical-biobert)", "Extracts clinical entities, detects negations ('no cough' vs 'cough'), parses symptom duration and severity.", "Structured symptom dictionary & severity vectors"],
            ["Medical Vision", "PyTorch ResNet-18/50 Backbone", "Classifies frontal chest radiographs across 15 standard thoracic categories; extracts Grad-CAM gradients at layer4[-1].", "15-class probability tensor + 224x224 heatmap array"],
            ["Tabular Prediction", "GradientBoosting / XGBoost", "Evaluates vital signs (BP, HR, SpO2, temp, glucose, BMI) against age/gender demographic risk curves.", "Baseline physiological risk scores [0.0 - 1.0]"],
            ["RAG Guidelines", "FAISS + all-MiniLM-L6-v2", "Semantic vector search across 500+ curated clinical guidelines (WHO, NICE, ACC/AHA, GOLD COPD).", "Ranked guideline passages with verified citations"],
            ["Synthesis & Arb.", "EN-SCAF + MCRC-DS Engine", "Calculates Dempster-Shafer conflict K, applies knowledge-graph pruning, runs DEMAT triage, and bounds conformal risk.", "Unified clinical report + FHIR R4B bundle"]
        ]
    )

    add_h2("2.2 Key Mathematical Algorithms")
    
    add_h3("Algorithm 1: DEMAT (Dynamic Entropy-Minimizing Active Triage)")
    add_p("DEMAT models the differential diagnosis D as a categorical probability distribution over m candidate diseases. Instead of presenting static questionnaires, it selects questions that maximize expected uncertainty reduction:")
    add_bullet("H(D) = - ∑ P(di) · log2 P(di). Maximum entropy occurs when all candidate diseases have equal probability (total ambiguity); minimum entropy (0.0 bits) represents absolute diagnostic certainty.", "1. Shannon Diagnostic Entropy: ")
    add_bullet("IG(D; q) = H(D) - E[H(D | q, a)]. Each candidate inquiry q in the question bank is evaluated against potential patient answers a in {Yes, No, Mild, Severe}. The question maximizing mutual information gain is selected.", "2. Expected Mutual Information Gain: ")
    add_bullet("P(di | a*) = [P(di) · L(a* | di)] / [∑ P(dj) · L(a* | dj)], where L(a* | di) is the clinical likelihood matrix representing the observed frequency of finding a* in disease di.", "3. Bayesian Posterior Updating: ")
    add_bullet("Questioning halts immediately if (a) Current Entropy H(D) <= 0.80 bits; (b) Maximum Information Gain max_q IG(D; q) < 0.02 bits; or (c) Maximum rounds r_max = 2 reached to prevent patient fatigue.", "4. Dynamic Stopping Rules: ")

    add_h3("Algorithm 2: EN-SCAF (Evidential Neuro-Symbolic Conflict Arbitration)")
    add_p("When specialist modalities disagree, standard neural networks average their outputs and produce dangerous compromises. EN-SCAF uses Dempster-Shafer Evidence Theory:")
    add_bullet("Each specialist agent k assigns a basic belief assignment (mass function) m_k(A) over hypotheses A in power set 2^Theta, such that ∑ m_k(A) = 1.", "1. Belief Mass Function: ")
    add_bullet("K = ∑ m_Vision(B) · m_Text(C) for all B ∩ C = ∅. K measures the total degree of direct contradiction between radiological imaging and clinical text/vitals.", "2. Orthogonal Conflict Coefficient K: ")
    add_bullet("• If K < 0.20: Modalities agree; fuse using Dempster's rule of combination.\n• If 0.20 <= K <= 0.40: Moderate conflict; traverse UMLS / SNOMED-CT knowledge graphs. If finding B and condition C share no physiological path in the DAG, prune the lower-confidence hypothesis.\n• If K > 0.40: Severe contradiction; suppress autonomous diagnosis, raise an audible clinical red-flag, and trigger mandatory clinician review.", "3. Three-Tier Safety Gate: ")

    add_h3("Algorithm 3: MCRC-DS (Multimodal Conformal Risk-Controlled Synthesis)")
    add_p("To avoid relying solely on point predictions that may fail silently, AegisMed applies split-conformal prediction to generate prediction sets with guaranteed distribution-free coverage:")
    add_bullet("Γ_α(x) = { d in D : s(x, d) <= q_hat_(1-α) }, where s(x, d) = 1 - P_hat(d | x) is the non-conformity score, and q_hat is the calibrated empirical quantile computed over calibration data. For α = 0.05, the true diagnosis is mathematically guaranteed to lie within prediction set Γ_0.05 in at least 95% of presentations.", "Conformal Prediction Set: ")

    add_h3("Algorithm 4: Grad-CAM Saliency Engine")
    add_p("To explain chest radiograph predictions, AegisMed extracts gradients from the final convolutional layer (layer4[-1] in ResNet):")
    add_bullet("α_k^c = (1/Z) ∑∑ (∂y^c / ∂A_ij^k). Global average pooling of gradients yields importance weight α_k^c for each feature map k with respect to target class c.", "1. Feature Map Weighting: ")
    add_bullet("L_GradCAM^c = ReLU(∑ α_k^c · A^k). Applying ReLU eliminates features that negatively contribute to class c. The activation map is normalized to [0, 255], mapped to a custom jet colormap, and blended at 45% alpha over the radiograph.", "2. Heatmap Generation & Overlay: ")

    add_h2("2.3 Justification: Why Agentic Council Beats Monolithic LLMs")
    format_table(
        [1.5, 2.5, 2.5],
        ["Evaluation Dimension", "Monolithic LLM Approach (GPT-4 Prompt)", "AegisMed Multi-Agent Council"],
        [
            ["Modality Processing", "Processes text and downsampled image tokens through a single shared attention graph. Text often overpowers visual tokens.", "Dedicated specialized neural backbones (PyTorch ResNet for vision, BioBERT for NLP) maintaining full resolution and inductive bias."],
            ["Diagnostic Investigation", "Passive one-shot generation. Either guesses immediately or asks broad, unstructured 10-question lists.", "Active, closed-loop entropy minimization (DEMAT) selecting the single most informative question using mutual information gain."],
            ["Contradiction Handling", "Hallucinates narrative compromises when modalities disagree (e.g., invented 'migraine-induced lung consolidation').", "Mathematical Dempster-Shafer conflict metric K. Rejects synthesis and triggers clinician escalation when K > 0.40."],
            ["Risk Calibration", "Uncalibrated softmax probabilities prone to overconfident hallucinations.", "MCRC-DS conformal prediction sets providing distribution-free 95% coverage guarantees."],
            ["Clinical Grounding", "Internal parameter weights prone to confabulated medical citations.", "FAISS RAG vector store over 500+ verified guidelines with strict citation provenance."]
        ]
    )

    # ==================== 3. IMPLEMENTATION ====================
    add_h1("3. Implementation Details, Datasets & Live Demo")
    
    add_h2("3.1 Full-Stack Technical Architecture")
    add_bullet("Built with Python 3.11+ using FastAPI. Features asynchronous request handling, Server-Sent Events (SSE) streaming for real-time agent execution events, and native HL7 FHIR R4B JSON bundle processing.", "Backend API Framework: ")
    add_bullet("Built with Next.js 16, React 19, TypeScript, and Tailwind CSS. Features dynamic Lucide iconography, interactive Recharts diagnostic radar plots, Grad-CAM opacity sliders, and dual-persona UI toggles.", "Frontend Clinical Portal: ")
    add_bullet("Headless PDF generation via ReportLab (/api/report/generate), compiling patient vitals, diagnostic differentials, entropy reduction traces, and legal disclaimers into an exportable document.", "Automated Clinical Reporting: ")

    add_h2("3.2 Datasets & Knowledge Corpora")
    add_bullet("NIH ChestX-ray14 & CheXpert standards covering 15 thoracic pathologies: Atelectasis, Cardiomegaly, Consolidation, Edema, Effusion, Emphysema, Fibrosis, Hernia, Infiltration, Mass, Nodule, Pleural Thickening, Pneumonia, Pneumothorax, and No Finding.", "Medical Vision Dataset: ")
    add_bullet("500+ curated, peer-reviewed clinical practice guidelines compiled from the World Health Organization (WHO), UK National Institute for Health and Care Excellence (NICE), American Heart Association (AHA), and Global Initiative for Chronic Obstructive Lung Disease (GOLD).", "Guideline Corpus: ")
    add_bullet("200 standardized multi-modal patient vignettes spanning 15 disease categories (Cardiovascular, Respiratory, Gastrointestinal, Neurological, Endocrine, etc.) designed for evaluation.", "Standardized Benchmark Cohort: ")

    add_h2("3.3 Live Demonstration Walkthrough Script (What to Show in Viva)")
    add_p("Follow this exact 6-step walkthrough when demonstrating the project to your professor:")
    add_bullet("Open http://localhost:3000/diagnosis. Enter chief complaint: 'Chest tightness, mild dry cough, shortness of breath.' Enter vitals: HR 98 bpm, BP 135/85, SpO2 94%. Upload sample chest radiograph. Click 'Run Multi-Agent Diagnosis'.", "Step 1: Patient Presentation — ")
    add_bullet("Direct the professor's attention to the Agent Execution Stepper. Point out the live Server-Sent Events (SSE) stream showing the NLP agent tokenizing symptoms, the vision agent generating activations, and the RAG agent querying guidelines.", "Step 2: SSE Execution Stepper — ")
    add_bullet("The initial differential displays high uncertainty: 'Shannon Diagnostic Entropy: 2.84 bits (High Ambiguity)'. The system generates a targeted inquiry: 'Do your symptoms worsen when lying flat on your back (Orthopnea)?' Answer 'Yes'. Show how the entropy drops to 1.31 bits, eliminating viral bronchitis and confirming congestive heart failure.", "Step 3: DEMAT Active Triage — ")
    add_bullet("Switch to the Medical Vision tab. Adjust the interactive opacity slider from 0% (raw grayscale radiograph) to 100% (Grad-CAM heatmap). Point out the localized activation over the lower lung bases.", "Step 4: Grad-CAM Saliency Map — ")
    add_bullet("Click the persona toggle in the top-right corner. Demonstrate the immediate transition from Clinician Mode (showing ICD-10 codes, Dempster-Shafer K values, and conformal prediction sets) to Patient Mode (plain-language summaries and red-flag advice).", "Step 5: Dual-Persona Toggle — ")
    add_bullet("Click 'Download Clinical Report'. Open the generated PDF showing the audit trail, execution metadata, and legal disclaimers.", "Step 6: One-Click PDF Export — ")

    # ==================== 4. RESULTS & VALIDATION ====================
    add_h1("4. Empirical Results & Validation")
    
    add_h2("4.1 Comparative Benchmark: DEMAT vs. Single-Pass Baseline")
    add_p("All figures are drawn directly from the verified 200-case empirical research benchmark (data/benchmarks/results/demat_research_benchmark.json):")

    format_table(
        [1.8, 1.4, 1.4, 1.2, 0.9],
        ["Performance Metric", "Arm 1: Full DEMAT Triage", "Arm 2: Single-Pass Baseline", "Absolute Delta", "Significance"],
        [
            ["Top-1 Diagnostic Accuracy", "98.0% (196/200)", "93.0% (186/200)", "+5.0%", "p = 0.0339 *"],
            ["Top-3 Differential Coverage", "100.0% (200/200)", "97.5% (195/200)", "+2.5%", "Clinically Safe"],
            ["Top-5 Differential Coverage", "100.0% (200/200)", "100.0% (200/200)", "0.0%", "Identical Tail"],
            ["Mean Shannon Entropy", "1.3178 bits", "2.8464 bits", "-53.7%", "-1.5286 bits"],
            ["Mean Brier Score (Error)", "0.2005", "0.5296", "-62.1%", "Sharper Probs"],
            ["Expected Calibration Error", "0.2451", "0.5528", "-55.7%", "Well Calibrated"],
            ["Mean Questions Asked", "1.92 inquiries", "0.00 (N/A)", "+1.92", "Low Burden"],
            ["Mean Triage Latency", "0.37 ms", "0.10 ms", "+0.27 ms", "Real-Time"]
        ]
    )

    add_h2("4.2 Category-Level Breakdown (Where DEMAT Wins)")
    format_table(
        [1.8, 1.0, 1.2, 1.2, 1.3],
        ["Clinical Disease Category", "Cases (N)", "DEMAT Top-1", "Ablation Top-1", "Advantage (Delta)"],
        [
            ["Cardiovascular", "28", "85.71%", "71.43%", "+14.28% (DEMAT Win)"],
            ["Respiratory", "42", "100.00%", "85.71%", "+14.29% (DEMAT Win)"],
            ["Endocrine", "13", "100.00%", "100.00%", "0.00% (Tied High)"],
            ["Neurological", "26", "100.00%", "100.00%", "0.00% (Tied High)"],
            ["Gastrointestinal", "26", "100.00%", "100.00%", "0.00% (Tied High)"],
            ["Psychiatric / Others", "65", "100.00%", "100.00%", "0.00% (Tied High)"]
        ]
    )

    add_h2("4.3 Statistical Significance Analysis")
    add_p("To test whether the 5.0% Top-1 accuracy gain was statistically meaningful rather than random variation, we conducted a paired McNemar Chi-Square test across the 200 standardized clinical cases:")
    add_bullet("There were 14 cases where DEMAT was correct and the single-pass baseline failed, versus only 4 cases where the single-pass baseline was correct and DEMAT was not.", "Contingency Matrix: ")
    add_bullet("χ² = (|14 - 4| - 1)² / (14 + 4) = 81 / 18 = 4.50. The resulting two-tailed p-value is 0.033895 (p = 0.0339).", "McNemar Test Statistic: ")
    add_bullet("Because p < 0.05, the null hypothesis of equal diagnostic capability is rejected. The active questioning mechanism provides a statistically significant improvement in diagnostic accuracy.", "Scientific Conclusion: ")

    # ==================== 5. TECHNICAL CHALLENGES ====================
    add_h1("5. Engineering Challenges Faced & Solutions")
    
    add_h2("Challenge 1: Medical Vision Checkpoint Architecture Mismatch")
    add_p("The pretrained weights file models/vision_resnet50.pth was failing to load into a ResNet-50 model. Inspection revealed that the final fully connected weights had shape [15, 512]. ResNet-50 uses a 2048-dimensional bottleneck feature vector, meaning the checkpoint was actually a trained ResNet-18 model with an incorrect filename. Hardcoding ResNet-50 caused weights to be silently initialized randomly.", bold_prefix="The Bug: ")
    add_p("We implemented dynamic architecture inspection in src/agents/vision/agent.py. The loader now reads checkpoint tensor dimensions before building the PyTorch graph: if fc.weight.shape[1] == 512, it instantiates ResNet-18; if 2048, it instantiates ResNet-50.", bold_prefix="The Solution: ")

    add_h2("Challenge 2: Cross-Modal Contradictions (Text vs. Vision)")
    add_p("When testing patient vignettes with contradictory data (e.g., an elderly patient with pneumonia on X-ray who only complained of a mild migraine), early prototypes generated a blended text report suggesting the patient had 'migraine-induced lung consolidation.'", bold_prefix="The Bug: ")
    add_p("We integrated the EN-SCAF arbitration gate. We compute Dempster's orthogonal conflict parameter K. If K > 0.40, the system locks down synthetic blending, flags a severe cross-modal disagreement, and explicitly presents both findings side-by-side with an alert requiring human clinical review.", bold_prefix="The Solution: ")

    add_h2("Challenge 3: Silent Random Fallback in RAG Embeddings")
    add_p("During test runs, identical guideline text queries returned near-zero cosine similarity scores (~0.06). We discovered that transformers 5.7.0 had an incompatible dependency on huggingface-hub, which caused the SentenceTransformer import to fail silently and fall back to generating random Gaussian vectors.", bold_prefix="The Bug: ")
    add_p("We traced the import exception in src/data/embedding.py, pinned huggingface-hub>=1.5.0,<2.0 in requirements.txt, and wrote a regression test (tests/unit/test_embedding.py) asserting that identical clinical strings produce a cosine similarity > 0.99.", bold_prefix="The Solution: ")

    add_h2("Challenge 4: Operating System Storage Eviction (macOS Dataless APFS)")
    add_p("Pytest began hanging mysteriously during test collection on macOS. Investigation revealed that iCloud Drive's 'Optimize Mac Storage' feature had silently evicted 33,000 files in the virtual environment directory (venv/), turning Python packages into 0-byte dataless APFS placeholders.", bold_prefix="The Bug: ")
    add_p("We rebuilt the environment in an un-evicted directory named venv.nosync/ using uv, placed a .nosync barrier file inside it to permanently disable macOS iCloud eviction, and symlinked venv to it.", bold_prefix="The Solution: ")

    # ==================== 6. FUTURE PLAN ====================
    add_h1("6. Future Plan & Project Roadmap")
    format_table(
        [1.2, 1.4, 2.7, 1.2],
        ["Timeline", "Milestone", "Specific Deliverables & Objectives", "Status"],
        [
            ["Nov 2026", "Statutory Patent Filing", "File Form 2 provisional specification with all 12 claims and 5 formal figures at the Indian Patent Office (IPO) / USPTO to secure priority date.", "READY FOR USER FILING"],
            ["Dec 2026", "Academic Submission", "Submit the compiled 8-page double-blind research manuscript to ACM CHIL 2027 / MICCAI workshop.", "MANUSCRIPT READY"],
            ["Jan-Feb 2027", "Clinical Cohort Trial", "Conduct retrospective clinical validation using credentialed MIMIC-IV EHR records and the CheXpert validation cohort.", "PLANNED"],
            ["Mar 2027", "PACS / DICOM Native Integration", "Implement pydicom listeners to ingest raw 16-bit radiological DICOM studies directly from hospital PACS servers.", "PLANNED"],
            ["May 2027", "Final B.Tech Defense", "Deliver final project dissertation, comprehensive demonstration, and public open-source benchmark repository.", "TARGET"]
        ]
    )

    # ==================== 7. PROFESSOR GRILL VAULT ====================
    add_h1("7. The Professor Grill-Session: Top 10 Questions & Answers")
    
    add_qa(
        1, "Why did you build a multi-agent system? Couldn't I just give GPT-4 a detailed system prompt and get the same result?",
        [
            ("Modality Isolation & Inductive Bias", "A monolithic LLM processes image and text tokens through a single self-attention matrix. In clinical cases, extensive text tokens frequently overpower visual tokens, leading to missed radiological findings. AegisMed preserves specialized inductive biases by running a dedicated convolutional network on raw pixels."),
            ("Formal Statistical Guarantees", "Prompted LLMs cannot provide distribution-free risk bounds. AegisMed uses split-conformal prediction (MCRC-DS) to output guaranteed prediction sets with 95% coverage."),
            ("Active vs. Passive Triage", "Prompted LLMs either guess in one shot or ask long, rambling surveys. DEMAT calculates exact Shannon entropy values and picks the mathematically optimal question using mutual information gain.")
        ]
    )

    add_qa(
        2, "What is your actual intellectual property here? What are you patenting?",
        [
            ("Three Technical Pillars", "Our provisional patent specification contains 12 claims structured around three novel software mechanisms:"),
            ("1. The DEMAT Closed-Loop", "Modeling differential diagnoses as categorical distributions, calculating mutual information gain across an inquiry bank, and executing Bayesian updates until entropy falls below 0.80 bits."),
            ("2. The EN-SCAF Arbitrator", "Mapping continuous neural activations to discrete Dempster-Shafer belief masses and gating outputs based on the orthogonal conflict parameter K coupled with knowledge-graph traversal."),
            ("3. Conformal Dual-Persona Pipeline", "Structuring split-conformal risk bounds across multi-agent outputs with dynamic persona translation.")
        ]
    )

    add_qa(
        3, "Is AegisMed legally diagnosing patients? What about medical liability?",
        [
            ("Regulatory Classification", "AegisMed is explicitly designed as a Clinical Decision Support System (CDSS) under FDA 21 CFR Section 820 and EU MDR guidelines—not an autonomous medical device."),
            ("Human-in-the-Loop Safeguards", "It provides probabilistic decision support, explainable heatmaps, and guideline citations to assist licensed physicians. Every report includes a statutory disclaimer, and when high cross-modal conflict (K > 0.40) or high diagnostic entropy occurs, the system locks into mandatory physician escalation mode.")
        ]
    )

    add_qa(
        4, "Why did you use ResNet instead of a Vision Transformer (ViT)?",
        [
            ("Localized Radiological Lesions", "While Vision Transformers capture global context well, convolutional architectures possess strong inductive biases for local translation equivariance, which is critical for identifying localized lesions such as small nodules or pleural effusions."),
            ("Deterministic Gradient Explanations", "Computing Grad-CAM gradients on ResNet's final convolutional layer (layer4[-1]) is mathematically well-defined, computationally efficient (~15 ms on standard hardware), and produces crisp, clinically verifiable localization maps without the high GPU memory overhead of ViT self-attention matrices.")
        ]
    )

    add_qa(
        5, "How does DEMAT know which questions exist, and could it ask an irrelevant question?",
        [
            ("Calibrated Question Bank", "Questions are not generated unconstrained. DEMAT draws from a curated clinical inquiry bank linked to our disease knowledge base. Each question has a pre-computed conditional likelihood matrix P(a | di) representing the historical probability of an answer given a disease."),
            ("Mutual Information Filtering", "Because DEMAT weights questions by Expected Mutual Information Gain I(D; q), any question whose answers do not shift the probability distribution across the current differential yields IG ≈ 0 and is filtered out.")
        ]
    )

    add_qa(
        6, "Why use Dempster-Shafer theory instead of simple Bayesian probability for conflict resolution?",
        [
            ("Epistemic Ignorance vs. Uncertainty", "Bayesian probability forces all unassigned probability into known hypotheses (∑ P = 1), which conflates 'equal uncertainty among known diseases' with 'complete lack of evidence.'"),
            ("Direct Mass Assignment to Theta", "Dempster-Shafer theory allows us to assign belief mass directly to the frame of discernment Theta (representing epistemic ignorance). This lets EN-SCAF cleanly distinguish between an agent saying 'I am confident it is disease A' versus 'I do not have enough data to tell,' which is essential for computing an honest conflict metric K.")
        ]
    )

    add_qa(
        7, "What happens when a patient presents with a disease not in your 15 benchmark classes?",
        [
            ("Conformal Prediction Safeguard", "Under out-of-distribution presentations, the model's non-conformity scores will be uniformly high."),
            ("Automatic Escalation", "Under MCRC-DS, the system either outputs an empty prediction set or a set containing all categories with high entropy (H(D) > 2.8 bits), which automatically triggers an out-of-distribution alert and directs the patient to an emergency department rather than offering an erroneous guess.")
        ]
    )

    add_qa(
        8, "How does the RAG system prevent hallucinations in the final synthesis?",
        [
            ("Verified Curated Corpus", "It retrieves strictly from a verified, curated local corpus of 500+ official clinical practice guidelines (WHO, NICE, AHA)."),
            ("Strict Similarity Gating", "Any retrieved chunk with a cosine similarity score below 0.65 is rejected."),
            ("Mandatory Provenance Anchoring", "The synthesis agent is constrained to include direct provenance keys (guideline name, publication year, section) in every recommendation. If no guideline matches, it falls back to a deterministic, rule-based clinical synthesis template.")
        ]
    )

    add_qa(
        9, "What is HL7 FHIR R4B, and why does an AI project need it?",
        [
            ("Global Healthcare Standard", "Most academic AI projects output plain JSON or raw text, meaning they can never be deployed in a hospital. HL7 FHIR (Fast Healthcare Interoperability Resources) is the global standard for electronic health records."),
            ("Native Resource Mapping", "AegisMed natively ingests and exports FHIR R4B Bundle resources containing Patient, Observation, Condition, DiagnosticReport, and Media resources. A hospital's existing Epic or Cerner EHR can query our /api/fhir/diagnose endpoint and receive a fully compliant clinical bundle.")
        ]
    )

    add_qa(
        10, "If your system works so well, what is its biggest current limitation?",
        [
            ("Standardized Cohort vs. Prospective ED Trial", "The primary limitation is that our benchmark evaluation was conducted on 200 standardized clinical vignettes rather than an IRB-approved prospective trial on real emergency department patients."),
            ("Plan for Resolution", "Our vision model currently evaluates frontal 2D chest radiographs rather than full volumetric 3D CT scans. Our Phase 4 roadmap specifically targets prospective validation on the MIMIC-IV cohort and full DICOM integration.")
        ]
    )

    # ==================== 8. RAPID-FIRE MEMORY CHEAT SHEET ====================
    add_h1("8. Rapid-Fire Viva Memory Cheat Sheet")
    add_p("Memorize these key numbers and facts right before walking into your viva:")
    
    format_table(
        [2.0, 4.5],
        ["Key Parameter / Metric", "Exact Verified Value to State in Viva"],
        [
            ["Top-1 Accuracy Gain", "98.0% (DEMAT) vs. 93.0% (Single-pass baseline) — a +5.0% absolute improvement"],
            ["Statistical Significance", "McNemar Chi-Square χ² = 4.50, p = 0.0339 (p < 0.05, statistically significant)"],
            ["Shannon Entropy Reduction", "53.7% reduction (mean initial 2.8464 bits collapsed to 1.3178 bits)"],
            ["Average Inquiries Asked", "1.92 questions per patient session (well below the 3-question fatigue ceiling)"],
            ["Triage Latency Overhead", "0.37 milliseconds (negligible computational overhead, operates in real time)"],
            ["Brier Score (Prob. Error)", "0.2005 (DEMAT) vs. 0.5296 (Baseline) — a 62.1% reduction in probabilistic error"],
            ["Expected Calibration Error", "0.2451 (DEMAT) vs. 0.5528 (Baseline) — a 55.7% improvement in calibration"],
            ["Conflict Threshold (K)", "K > 0.40 triggers mandatory clinician review; K < 0.20 permits autonomous fusion"],
            ["Conformal Coverage Bound", "1 - α = 0.95 (95% guaranteed statistical coverage across prediction sets)"],
            ["Passing Test Suite", "133+ passed automated tests across unit, integration, and API suites"]
        ]
    )

    # Save Document
    output_path = "/Users/arhamsaghir/Documents/All Projects/Final Year Project/AEGISMED_PROJECT_VIVA_PREPARATION_GUIDE.docx"
    doc.save(output_path)
    print(f"Document successfully created at: {output_path}")

if __name__ == "__main__":
    create_document()
