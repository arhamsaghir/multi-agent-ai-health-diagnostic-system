# AegisMed — Conference Submission Checklist (ACM CHIL / MICCAI)

**Target Venues:**
- **Primary:** ACM Conference on Health, Inference, and Learning (ACM CHIL) — Research Track
- **Secondary (Alternative):** MICCAI Workshop on Clinical Machine Learning / Multimodal AI in Healthcare

**Status:** Research Draft re-scoped to the mechanism contribution (publication-truth phase A); Repro Package Complete — **not** submission-ready until external evaluation numbers exist (see `data/benchmarks/RETIREMENT.md`; the manuscript currently makes no accuracy claim by design)  
**Notice:** *Submission requires author registration, OpenReview/HotCRP upload, and final blinding check by the corresponding author. The automated system compiles and verifies all technical artifacts; actual submission is the user's action.*

---

## 1. Paper Manuscript & Formatting Verification

| # | Item | Specification / Requirement | Status | Verification / Artifact Location |
|:---|:---|:---|:---|:---|
| **1** | **Compiled PDF** | Clean compilation, 8 pages, 0 errors, 0 undefined citations | `READY` | `paper/phase3-paper/main.pdf` (compiled via `tectonic`) |
| **2** | **LaTeX Source** | Self-contained `.tex` manuscript source | `READY` | `paper/phase3-paper/main.tex` (single-file monolithic source) |
| **3** | **Bibliography** | Complete `.bib` database with 17 verified citations | `READY` | `paper/phase3-paper/references.bib` |
| **4** | **Page Limit Compliance** | CHIL guideline: $\le 10$ pages excluding references. AegisMed: 7.5 content pages + references | `READY` | Verified 8 pages total |
| **5** | **Figure Resolution** | High-resolution publication-quality vector/raster graphics | `READY` | `paper/phase3-paper/figures/` (FIG. 1 architecture, FIG. 2 DEMAT flowchart, FIG. 5 empirical results) |
| **6** | **Empirical Honesty** | Manuscript reports mechanism-only measurements from the self-generated regression suite; no accuracy claim; every number traces to the committed artifact | `READY` | Verified against `data/benchmarks/results/demat_research_benchmark.json` and `data/benchmarks/RETIREMENT.md` |

---

## 2. Double-Blind Review & Anonymization Gate

ACM CHIL and MICCAI enforce strict double-blind peer review.

| Check | Requirement | Current State | Action Required |
|:---|:---|:---|:---|
| **Author Names & Affiliations** | Must not appear in header, title block, or footnotes | Currently lists `Arham Saghir` in camera-ready draft `main.tex` | `BLOCKED: user action` (Toggle to `\author{Anonymous Author(s)}` in `main.tex` before uploading PDF to OpenReview) |
| **Self-Citations** | Third-person phrasing ("In prior work [X], they proposed...", not "In our prior work [X]...") | Formulated neutrally; no identifying prior team publications cited | `VERIFIED` |
| **Repository Links** | Links to code must use anonymous GitHub (e.g., `anonymous.4open.science`) or Zenodo blind repo | Code references in draft point to supplemental zip, not personal GitHub URL | `VERIFIED` |
| **Funding & Acknowledgments** | Grant numbers, university affiliations, and personal thank-yous must be omitted | Acknowledgment section currently omitted from submission draft | `VERIFIED` |

---

## 3. Reproducibility & Open Science Package

| Item | Description | Path in Repository |
|:---|:---|:---|
| **Benchmark Runner** | Complete 2-arm ablation benchmark harness (DEMAT vs. Single-Pass) | `scripts/benchmark/demat_benchmark.py` |
| **Evaluation Metrics** | Shannon entropy, Brier score, ECE, McNemar significance calculator | `scripts/benchmark/metrics.py` |
| **Standardized Dataset** | 200 clinical presentations across 9 medical categories & 15 conditions | `data/benchmark_cases.json` |
| **Committed Results** | Machine-readable benchmark outputs, entropy curves, and test statistics | `data/benchmarks/results/demat_research_benchmark.json` |
| **Deterministic Seed** | Fixed pseudorandom seed for exact replication | `--seed 42` (hardcoded in benchmark script default) |
| **Core Algorithms** | Standalone DEMAT active triage & Dempster-Shafer evidential fusion engine | `src/core/demat.py`, `src/core/disease_kb.py`, `src/core/question_bank.py` |

To generate a standalone ZIP for OpenReview supplementary materials:
```bash
zip -r aegismed_reproducibility_supplement.zip \
  scripts/benchmark/ \
  data/benchmark_cases.json \
  src/core/ \
  paper/phase3-paper/main.pdf
```

---

## 4. Ethical & Clinical Disclaimers Checklist

- [x] **Synthetic / De-Identified Data Statement:** Section 4.1 of manuscript explicitly discloses that evaluations are conducted on standardized clinical vignette benchmarks and that no protected health information (PHI) was accessed without IRB oversight.
- [x] **Clinical Decision Support Framing:** Manuscript repeatedly reinforces that AegisMed provides *decision support and risk bounding for licensed clinicians*, not autonomous medical intervention.
- [x] **Limitations Disclosure:** Section 5.3 explicitly discusses constraints: evaluation on 15 core conditions rather than full 70,000+ ICD-10 ontology, prospective emergency department validation needs, and FHIR interoperability requirements.

---

## 5. Submission Execution Steps for the Human Author

1. **Step 1 (Patent Priority):** Confirm that the provisional patent application has been lodged and an official application number received (see `patent/FILING_CHECKLIST.md`). **Do not upload until priority is secured.**
2. **Step 2 (Blinding):** In `paper/phase3-paper/main.tex`, set author to `Anonymous Author(s)` and remove university address; run `tectonic paper/phase3-paper/main.tex` to re-generate blinded submission PDF.
3. **Step 3 (OpenReview Account):** Log in to the ACM CHIL OpenReview submission portal (or MICCAI equivalent).
4. **Step 4 (Metadata Entry):** Copy Abstract, Keywords, and Subject Areas from `paper/phase3-paper/main.tex`.
5. **Step 5 (Upload):** Upload blinded PDF manuscript and `aegismed_reproducibility_supplement.zip`.
6. **Step 6 (Declaration):** Complete the ACM Reproducibility and Conflict of Interest (COI) disclosures.
