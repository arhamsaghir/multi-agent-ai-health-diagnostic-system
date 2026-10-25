# AegisMed — Provisional Patent Application Filing Checklist

**Document Version:** 1.0  
**Date:** October 2026  
**Status:** Filing Preparation & Assembly Complete — Awaiting User Execution  
**Project:** AegisMed Clinical Decision Support System (CDSS)  
**Notice:** *This checklist is a procedural guide for the human applicant and patent agent. The AI system prepares all required technical artifacts; actual submission to patent offices requires human legal authorization, execution of statutory declarations, and payment of official fees.*

---

## 1. Jurisdiction Route & Strategic Decision

### Selected Default Route: Indian Patent Office (IPO)
- **Rationale:** Project affiliation, institutional research base, and priority establishment under the Indian Patents Act, 1970.
- **Convention Advantage:** Filing a provisional application in India secures an immediate priority date under the Paris Convention, granting a 12-month window to file complete applications or international applications (PCT / USPTO / EPO) while preserving worldwide novelty.
- **Alternative / Dual-Filing Route:** USPTO 35 U.S.C. § 111(b) provisional application (can be filed concurrently or within 12 months claiming foreign priority).

---

## 2. Statutory Documents & Deliverables Matrix

Every filing component is tracked below. All technical preparation is complete and mapped to repository files. Statutory actions requiring human legal execution are explicitly flagged as `BLOCKED: user action`.

| # | Filing Component | Description | Repo Artifact / File Location | Status | Action Required |
|:---|:---|:---|:---|:---|:---|
| **1** | **Provisional Specification (Markdown)** | Authoritative technical disclosure and claims draft | `patent/specification/provisional_patent_specification.md` | `READY` | None (repo source) |
| **2** | **Provisional Specification (DOCX)** | Editable filing-ready document formatted for patent attorney review | `patent/specification/provisional_patent_specification.docx` | `READY` | None (exported) |
| **3** | **Drawing Figures Bundle (300 DPI)** | 5 statutory line diagrams and execution flows (FIGS. 1–5) | `patent/figures/FIG_[1-5]*.png` | `READY` | None (verified 300 DPI) |
| **4** | **Figure Generator Script** | Fully reproducible diagram compilation pipeline | `scripts/patent/generate_patent_figures.py` | `READY` | None (reproducible) |
| **5** | **Patent Agent Technical Brief** | Technical summary, prior art search queries, and Section 3(k)/3(i) defense notes | `patent/PATENT_AGENT_BRIEF.md` | `READY` | None (ready for counsel) |
| **6** | **Portfolio Summary & Claim Matrix** | 12-claim traceability table mapping claims to source code & figures | `patent/PATENT_PORTFOLIO_SUMMARY.md` | `READY` | None (complete) |
| **7** | **IPO Form 1 (Application for Grant)** | Statutory application form detailing applicant and inventor details | `patent/filing_forms/ipo/Form_1_template.md` *(see §3 below)* | `BLOCKED: user action` | Applicant must sign and date |
| **8** | **IPO Form 2 (Provisional Specification)** | Statutory cover sheet for provisional technical description | `patent/filing_forms/ipo/Form_2_template.md` *(see §3 below)* | `BLOCKED: user action` | Attach DOCX/PDF & sign |
| **9** | **IPO Form 3 (Section 8 Undertaking)** | Foreign filing undertaking (if concurrent USPTO filing is planned) | Statutory IPO form | `BLOCKED: user action` | Disclose foreign filings if any |
| **10** | **IPO Form 5 (Declaration of Inventorship)** | Formal declaration of true and first inventors | Statutory IPO form | `BLOCKED: user action` | Inventor signature required |
| **11** | **IPO Form 26 (Power of Attorney)** | Authorizes registered Indian Patent Agent to act on behalf of inventors | Required if using external agent | `BLOCKED: user action` | Execute on stamp paper if using agent |
| **12** | **Statutory Filing Fee Payment** | Official fee (Natural Person: ₹1,600 / Small Entity: ₹4,000 / Others: ₹8,000) | IPO e-Filing Portal payment | `BLOCKED: user action` | Payment via ipindia.gov.in portal |
| **13** | **USPTO Cover Sheet (PTO/SB/16)** | Provisional Application Cover Sheet (if filing US route) | USPTO e-filing (Patent Center) | `BLOCKED: user action` | Complete online via Patent Center |
| **14** | **USPTO Statutory Filing Fee** | Official fee (Micro Entity: $60 / Small: $120 / Undiscounted: $300) | USPTO Payment Portal | `BLOCKED: user action` | Payment via Patent Center |

---

## 3. Statutory Forms Preparation Details (IPO Route)

### IPO Form 1 (Application for Grant of Patent)
- **Application Type:** Ordinary Application (Provisional)
- **Title:** *SYSTEM AND METHOD FOR DYNAMIC ENTROPY-MINIMIZING ACTIVE CLINICAL TRIAGE AND EVIDENTIAL MULTI-AGENT DIAGNOSTIC CONFLICT ARBITRATION*
- **Field of Invention:** Computer-Implemented Inventions / Biomedical Informatics / Clinical Decision Support Systems
- **Applicant & Inventor:** Arham Saghir & Team AegisMed Contributors
- **Address for Service:** To be completed by registered patent agent or lead inventor.

### IPO Form 2 (Provisional Specification)
- **Preamble to Description:** *"PROVISIONAL SPECIFICATION: The following specification describes the invention."*
- **Body of Specification:** Integrated directly from `patent/specification/provisional_patent_specification.docx`.
- **Drawings Sheet:** 5 sheets of drawings attached as per Rule 15 of Indian Patents Rules (attached from `patent/figures/`).

### Statutory Compliance with Indian Patent Office Rules:
1. **Rule 13 (Specifications):** Margins set to minimum 4 cm top/left, 3 cm bottom/right; clean font, sequentially numbered paragraphs.
2. **Rule 15 (Drawings):** 300 DPI clear line drawings, reference numerals matching detailed description (100–126, 200–216, 300–322, 400–414, 500–518).
3. **Section 3(k) & 3(i) Compliance:** Verified and documented in `patent/PATENT_AGENT_BRIEF.md`.

---

## 4. Alternative: USPTO Provisional Route (35 U.S.C. § 111(b))

If the applicant elects to file in the United States directly:
1. **Filing Method:** USPTO Patent Center (online e-filing portal).
2. **Documents to Upload:**
   - Completed Form PTO/SB/16 (Provisional Application Cover Sheet).
   - Specification PDF / DOCX (from `patent/specification/provisional_patent_specification.docx`).
   - Drawings PDF (from `patent/figures/` bundle).
3. **Inventor Declarations:** Under 35 U.S.C. § 111(b), formal inventor oaths/declarations and prior art disclosure (IDS) are **not** required for a provisional filing, significantly reducing initial filing friction.
4. **Term:** Expires exactly 12 months after filing date; non-provisional application claiming benefit under 35 U.S.C. § 119(e) must be filed prior to expiration.

---

## 5. Pre-Publication Embargo Protocol

> **CRITICAL REMINDER:**  
> Under both Indian patent law (Section 29–34) and international patent law (PCT / Paris Convention), absolute novelty is required.  
> **Do not publish the research paper (`paper/phase3-paper/main.pdf`), post code to public GitHub, or present findings at seminars until the provisional application receives an official Application Number and Electronic Filing Receipt from the patent office.**

---

## 6. Execution Steps for the Human Applicant

1. **Step 1:** Transmit `patent/specification/provisional_patent_specification.docx`, `patent/figures/`, and `patent/PATENT_AGENT_BRIEF.md` to your designated patent practitioner.
2. **Step 2:** Decide between IPO Form 2 provisional vs. USPTO § 111(b) provisional (default recommendation: IPO for local cost efficiency and Paris Convention priority).
3. **Step 3:** Review and sign Form 1 and Form 2 (or PTO/SB/16).
4. **Step 4:** Pay the statutory filing fee via the respective government portal.
5. **Step 5:** Record the official Application Number and Date of Filing in this repository.
6. **Step 6:** Lift public disclosure embargo and proceed with conference submission.
