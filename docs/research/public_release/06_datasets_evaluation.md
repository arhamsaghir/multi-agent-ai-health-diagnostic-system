# S6 — Datasets & Evaluation Protocols for Symptom-Based Diagnosis

**Scope:** datasets and evaluation protocols AegisMed can adopt for a credible, non-circular public-release evaluation — symptom→disease corpora, clinical vignette benchmarks, EHR-derived evaluation, triage labels, Indian-context data, vignette-methodology and statistics, LLM-as-judge, and what is usable without IRB.

**Written:** 2026-10-27 · Evidence rules per `README.md` (≥3 independent sources or `WEAK-EVIDENCE`; verbatim quotes with URL + publisher + date; `UNKNOWN` markers).

---

## TL;DR

1. **The 98% top-1 claim must be retired.** The benchmark it comes from is generated from AegisMed's own KB (confirmed in `scripts/benchmark/demat_benchmark.py`: `simulate_patient_answer()` answers DEMAT's questions using the same `DISEASE_DATABASE` likelihoods it is being scored against). The community-standard Kaggle "Disease Symptom Prediction" dataset is **not** a fix: it is of undocumented provenance, unlicensed on Kaggle, massively duplicated, and routinely produces absurd 100% accuracies [1][2][3].
2. **There is a viable credential-free replacement stack.** (a) `gretelai/symptom_to_diagnosis` (853 train / 212 test natural-language symptom descriptions, 22 diagnoses, **Apache 2.0**) [9]; (b) **DxBench** (1,148 real doctor–patient dialogue cases, 461 diseases) [14]; (c) **HealthBench** (5,000 multi-turn conversations, 48,562 physician-written rubric criteria, **MIT license** on the dataset) [18][19] for the report-synthesis stage.
3. **Best-model reality checks:** on DxBench, GPT-4 reaches only **62.5%** top-1 with inquiry (3-candidate setting); open-ended best is **44.2%** [14]. On HealthBench, **o3 scores 60%**, and the Hard subset tops out at **32%** [18]. Symptom checkers audited with vignettes get the right diagnosis first only **~34–36%** of the time (Semigran 2015; Hill 2020) [23][24]. These are the numbers any honest AegisMed claim must be set against — not against a synthetic KB.
4. **MIMIC-IV is reachable without IRB but needs PhysioNet credentialing** (free CITI "Data or Specimens Only Research" training + DUA 1.5.0; typically days-to-weeks of human review) [27][28][29]. It is **not** the right first step for a symptom-level assistant anyway — MIMIC-IV-ED's triage table (ESI 1–5 acuity over ~425k ED visits) is the one MIMIC asset that maps to AegisMed's triage stage [30][31].
5. **Synthea (Apache 2.0) is a defensible way to regenerate risk-model training data** — but must be described as simulation-derived with documented validity limits (Chen 2019 validation study) [33][34][35].
6. **India-specific patient text is the biggest genuine gap:** no public Hindi/Hinglish *clinical* patient-text corpus exists (`WEAK-EVIDENCE`, negative claim after repeated searches); NFHS-5 / ICMR-INDIAB / GBD provide open prevalence priors [39][40][41]; HealthCareMagic-100k-style teleconsult corpora are scraped and license-dirty [44].
7. **A credible claim costs ~250–400 scored vignettes, not 200 synthetic cases:** ±5pp CI at p≈0.7 needs **n≈323** (computed, Cochran formula); a Semigran-style 15/15/15 urgent/low-urgency/non-urgent design with blinded rubric grading and McNemar/bootstrap statistics is the minimum publishable protocol [23][24][25][49].
8. **LLM-as-judge is usable for AegisMed's synthesis reports if calibrated:** GPT-4-class judges reach ~85% agreement with human preference (Zheng 2023) [46], but medical judge–physician agreement is moderate (κ≈0.63 in a diagnostic-eval preprint [47]); the HealthBench pattern — rubric-graded outputs validated against physician consensus — is the safe template [18].

---

## 1. Symptom→disease datasets

### 1.1 Kaggle "Disease Symptom Prediction" (itachi9604) — the field's default, and its problems

- **What it is:** 4,920 rows × ~132–134 symptom columns mapping to **41 diseases**; ships `symptom_severity.csv`, `symptom_precaution.csv`, `symptom_Description.csv` [1].
- **Provenance: none.** The Kaggle page documents no source. The GitHub mirror README says only: *"A dataset created for the purpose of creating a healthcare prediction system"* [2]. Community consensus is that rows were programmatically expanded from a smaller symptom–disease mapping (WebMD-style descriptive text) — no peer-reviewed provenance statement exists [1][2][3].
- **License: UNKNOWN on the canonical distribution.** The Kaggle page shows no license ("Unknown"/other applies); the GitHub mirror attaches **GPL-3.0** to the repo [1][2]. For a public release this is a real redistribution problem: a GPL-3.0 claim over scraped/derived health content is legally messy, and Kaggle's "unknown" is worse.
- **Quality criticisms:** a Kaggle analysis notebook explicitly warns *"Duplicated rows or records will not be dropped from the training dataset in this case"* [3] — consistent with the widely repeated observation that unique symptom patterns were replicated (~120×) to inflate to 4,920 rows. Multiple notebooks report **100% accuracy** with trivial models [4], a textbook signature of a deterministic, information-poor benchmark. A 2025–26 methodological review of symptom-based ML datasets warns that naive benchmark comparisons on such datasets are "misleading due to dataset-specific artifacts" [5]. `WEAK-EVIDENCE` on the exact ~120× duplication figure (community observation; nobody has published the count), strong evidence on the duplication phenomenon itself [3][4][5].
- **Verdict for AegisMed:** usable for smoke-testing the pattern extractor only; never for headline numbers; do not ship in a public repo without a license audit.

### 1.2 Symptom2Disease and its Apache-2.0 derivative (usable today)

- **Symptom2Disease** (Kaggle, niyarrbarman): *"The dataset consists of 1200 datapoints and has two columns: 'label' and 'text'"* — 41 diseases × 30 natural-language patient-perspective symptom descriptions [6]. License not surfaced on the mirror — `UNKNOWN`, verify card. `WEAK-EVIDENCE` on 41-disease count (Kaggle card + one HF mirror only) [6][7].
- **gretelai/symptom_to_diagnosis** (Hugging Face): the same corpus rewritten by an LLM into realistic patient language: *"The data is split to 80% train (853 examples, 167kb) and 20% test (212 examples, 42kb)"*; 22 diagnoses; *"This dataset is licensed Apache 2.0 and free for use."* The card states the data *"was updated using an LLM to create language more consistent with how a patient would describe symptoms."* [8][9]. This is the only symptom-text dataset found with a clean license + explicit synthetic-provenance disclosure.
- **Diseases-and-symptoms-dataset (dhivyeshrk)**: 773 diseases × 377 symptoms (~5k records), also a Kaggle community compile; same undocumented-provenance caveats [10]. `WEAK-EVIDENCE` on exact counts (single Kaggle card + one Scribd-derived description).

### 1.3 DXY/丁香园-derived Chinese corpora (large, but license-dirty)

- **MedDialog (Chinese)**: *"contains conversations (in Chinese) between doctors and patients. It has 1.1 million dialogues and 4 million utterances"* (OpenDataLab; original EMNLP paper) [11][12].
- **cMedQA2**: Chinese community medical QA (SJTU), hosted on Tianchi (dataset 90188) and GitHub (ZhangShanhai/cMedQA2) [12].
- **Chinese-medical-dialogue** (6-department QA, ~793k pairs; sources include DXY/丁香园, 春雨医生, 好大夫在线) [12]. A disease–symptom knowledge graph built from ~270,000 EMRs circulates via the Yb-Z/Chinese_medical_NLP aggregator [12].
- All are scraped from commercial consultation platforms; none carries a clean commercial-use license. For AegisMed they are useful **as evaluation cases** (research use) and as the source from which DxBench was built (§2.2). `UNKNOWN — how to find out: write to dataset maintainers (cMedQA2/_meddialog_) for redistribution terms before any public release that includes derived rows.`

### 1.4 SymCat-derived data

SymCat (symcat.com) was a "disease calculator" over aggregated patient records; the site is defunct and scraped derivatives carry no license. The NLICE paper (arXiv:2401.13756) built **5M synthetic triage records covering 801 conditions and 376 symptoms** from SymCat's symptom–disease mappings [13]. Useful as prior art for synthetic-record generation methodology; not safe to redistribute.

### 1.5 "Muzna" symptom-disease datasets

Repeated targeted searches (Kaggle, Hugging Face, GitHub) found **no** dataset attributable to a "Muzna" author — the closest matches are Symptom2Disease [6] and SympScan (200+ symptoms → 100+ diseases, Kaggle behzadhasan) [10]. **UNKNOWN — how to find out: if the team encountered a specific Kaggle URL, archive it; otherwise treat the "Muzna dataset" as folklore and use Symptom2Disease/gretelai instead.**

### 1.6 2023–2026 additions

- **Bangla disease–symptom dataset** (arXiv:2506.13610, 2025): structured disease–symptom pairs compiled from public sources with a documented methodology — notable as one of the few recent low-resource symptom corpora with a paper [10].
- **Healthcare Symptoms–Disease Classification** (Kaggle kundanbedmutha): 25,000 *synthetic* records, 30 diseases, explicitly labeled synthetic [10] — safe to redistribute only if its card confirms license; check before use.

---

## 2. Clinical vignette corpora and diagnostic benchmarks

### 2.1 NEJM CPC / case-record-derived corpora

- The **70 postmortem Clinicopathological Conference (CPC) vignettes** from NEJM are the de-facto "hard cases" corpus: Goh et al. randomized **50 physicians** to solve them with/without GPT-4; *"median diagnostic reasoning score per case was 76% (IQR, 66%–87%) for the LLM group and 74%"* for conventional resources (adjusted difference 2 pp, 95% CI −4 to 8, P=.60), while **LLM alone scored 92% (IQR, 82%–97%)** [15][16]. Grading used a structured multi-domain rubric with two blinded physician scorers and consensus adjudication of >10-point disagreements [16].
- **AgentClinic** (arXiv:2405.07960, 2024): multimodal benchmark with simulated patient/doctor agents; some vignettes derived from NEJM case records [17]. Preprint; license on GitHub (blueonion/AgentClinic) should be checked before adopting.

### 2.2 DxBench (FreedomIntelligence, 2024) — real-dialogue diagnosis benchmark

Fetched verbatim from the Chain-of-Diagnosis paper (arXiv:2407.13301v2): DxBench contains *"over 1,000 real cases, covering 461 disease types from 15 departments and 5,038 symptoms"* — precisely **1,148 test cases** built from MedDialog doctor–patient dialogues (3,121 filtered → GPT-4 structuring → manual refinement), each case offering **three candidate diseases** (one ground truth). Reported accuracies: **GPT-4 62.5% with inquiry (60.1% without)**; DiagnosisGPT-13B **64.5%** (τ=0.6, 3.1 inquiry rounds); **44.2%** in the fully open-ended (no candidates) setting [14]. This is the single most relevant *external* benchmark for a symptom→diagnosis system, and it is derived from public dialogues (§1.3 license caveats apply to the rows themselves; running AegisMed against it for internal scoring is research use).

### 2.3 DxGPT (SJD Barcelona)

Hospital Sant Joan de Déu's DxGPT study (medRxiv 2024, preprint — not peer-reviewed): on real pediatric cases, *"clinicians achieved 65% top-5 diagnostic accuracy vs. 60% for DxGPT"* — no statistically significant difference [20][21]. `WEAK-EVIDENCE` (two sources, both preprint-adjacent). The value for AegisMed is the **protocol**: top-5 differential vs. clinician panel, speed comparison, named-disease scoring — replicable without credentialing since cases were authored, not extracted.

### 2.4 MedQA / PubMedQA (exam-style; report-only baselines, not symptom evals)

- **MedQA (USMLE)**: ~12,723 English questions collected from professional medical board exams; **MIT license** on the canonical mirrors [22][23-sources: openmedlab, Kaggle evidence/medqa-usmle, HF GBaker/MedQA-USMLE-4-options].
- **PubMedQA**: 2,733 labeled yes/no/maybe questions over PubMed abstracts (plus 61.2k unlabeled, 211.3k artificial); MIT-licensed HF distribution [24][25].
- These are **not symptom-checker evaluations** (they test exam QA), but including them situates AegisMed in the literature and costs nothing.

### 2.5 OpenAI HealthBench (May 2025) — the template for grading *reports*

Fetched verbatim from the arXiv abstract (2505.08775): *"HealthBench consists of 5,000 multi-turn conversations between a model and an individual user or healthcare professional"* with *"48,562 unique rubric criteria spanning several health contexts"* created by **262 physicians** (60 countries per OpenAI's announcement and secondary coverage) [18][19][26]. Scoring is rubric-based: each criterion carries weighted points, including **negative points for dangerous errors** (e.g., a rubric item advising vasopressin instead of epinephrine scores −6) [19]. Two special subsets, reported as ~1,000 conversations each (`WEAK-EVIDENCE` on exact size — two secondary sources): **HealthBench Hard** (*"the current top score is 32%"*) and **HealthBench Consensus** (*"34 particularly important dimensions of model behavior validated via physician consensus"*) [18]. Performance anchors: *"GPT-3.5 Turbo's 16% to GPT-4o's 32%"*; *"o3 scores 60%"* [18]. **Dataset license: MIT** (Hugging Face `openai/healthbench` card) [19].

### 2.6 A correction on scope note "Arc Institute's Virtual Lab"

The Virtual Lab (Arc Institute/Stanford, *Nature*, 2025-07-29, doi:10.1038/s41586-025-09442-9) is a **multi-agent scientific discovery system** (PI/immunologist/ML/computational-biologist/critic agents holding "research meetings"; designed 92 SARS-CoV-2 nanobodies, 2 experimentally validated) — **not a diagnostic benchmark** [26a]. It is relevant to AegisMed only as an agentic-architecture prior art reference (S11), not as an evaluation corpus. The consumer-diagnosis benchmark from 2025 is HealthBench [18].

### 2.7 MIMIC-derived vignette benchmarks

- **CliBench** / **MedAgentBench** / ED-specific benchmarks built from MIMIC-IV(-ED) records for multifaceted clinical decision evaluation [17a][17b]. All inherit PhysioNet credentialing (§3.1) — the *benchmark code* is public, but reproducing the data requires access.

---

## 3. EHR-derived evaluation

### 3.1 MIMIC-III/IV — credentialing reality

- **Access = PhysioNet credentialed health data, not open data.** Requirements: registered PhysioNet account; completion of **CITI "Data or Specimens Only Research"** training (free; covers human-subjects protection + HIPAA); endorsement (supervisor for trainees); signature of the **PhysioNet Credentialed Health Data Use Agreement 1.5.0** (no re-identification, research-only, data security) [27][28][29]. Cost: **free**. Timeline: human committee review; community reports range *"~1–3 business days to about a week"* for complete applications (`WEAK-EVIDENCE`; no official SLA — UNKNOWN official timeline) [29].
- **IRB:** individual use of the de-identified MIMIC-IV under the DUA does not itself require IRB (the data are already limited-data released for research); *institutional* policies vary, and any re-contact/prospective component absolutely does require IRB. `UNKNOWN — how to find out: ask the host institution's IRB whether PhysioNet-credentialed use of pre-de-identified data qualifies as non-human-subjects research under their policy.`
- **What AegisMed can/cannot do with it:** MIMIC-IV is ICU/inpatient data — wrong unit of analysis for a consumer symptom assistant. The exception is **MIMIC-IV-ED** (§4.1).

### 3.2 eICU-CRD and HiRID

- **eICU**: same credentialed-access model; *"Once approved, data can be directly downloaded from the eICU Collaborative Research Database project on PhysioNet"*; a **free demo (eICU-CRD Demo 2.0.1)** is available without credentialing [29a][29b]. Not symptom-level.
- **HiRID**: ~33,000–34,000 ICU admissions (Bern University Hospital), high time-resolution; PhysioNet credentialed access **plus contributor approval** (separate DUA) [29c][29d]. The HiRID-III benchmark release lives on GitHub/Zenodo — check its license there. Not symptom-level.

### 3.3 Synthea — the legitimate synthetic-EHR route

- **License: Apache 2.0**, software and generated data; maintainers confirm generated data are *"realistic but not real"* and *"free from cost, privacy, and security restrictions"* [33][34].
- **Validation study:** Chen et al. 2019 (*The validity of synthetic clinical data*, ~183 citations) found *"Synthea is quite reliable in modeling demographics and probabilities of services"* but with documented caveats [34][35].
- **Known limits:** rule-based modules mean only authored diseases appear with limited interactions; data are "too clean" (no transcription noise, unnatural missingness); birth-to-death simulation biases some outcome models [35][36][37]. Consequence for AegisMed: Synthea is a legitimate **training-data generator for the risk models** (replacing the in-house 500-record generator) and a pipeline-test corpus, but claims from it must be labeled simulation-derived and externally validated.

---

## 4. Triage / urgency labels

### 4.1 MIMIC-IV-ED triage table (the best record-level urgency corpus)

- **~425,000 ED visits** (Beth Israel Deaconess, 2011–2019); the `triage` table records, per the MIT-LCP documentation, **`acuity` — "an ordinal triage acuity level (1 = highest urgency / most acute, down to 5 = lowest urgency)", corresponding to the Emergency Severity Index (ESI)** — plus chief complaint, vitals, pain [30][31][32]. Access = PhysioNet credentialing (§3.1). This is the only large, record-level, publicly obtainable symptom-chief-complaint → urgency corpus, and the ESI 1–5 labels are exactly what AegisMed's triage stage should be scored against.

### 4.2 Manchester Triage System (MTS)

No public record-level MTS-coded dataset exists; MTS ML studies use private hospital data (multicentre reproducibility studies, MTS-vs-ESI comparison papers) [38]. `WEAK-EVIDENCE` (negative claim — three independent searches found only institutional/private MTS datasets). Implication: if AegisMed's triage output is mapped to MTS-like categories, it must be validated by **physician/expert-panel vignette grading**, not by an open dataset.

### 4.3 NHS Pathways / NHS 111 Online

Published by NHS Digital as **open data (weekly XLSX releases)**: counts of triaged contacts by pathway (symptom group) and **disposition** (ambulance / ED / primary care / self-care), by region/age/sex [39a][39b]. Aggregate counts only — useful for calibrating AegisMed's triage-distribution priors, **not** for supervised training. License: NHS open data (OGL-style; verify per-release).

---

## 5. Indian-context data

### 5.1 Prevalence priors (open)

- **NFHS-5 (2019–21)**: microdata via DHS Program (free registration) and World Bank Microdata Library (catalog 4482); district/state indicators for anemia, hypertension, blood glucose, NCD risk factors [40][41].
- **ICMR**: India State-Level Disease Burden Initiative (ICMR–PHFI–IHME, Lancet-published) with **open GBD-based state-level estimates** via IHME's data tools; ICMR-NHRDR hosts open cardiovascular risk-factor datasets; ICMR-INDIAB (Lancet Diabetes & Endocrinology) for diabetes prevalence [41][42].
- Use for AegisMed: **prevalence-weighted calibration of priors** (e.g., entropy-triage base rates for the 15 conditions) and honest demographic framing of claims — not as case corpora.

### 5.2 Hindi/Hinglish patient text — a genuine gap

- **No public Hindi/Hinglish *clinical* patient-text dataset was found** after multiple targeted searches (`WEAK-EVIDENCE`, negative claim). Closest assets: **COMI-LINGUA** (2025, arXiv:2503.21670, expert-annotated Hindi–English code-mixed multitask NLP), the 55k Hinglish sentiment Kaggle corpus, AI4Bharat's IndicNLP corpora (2.7B words, 10 languages — general domain) [43]. None is clinical.
- **UNKNOWN — how to find out: (a) ICMR/DBT data-sharing portals for telemedicine research corpora; (b) eSanjeevani (national telemedicine service) research partnerships; (c) construct one: have bilingual annotators Hinglish-ify the 212 gretelai test vignettes, release under CC0 with a documented protocol — that would be a citable contribution in itself.**

### 5.3 Telemedicine transcripts

- **ChatDoctor / HealthCareMagic-100k**: *"100k real patient–doctor conversations"* scraped from HealthCareMagic.com covering 700+ diseases (arXiv:2303.14070), plus ~200k iCliniq-derived conversations; mirrored on HF (`lavita/ChatDoctor-HealthCareMagic-100k`) [44]. **License: UNKNOWN/formally absent** — scraped user-generated content; mirrors are "research purposes only". Never ship in the public repo; usable as internal eval/steering data at most, with provenance disclosed.
- **MedDialog (English)** (~250k consultations) — same caveat family [11].

---

## 6. Evaluation-protocol design for consumer symptom checkers

### 6.1 The vignette playbook (Semigran → Hill → Hammoud → Goh)

- **Semigran et al., BMJ 2015** (the canonical audit): **45 standardized vignettes** (15 urgent / 15 low-urgency / 15 non-urgent), **23 symptom checkers**, **770 evaluations**; correct diagnosis in top-20 **58%**, top-1 **34%**; appropriate triage **57%**; in ~80% of urgent cases triage advice was incorrect [23][24-of-2015-coverage][45]. Scores were set by a physician panel before running; every checker received identical inputs.
- **Hill et al., MJA 2020** (note: MJA, not BMJ): **36 symptom checkers**, 27 vignettes → **1,170 diagnostic vignette tests + 688 triage tests**; correct diagnosis first **36%** (421/1,170), top-3 **~52%** (606/1,170) [24].
- **Hammoud et al., JMIR AI 2024** (fetched): the modernized methodology — *"we developed and peer-reviewed 400 vignettes, each approved by at least 5 out of 7 independent and experienced primary care physicians"* (supermajority gate), vignettes drawn from USMLE Step 2 CK / MRCP / ABFM / ABP material; seven metrics (M1/M3/M5, recall, precision, F1, NDCG); three physicians per checker; three senior physicians blinded gold-standard comparison. Best checker's M1 67.5% vs doctors' 61.2%. **Caveat: all authors are Avey Inc employees — treat magnitudes with suspicion, copy the method** [25].
- **El-Osta et al., BMJ 2022**: documented failure modes of vignette testing (fixed inputs, no follow-up questions) — motivates interactive/adaptive testing, which is exactly AegisMed's DEMAT differentiator and must be evaluated *interactively* (scripted patient turns), not single-pass [45a].
- **Goh et al., JAMA Netw Open 2024**: rubric-based **Diagnostic Reasoning Score (0–10)**, two blinded physician scorers, consensus adjudication — the model for grading AegisMed's *report text* rather than just top-1 labels [15][16].

### 6.2 Statistics and sample size

- **Proportion CIs (Cochran/Wilson, computed 2026-10-27):** for 95% CI half-width ±5pp: n = 1.96²·p(1−p)/0.05² → **p=0.5: n=385; p=0.7: n=323; p=0.8: n=246; p=0.9: n=139**. For ±3pp: 1,068 / 768(p=.7) / 683 / 385. So a credible "top-1 ≈70% ±5%" claim needs **~325 scored cases**; a "≈90% ±5%" claim needs ~140. AegisMed's 200 synthetic cases are both circular *and* underpowered for a ±5pp claim at anything below p≈0.9.
- **Paired system comparison (DEMAT vs ablation)**: McNemar's test on discordant pairs is the standard; power depends on the discordance rate, so a 5pp difference at 80% power generally needs **several hundred cases** (or an exact McNemar on ≥300 cases; simulate power from pilot discordance rather than trusting closed-form shortcuts). Report **bootstrap CIs (≥10k resamples, case-level)** alongside every headline number — this is now table stakes in ML-health venues and in the benchmark papers above [14][15][25].
- **Preregistration:** OSF prereg of hypotheses, vignette set, primary metric, and analysis plan before scoring; report per **DECIDE-AI** (17 AI-specific items for early-stage clinical evaluation of decision-support systems, BMJ 2022) and, for model-development claims, **TRIPOD+AI** (EQUATOR) [46a][46b]. This costs nothing and is what separates a CHIL-publishable eval from a demo.

---

## 7. Decision table — dataset × access barrier × usable-for-what

| Dataset | Access barrier | Without IRB? | License cleanliness | Usable for |
|---|---|---|---|---|
| Kaggle Disease Symptom Prediction [1][2] | None (download) | Yes | **Dirty** — no license on Kaggle; GPL-3.0 on mirror; no provenance | Smoke tests only; never headline claims |
| Symptom2Disease [6] | None | Yes | UNKNOWN | Internal pattern-extractor tuning |
| gretelai/symptom_to_diagnosis [9] | None | Yes | **Clean (Apache 2.0)** | **Primary held-out NLP eval; public reporting** |
| DxBench [14] | None (GitHub/arXiv release; verify redistribution) | Yes | Research-grade (MedDialog-derived) | **External diagnosis benchmark; headline top-1/top-3** |
| HealthBench [18][19] | None | Yes | **Clean (MIT)** | **Rubric-graded eval of report synthesis; emergency-referral safety** |
| MedQA / PubMedQA [22][24] | None | Yes | MIT | Literature-positioning baselines |
| NEJM CPC 70-vignette set [15][16] | None (published in paper/PMC) | Yes | Journal copyright — use for internal scoring, don't redistribute | Hard-case eval; rubric grading practice |
| AgentClinic [17] | None | Yes | Preprint/GitHub — verify | Interactive agentic eval design reference |
| MIMIC-IV / MIMIC-IV-ED [27][28][30][31] | PhysioNet credentialing (CITI + DUA; free; days–weeks) | Yes, for de-identified DUA use (institution-dependent) | Clean for research under DUA | ESI 1–5 triage scoring; chief-complaint→disposition; **not** symptom-level dx eval |
| eICU / HiRID [29a][29c] | Credentialing (+ HiRID contributor approval) | Same as above | Clean under DUAs | Not applicable to symptom triage |
| Synthea [33][34] | None | Yes | **Clean (Apache 2.0)** | **Regenerating risk-model training data; pipeline tests** (label as synthetic) |
| NHS Pathways open data [39a][39b] | None | Yes | Open (OGL-style) | Triage-distribution priors (aggregate only) |
| NFHS-5 / GBD / ICMR-INDIAB [40][41][42] | Free registration (DHS) / open (GBD) | Yes | Open | Prevalence-weighted priors; India framing |
| ChatDoctor/HCM-100k, MedDialog [11][44] | None | Yes | **Dirty** (scraped; research-only) | Internal only; provenance disclosed; never shipped |
| COMI-LINGUA / Hinglish corpora [43] | None | Yes | Verify per card | Coarse Hinglish robustness probes; **not** clinical eval |
| Semigran/Hill vignette designs [23][24] | None (published methods) | Yes | n/a (methodology) | **Template for a physician-graded vignette study** |
| Real patients (prospective) | — | **No — needs IRB** | — | Only for the eventual DECIDE-AI stage-2/3 live evaluation |

**The bright line:** everything above the "Real patients" row can be executed **today, without IRB**; anything involving real patients, re-identification, or prospective interaction needs the (already drafted) IRB protocol.

---

## 8. LLM-as-judge for diagnosis reports

- **General calibration:** Zheng et al. 2023 (MT-Bench): GPT-4-as-judge agrees with human preference **85%** (non-tie, S2 setting) vs **~81% human–human** — the first judge to match human consistency; GPT-3.5-class judges fall to ~66% [46]. Position-bias mitigation (swap order, average) is standard and should be replicated.
- **Medical-specific agreement:** a JMIR preprint on ChatGPT-4 identifying final diagnoses reports **Cohen's κ = 0.63 (95% CI 0.56–0.69)** vs physicians — "fair to good" agreement [47] (`WEAK-EVIDENCE`, single preprint). Croxford et al. 2025 (medRxiv) found medical LLM judges concordant on faithfulness/completeness-type rubric criteria but weaker on interpretive criteria [48] (`WEAK-EVIDENCE`).
- **The operating conclusion for AegisMed:** use an LLM judge **only** over atomic, verifiable rubric items (HealthBench-style: accuracy facts, must-ask questions, red-flag escalations with negative points) [18][19], *and* calibrate it against ≥2 physicians on a 20–30-case subset, reporting κ (target ≥0.6, consistent with κ≈0.63 medical agreement literature [47]) before reporting any judge-derived score. A JAMA systematic review notes only ~5% of healthcare LLM evaluations use real patient care data [49] (`WEAK-EVIDENCE`) — a physician-calibrated rubric eval would put AegisMed above the field's norm.

---

## Sources

1. Kaggle — *Disease Symptom Prediction* (itachi9604). https://www.kaggle.com/datasets/itachi9604/disease-symptom-description-dataset (fetched 2026-10-27 via search; page is JS-gated). Reported: 4,920 rows, 41 diseases, Symptom_1..17 + severity/precaution/description files; no license displayed.
2. GitHub — itachi9604/Disease-Symptom-dataset (fetched 2026-10-27). README verbatim: *"A dataset created for the purpose of creating a healthcare prediction system."* Repo license: GPL-3.0. No provenance or citation requirement stated.
3. Kaggle notebook — annelieseneo/disease-prediction. Verbatim (via search snippet): *"Duplicated rows or records will not be dropped from the training dataset in this case."* https://www.kaggle.com/code/annelieseneo/disease-prediction (accessed 2026-10-27).
4. Scribd — *Disease Prediction Based on Symptoms Using Machine Learning* presentation: Random Forest achieves 100% accuracy on the dataset. https://www.scribd.com/presentation/854363352/Disease-Prediction-Presentation (accessed 2026-10-27). Also multiple Kaggle notebooks with 100% results.
5. *Context matters in machine learning based disease prediction* (2025). https://pmc.ncbi.nlm.nih.gov/articles/PMC12663224 (accessed 2026-10-27 via search). Symptom-based dataset comparisons can be misleading due to dataset-specific artifacts.
6. Kaggle — *Symptom2Disease* (niyarrbarman). Verbatim (via search snippet): *"The dataset consists of 1200 datapoints and has two columns: 'label' and 'text'."* https://www.kaggle.com/datasets/niyarrbarman/symptom2disease (accessed 2026-10-27).
7. Hugging Face — seokochin/Symptom2Disease mirror. https://huggingface.co/seokochin/Symptom2Disease (accessed 2026-10-27).
8. Kaggle — *Diseases and Symptoms Dataset* (dhivyeshrk): 773 diseases, 377 symptoms; *Healthcare Symptoms–Disease Classification* (kundanbedmutha): 25,000 synthetic records, 30 diseases; *SympScan* (behzadhasan). URLs in text. (accessed 2026-10-27)
9. Hugging Face — gretelai/symptom_to_diagnosis (fetched 2026-10-27). Verbatim: *"The data is split to 80% train (853 examples, 167kb) and 20% test (212 examples, 42kb)"*; *"This dataset is licensed Apache 2.0 and free for use."*; data *"was updated using an LLM to create language more consistent with how a patient would describe symptoms"*; adapted from Kaggle Symptom2Disease. https://huggingface.co/datasets/gretelai/symptom_to_diagnosis
10. arXiv — *A Structured Bangla Dataset of Disease-Symptom* (2025), arXiv:2506.13610. https://www.arxiv.org/pdf/2506.13610v1 (accessed 2026-10-27 via search).
11. OpenDataLab — *MedDialog (Chinese)*: *"1.1 million dialogues and 4 million utterances"*. https://opendatalab.com/OpenDataLab/MedDialog (accessed 2026-10-27 via search).
12. GitHub aggregators — ZhanShanhai/cMedQA2; Tianchi dataset 90188; Yb-Z/Chinese_medical_NLP (disease–symptom KG from ~270k EMRs); Chinese-medical-dialogue 6-department set (DXY/春雨/好大夫-derived). (accessed 2026-10-27 via search)
13. arXiv — *NLICE: Synthetic Medical Record Generation for Effective Primary Care Triage* (2024), arXiv:2401.13756: 5M synthetic records, 801 conditions, 376 symptoms from SymCat mappings. https://arxiv.org/html/2401.13756v1 (accessed 2026-10-27 via search).
14. arXiv — *CoD: Towards an Interpretable Medical Agent using Chain-of-Diagnosis* (2024), arXiv:2407.13301v2 (fetched 2026-10-27). Verbatim: *"over 1,000 real cases, covering 461 disease types from 15 departments and 5,038 symptoms"*; 1,148 test cases; GPT-4 **62.5%** with inquiry; DiagnosisGPT **64.5%**; open-ended best **44.2%**. https://arxiv.org/html/2407.13301v2
15. JAMA Network Open — Goh E, et al. *Large Language Model Influence on Diagnostic Reasoning: A Randomized Clinical Trial.* 2024;7(10):e2440969 (pub 2024-10-28). https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2825395 (accessed via search 2026-10-27).
16. PMC11519755 (fetched 2026-10-27). Verbatim: *"Fifty physicians (26 attendings, 24 residents…)"*; *"median diagnostic reasoning score per case was 76% (IQR, 66%–87%) for the LLM group and 74%"* (conventional; adjusted difference 2 pp, 95% CI −4 to 8, P=.60); LLM alone *"92% (IQR, 82%–97%)"* (95% CI 2–30, P=.03); two blinded scorers, consensus for >10% disagreements; 70 postmortem CPC vignettes (per trial registration/abstract). https://pmc.ncbi.nlm.nih.gov/articles/PMC11519755/
17. arXiv — *AgentClinic: a multimodal agent benchmark to evaluate AI in simulated clinical environments* (2024), arXiv:2405.07960; some vignettes derived from NEJM case records. https://papers.cool/arxiv/2405.07960 (accessed 2026-10-27 via search).
18. arXiv — OpenAI, *HealthBench* (2025), arXiv:2505.08775 (submitted 2025-05-13; fetched 2026-10-27). Verbatim: *"HealthBench consists of 5,000 multi-turn conversations…"*; *"48,562 unique rubric criteria"*; *"conversation-specific rubrics created by 262 physicians"*; *"34 particularly important dimensions of model behavior validated via physician consensus"*; *"HealthBench Hard, where the current top score is 32%"*; *"GPT-3.5 Turbo's 16% to GPT-4o's 32%"*; *"o3 scores 60%"*. https://arxiv.org/abs/2505.08775
19. Hugging Face — openai/healthbench dataset card (fetched 2026-10-27): License **MIT**; per-example rubric items with point weights incl. negative points (e.g., −6 for vasopressin-replaces-epinephrine error); theme tags incl. `emergency_referrals`. https://huggingface.co/datasets/openai/healthbench
20. medRxiv — *Evaluation of the Clinical Utility of DxGPT, a GPT-4 Based Large Language Model* (Hospital Sant Joan de Déu, 2024): clinicians **65%** vs DxGPT **60%** top-5 (NS). https://www.medrxiv.org/content/10.1101/2024.07.23.24310847v2.full.pdf (accessed 2026-10-27 via search).
21. ResearchGate mirror of same study. https://www.researchgate.net/publication/382616296 (accessed 2026-10-27).
22. MedQA: openmedlab/Awesome-Medical-Dataset (MIT; ~12,723 EN USMLE questions) https://github.com/openmedlab/Awesome-Medical-Dataset/blob/main/resources/MedQA.md; Kaggle evidence/medqa-usmle (MIT); HF GBaker/MedQA-USMLE-4-options. (accessed 2026-10-27)
23. BMJ — Semigran HL, Linder JA, Gidengil C, Mehrotra A. *Evaluation of symptom checkers for self diagnosis and triage: audit study.* BMJ 2015;351:h3480: 23 checkers, 45 vignettes (15/15/15), 770 evaluations; top-20 58%, top-1 34%, triage 57%. Full text PDF: https://media.wbur.org/wp/2015/07/BMJ-Embargoed-Symptom-Checker-study.pdf ; coverage: https://www.mobihealthnews.com/news/bmj-symptom-checkers-get-diagnosis-right-34-percent-time-average (2015-07-13). (accessed 2026-10-27)
24. MJA — Hill MG, Sim M, Mills B. *The quality of diagnosis and triage advice provided by free online symptom checkers and apps in Australia.* Med J Aust 2020;212(11):514–519: 36 checkers, 27 vignettes, 1,170 diagnostic + 688 triage tests; top-1 36% (421/1,170), top-3 52% (606/1,170). https://www.mja.com.au/journal/2020/212/11/ (accessed 2026-10-27 via search).
25. PMC — Hammoud M, et al. *Evaluating the Diagnostic Performance of Symptom Checkers: Clinical Vignette Study.* JMIR AI 2024 (pub 2024-04-29; fetched 2026-10-27). Verbatim: *"we developed and peer-reviewed 400 vignettes, each approved by at least 5 out of 7 independent and experienced primary care physicians"*; vignettes from *"USMLE, Step 2 CK, Membership of the Royal Colleges of Physicians Part 1… American Board of Family Medicine, and American Board of Pediatrics"*; Avey M1 67.5% vs doctors 61.2%; COI: all authors Avey Inc employees. https://pmc.ncbi.nlm.nih.gov/articles/PMC11091811/
26. OpenAI — *Introducing HealthBench* (2025-05-12): 5,000 conversations, custom physician rubrics, 262 physicians across 60 countries. https://openai.com/index/healthbench (page 403 to fetch; numbers corroborated by arXiv [18] and Fierce Healthcare https://www.fiercehealthcare.com/ai-and-machine-learning/openai-pushes-further-healthcare-release-healthbench-evaluate-ai-models).
26a. Nature — Swanson K, et al. *The Virtual Lab: AI agents design new SARS-CoV-2 nanobodies.* Nature (2025-07-29), doi:10.1038/s41586-025-09442-9: PI + specialist agents, research meetings, 92 nanobodies, 2 validated. https://www.nature.com/articles/s41586-025-09442-9 (accessed via search 2026-10-27).
27. PhysioNet — *Requirement for credentialing*: CITI training + DUA. https://physionet.org/about/database/requirement-for-credentialing/ (accessed 2026-10-27 via search).
28. PhysioNet — MIMIC-IV *view-required-training* ("Data or Specimens Only Research") and *view-dua* (Credentialed Health Data Use Agreement 1.5.0). https://physionet.org/content/mimiciv/view-required-training/ ; https://physionet.org/content/mimiciv/view-dua/ (accessed 2026-10-27 via search).
29. PhysioNet credentialing process (DBDC) community timeline ~days-to-a-week; `WEAK-EVIDENCE`. https://physionet.org (accessed 2026-10-27 via search).
29a. GitHub — MIT-LCP/eicu-data-paper: verbatim *"Once approved, data can be directly downloaded from the eICU Collaborative Research Database project on PhysioNet."* https://github.com/MIT-LCP/eicu-data-paper/blob/master/main.tex (accessed 2026-10-27 via search).
29b. PhysioNet — eICU-CRD Demo 2.0.1 (no credentialing required). https://physionet.org/content/eicu-crd-demo/ (accessed 2026-10-27 via search).
29c. PhysioNet — HiRID, a high time-resolution ICU dataset (v1.1.1; ~33–34k Bern ICU admissions; contributor approval + DUA). https://physionet.org/content/hirid/ ; ricu JSS paper: "almost 34,000 admissions". (accessed 2026-10-27 via search)
30. PhysioNet — MIMIC-IV-ED (~425,000 ED visits, BIDMC 2011–2019; credentialed access). https://physionet.org/content/mimic-iv-ed/ (accessed 2026-10-27 via search).
31. GitHub — MIT-LCP/mimic-iv-website, `ed/triage.md`: verbatim *"acuity — an ordinal triage acuity level (1 = highest urgency / most acute, down to 5 = lowest urgency)"* (ESI at BIDMC); chief complaint, vitals, pain. https://github.com/MIT-LCP/mimic-iv-website/blob/master/content/ed/triage.md (accessed 2026-10-27 via search).
32. ResearchGate — *Assessing Different Diagnoses in MIMIC-IV v2.2 and MIMIC-IV-ED Datasets* (2024). https://www.researchgate.net/publication/377474801 (accessed 2026-10-27).
33. GitHub — synthetichealth/synthea discussions #1167 (Apache 2.0; generated data free of cost/privacy/security restrictions) and #1445 (simulation-bias caveats). https://github.com/synthetichealth/synthea/discussions/1167 (accessed 2026-10-27 via search).
34. PubMed/PMC — Chen J, et al. *The validity of synthetic clinical data: a validation study of a leading synthetic data generator (Synthea)* (2019; PMID 30871520; ~183 citations): *"Synthea is quite reliable in modeling demographics and probabilities of services."* https://pmc.ncbi.nlm.nih.gov/articles/PMC6416981/ (accessed 2026-10-27 via search).
35. OHDSI 2024 — Wagner & Blacketer, *Evaluating Synthea*: reliability limits without adjustment. https://www.ohdsi.org/wp-content/uploads/2024/10/41-Wagner-Evaluating_Synthea-Clair-Blacketer.pdf (accessed 2026-10-27 via search).
36. Schiff S, 2018 — enrichment of synthesized relational data (realism limits + mitigation). https://www.sciencedirect.com/science/article/pii/S1877050918317794 (accessed 2026-10-27).
37. Healthcare IT Today (2017) — Synthea builds patients from CDC statistics + rule-based modules. https://www.healthcareittoday.com/2017/09/13/open-source-tool-offers-synthetic-patients-for-hospital-big-data-projects (accessed 2026-10-27).
38. MTS literature — comparative MTS-vs-ESI evaluation (2025) https://www.researchgate.net/publication/397925788 ; UEA multicentre MTS reproducibility study; r/datasets thread (2024) confirming no public record-level MTS dataset. (accessed 2026-10-27 via search)
39a. NHS Digital — *NHS Pathways and 111 Online Potential COVID-19 Open Data Descriptions* (weekly XLSX, e.g. WE 2022-04-17): triaged contacts by pathway × disposition. https://files.digital.nhs.uk/3C/3EA99E/... (accessed 2026-10-27 via search).
39b. NHS Digital analytics catalogue. https://nhsdigital.github.io/data-analytics-services (accessed 2026-10-27).
40. World Bank Microdata Library — NFHS-5 2019–21 microdata (catalog 4482); DHS Program dataset download (free registration); IIPS rchiips.org. https://microdata.worldbank.org/index.php/catalog/4482 (accessed 2026-10-27).
41. ICMR — India State-Level Disease Burden Initiative (ICMR–PHFI–IHME; Lancet); IHME GBD results/data visualizations (open). https://www.healthdata.org/results/data-visualizations ; ICMR-NHRDR open datasets https://nhrdr.icmr.org.in/datasets/ ; ICMR-NICHR appendix https://nichr.icmr.org.in/appendix (accessed 2026-10-27).
42. ICMR-INDIAB (Lancet Diabetes & Endocrinology) — India diabetes/NCD prevalence. (accessed 2026-10-27 via search)
43. COMI-LINGUA (2025), arXiv:2503.21670 (Hindi-English code-mixed multitask annotated dataset); Kaggle Hinglish 55k; AI4Bharat IndicNLP corpus (2.7B words, 10 languages) https://ai4bharat.iitm.ac.in/ (accessed 2026-10-27). No clinical Hinglish corpus found.
44. GitHub — Kent0n-Li/ChatDoctor (arXiv:2303.14070): *"100k real patient–doctor conversations"* (HealthCareMagic.com), 700+ diseases; HF mirror lavita/ChatDoctor-HealthCareMagic-100k; license UNKNOWN (scraped content, research-only). (accessed 2026-10-27)
45. Wallace W, et al. *The diagnostic and triage accuracy of digital and online symptom checker tools: a systematic review.* npj Digital Medicine 5, 118 (2022): diagnostic and triage accuracy "generally low" across 45 studies; AHRQ PSNet summary https://psnet.ahrq.gov/issue/diagnostic-and-triage-accuracy-digital-and-online-symptom-checker-tools-systematic-review ; MobiHealthNews 2022-08-29. Exact pooled percentages unverifiable from fetched pages — `WEAK-EVIDENCE` on precise figures. (accessed 2026-10-27)
45a. BMJ/Imperial — El-Osta A, et al. *What is the suitability of clinical vignettes in benchmarking the performance of online symptom checkers?* (2022). https://spiral.imperial.ac.uk/server/api/core/bitstreams/80754c16-d136-4bf5-9365-0386a7081c54/content (accessed 2026-10-27 via search).
46. NeurIPS 2023 — Zheng L, et al. *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*: GPT-4–human agreement 85% (non-tie) vs ~81% human–human. https://neurips.cc/virtual/2023/poster/73434 ; arXiv:2306.05685. (accessed 2026-10-27 via search)
47. JMIR preprint — Hirosawa T, et al.: ChatGPT-4 final-diagnosis evaluation vs physicians, *"Cohen's κ = 0.63 (95% CI: 0.56–0.69)"*. https://s3.ca-central-1.amazonaws.com/assets.jmir.org/assets/preprints/preprint-59267-accepted.pdf (accessed 2026-10-27 via search). `WEAK-EVIDENCE`.
48. medRxiv — Croxford S, et al. (2025) *Medical LLM-as-a-Judge* for clinical summaries: concordance on faithfulness/completeness rubrics, weaker on interpretive criteria. https://www.medrxiv.org/content/10.1101/2025.04.22.25326219v2.full.pdf (accessed 2026-10-27 via search). `WEAK-EVIDENCE`.
49. JAMA systematic review (2025): only ~5% of healthcare LLM evaluations use real patient care data (cited via secondary coverage). `WEAK-EVIDENCE`. (accessed 2026-10-27 via search)

---

## Implications for AegisMed

1. **Retire the 98% claim everywhere** (README, report, patent, viva deck). It is generated from AegisMed's own KB: `scripts/benchmark/demat_benchmark.py` builds its 200 cases from `DISEASE_DATABASE` and its `simulate_patient_answer()` answers DEMAT's follow-up questions using the same KB's `likelihoods` — the oracle is the system under test. Re-label it "internal consistency test" or delete it.
2. **Rebuild `scripts/benchmark/demat_benchmark.py` around an external case manifest.** New flow: (a) load `data/benchmark/cases.jsonl` — cases taken from **gretelai/symptom_to_diagnosis test split (212, Apache 2.0)** for the 22 overlapping conditions, plus a DxBench-derived subset (map its 1,148 cases onto AegisMed's 15 conditions and keep the intersection, discarding unmapped cases — report the kept-N); (b) patient turns come **only from the case text** — delete `simulate_patient_answer()` and any `DISEASE_DATABASE` reference inside the eval path; (c) if a DEMAT follow-up question has no scripted answer in the case, score it as "asked" and carry the case's stated symptoms forward, and report the fraction of questions answered from case text.
3. **Adopt a three-tier claim vocabulary:** Tier A "smoke test" (Kaggle DSP, in-KB cases — never published), Tier B "external benchmark" (gretelai test split, DxBench subset, HealthBench — publishable with per-split CIs), Tier C "physician-graded" (Semigran-style vignette panel — publishable and DECIDE-AI-reportable). No number may appear in README/paper/patent without a tier label.
4. **NLP stage eval:** fine-tune/evaluate the pattern extractor against the 212 gretelai test cases (input_text → diagnosis, and token-level symptom spans) and report top-1/top-3 + negation-accuracy on the explicit negation subset (build one by LLM-rewriting 50 test cases with negations, disclosed as synthetic).
5. **HealthBench-style rubric eval for report synthesis:** write ~40 weighted rubric items per case (accuracy facts, must-ask follow-ups, red-flag escalation with **negative points**, communication quality), grade AegisMed reports on 100 HealthBench-style conversations with an LLM judge (GPT-4-class), calibrate the judge against 2 physicians on a 30-case subset and report Cohen's κ (target ≥0.6, per [46][47]); report HealthBench axes (accuracy, completeness, context-awareness, communication) for comparability. HealthBench is MIT-licensed — the repo can include the grader and a subset of items.
6. **Triage stage eval:** map AegisMed's urgency output onto **ESI 1–5**; without credentialing, run the Semigran design (15 urgent / 15 low-urgency / 15 non-urgent vignettes, physician-set urgency gold standard, score over-/under-triage — the two failure modes that matter); with PhysioNet credentialing (no IRB needed for DUA use at most institutions), score chief-complaint → acuity on MIMIC-IV-ED's `triage` table (~425k visits).
7. **Risk-model training data:** replace the 500-record in-house generator with **Synthea-generated data (Apache 2.0)** using modules matching the 15 conditions, tuned to **ICMR-INDIAB / GBD-India prevalence priors**; document the Chen-2019 realism caveats in the model card and validate on gretelai/DxBench held-out cases.
8. **Sample-size rule:** any published accuracy claim needs n such that 1.96²·p(1−p)/n ≤ 0.05² — at p≈0.7 that is **323 cases** (p≈0.9 → 139; p≈0.5 → 385). For DEMAT-vs-ablation, run exact McNemar on ≥300 shared cases with ≥10k-re-sample case-level bootstrap CIs; preregister hypotheses + analysis on OSF before grading.
9. **India readiness:** prevalence-calibrate priors from NFHS-5/GBD; probe the pattern extractor with Hinglish paraphrases of the gretelai test set (documented as synthetic, since no public Hinglish clinical corpus exists); do not ship ChatDoctor/MedDialog-derived text in the public repo (scraped, license UNKNOWN).
10. **Write-up:** structure the vignette-study section of the CHIL paper per **DECIDE-AI**'s 17 items now (while blocked on IRB, stages 1–2 of DECIDE-AI — bench/silico + vignette evaluation — are fully executable); put TRIPOD+AI on the risk-model section. This converts the IRB blockage from an excuse into a staged plan.
