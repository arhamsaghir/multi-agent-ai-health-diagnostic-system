# S2 — How Symptom Checkers Are Measured: The Public Accuracy-Evaluation Literature (2015-2026)

**Commissioned:** 2026-10-28 · **Scope:** S2 (`02_public_accuracy_evaluations.md`)
**Method:** Full texts or abstracts of the landmark studies were fetched directly where possible: Semigran 2015 read from the full BMJ PDF (WBUR archive copy), Hill 2020 read from the MJA full text, Ceney 2021 and Wallace 2022 fetched from PLOS ONE / Nature, Fraser 2023 abstract from PubMed, Schmieding 2021 / Kopka 2025 / Ilicki 2025 / Hammoud 2024 / Shan 2025 fetched from PMC. Verbatim quotes carry URL + publisher + date. <3 sources ⇒ `WEAK-EVIDENCE`.

## TL;DR

A decade of vignette audits gives the field a stable measurement grammar — **top-1/top-3 diagnostic accuracy** and **appropriate-triage-advice accuracy**, split over an urgency taxonomy (emergent / urgent / non-urgent / self-care), with **over-triage** and **under-triage** counted separately. The headline numbers are sober and consistent: the landmark 2015 audit of 23 checkers (45 vignettes) found the correct diagnosis listed **first in 34%** of evaluations and appropriate triage advice in **57%**; the 2020 Australian audit (36 checkers, 48 vignettes) reproduced it (**36%** top-1, triage **"risk-averse"** with 40% of non-urgent/self-care vignettes escalated to urgent/emergency); a 2022 systematic review across 10 studies (48 checkers) put primary diagnostic accuracy at **19-37.9%** and triage accuracy at **48.8-90.1%**. Best-in-class deterministic systems reach ~70% top-3 (Ada, Gilbert 2020) and ~91% triage accuracy/94% safety when evaluated on favorable, urgent-skewed real-case vignettes (Ilicki 2025). The 2023-2026 LLM era changed the *diagnosis* leaderboard but not the *triage* leaderboard: ChatGPT matched rule-based checkers on top-1/top-3 in real ED data (Fraser 2023) but showed **41% unsafe triage** (GPT-3.5) vs Ada's 14%, and in a 600-participant RCT (Kopka 2025) the app improved laypeople's self-triage (53.2%→64.5%) while ChatGPT did not (54.8%→54.2%). **Every published evaluation uses externally authored or real-case vignettes — none would accept a benchmark generated from the system's own knowledge base.** AegisMed's 98% top-1 on 200 self-referential synthetic cases is not comparable to any number in this literature, and its keyword-based escalation (`/emergency-check`) would score like the worst 2015-era checkers: perfect over-triage, no self-care discrimination.

---

## 1. The canonical audit: Semigran et al., BMJ 2015

**Citation (read from full-text PDF [1]):** Semigran HL, Linder JA, Gidengil C, Mehrotra A. "Evaluation of symptom checkers for self diagnosis and triage: audit study." BMJ 2015;351:h3480, doi:10.1136/bmj/h3480, published 8 July 2015.

**Design:** 23 publicly available, free, English-language symptom checkers (from 143 identified; 102 excluded as duplicates, 25 as single-condition); 45 standardized patient vignettes **"equally divided into three categories of triage urgency: emergent care required (for example, pulmonary embolism), non-emergent care reasonable (for example, otitis media), and self care reasonable (for example, viral upper respiratory infection)"** — 15 each; 26 common and 19 uncommon diagnoses; entered by a non-clinician with standardized wording; **770** diagnosis evaluations and **532** triage evaluations in the analyzed set. Triage judged against Schmitt-Thompson nurse triage protocol conventions; a checker's most urgent suggestion counted.

**Verbatim key results [1]:**

- Diagnosis: **"The 23 symptom checkers provided the correct diagnosis first in 34% (95% confidence interval 31% to 37%) of standardized patient evaluations, listed the correct diagnosis within the top 20 diagnoses given in 58% (55% to 62%) of standardized patient evaluations, and provided the appropriate triage advice in 57% (52% to 61%) of standardized patient evaluations."**
- Top-3 (reported separately): correct diagnosis listed **in the first three diagnoses in 51% (47% to 55%)**.
- Triage by urgency: **"with appropriate triage advice provided in 80% (95% confidence interval 75% to 86%) of emergency cases, 55% (47% to 63%) of non-emergent cases, and 33% (26% to 40%) of self care cases (P<0.001)."**
- Diagnosis by urgency: correct first for **24%** of emergent, **38%** of non-emergent, **40%** of self-care evaluations (P<0.001).
- Diagnosis by prevalence: correct first more often for **common (38%) than uncommon (23%)** diagnoses (P=0.004).
- Spread: **"Performance across the 23 individual symptom checkers ranged from 33% (95% confidence interval 19% to 48%) to 78% (64% to 91%)"** for appropriate triage advice; listing correct dx first ranged **5% (MedDx) to 50%** (DocResponse).
- Risk-aversion mechanism: **"iTriage, Symptomate, and Isabel always suggested users seek care and therefore never advised self care"**; checkers using Schmitt/Thompson protocols provided appropriate triage more often (≥72% vs 55%, P=0.01).
- Sensitivity analysis: excluding four symptom checkers, appropriate triage advice **61% (56% to 66%)**.
- Conclusion: **"Symptom checkers had deficits in both triage and diagnosis. Triage advice from symptom checkers is generally risk averse, encouraging users to seek care for conditions where self care is reasonable."**

*Note:* the brief for this research said "20 symptom checkers" — the published number is **23**.

## 2. The Australian audit: Hill et al., MJA 2020 (often miscited as BMJ Open)

**Citation (fetched from MJA site [2]):** Hill MG, Sim M, Mills B. "The quality of diagnosis and triage advice provided by free online symptom checkers and apps in Australia." Med J Aust 2020;212(11):514-519, doi:10.5694/mja2.50600, published online 18 May 2020. *(The brief for this file listed it as "Hill et al. BMJ Open 2020" — it is MJA; BMJ Open 2020;10:e040269 is a different Hill-adjacent audit, Gilbert et al., below.)*

**Design (verbatim [2]):** "36 SCs providing medical diagnosis or triage advice were tested with 48 medical condition vignettes (1170 diagnosis vignette tests, 688 triage vignette tests)." Vignette mix: 13 emergency, 14 urgent, 11 non-urgent, 10 self-care; 85% common conditions. Ada was excluded (registration wall) per the authors' reply letter [3].

**Verbatim key results [2]:**

- **"listed the correct diagnosis first in 421 of 1170 SC vignette tests (36%; 95% CI, 31–42%)"**; **"among the top ten results in 681 tests (58%; 95% CI, 53–65%)"**.
- AI-labelled vs other SCs: **"listed the correct diagnosis first in 46% of tests (95% CI, 40–57%), compared with 32% (95% CI, 26–38%) for other SCs."**
- Individual spread: **"The mean rate of first correct results for individual SCs ranged between 12% and 61%."**
- Triage by urgency: **"Appropriate triage advice was more frequent for emergency care (63%; 95% CI, 52–71%) and urgent care vignette tests (56%; 95% CI, 52–75%) than for non-urgent care (30%; 95% CI, 11–39%) and self-care tests (40%; 95% CI, 26–49%)."**
- Over/under-triage: **"The advice for 40% of non-urgent and self-care category vignettes was to seek urgent or emergency care"**; **"for 10% of emergency category vignettes, non-urgent care or self-care was recommended."**
- Conclusion: "The quality of diagnostic advice varied between SCs, and triage advice was generally risk-averse, often recommending more urgent care than appropriate."

## 3. The GP head-to-head: Gilbert et al., BMJ Open 2020

**Citation:** Gilbert S, Mehl A, Baluch A, et al. "How accurate are digital symptom assessment apps for suggesting conditions and urgency advice? A clinical vignettes comparison to GPs." BMJ Open 2020;10(12):e040269, doi:10.1136/bmjopen-2020-040269 [4][5].

**Design:** 8 apps ("Ada Health, Babylon, Buoy, K Health, Mediktor, Symptomate, WebMD and Your.MD") × 200 clinical vignettes; 7 external GPs as comparison; each app tested once per vignette [5].

**Key results (news-account verbatim [5]; paper-level figures [4]):**

- Coverage: **"The most comprehensive app was Ada, which provided a condition suggestion 99% of the time, followed by WebMD at 93% and Buoy at 88.5%"**; lowest **"Babylon… only 51.5% of the time, followed by Symptomate at 61.5% and Your.MD at 64.5%"**.
- Accuracy (top-3): GPs **82.1% (±5.2)**; Ada **70.5%** (best app); Buoy **43%**; lowest Symptomate **27.5%**.
- Safety of urgency advice: GPs **97.0% (±2.5)**; "Most apps gave safe advice, all scoring above 80%, but only Ada, Babylon and Symptomate came close to the 97% safety rating of the human GPs."
- Conclusion (paper): "The utility of digital symptom assessment apps relies on coverage, accuracy and safety. While no digital…" app outperformed GPs. [4]

This is the study that produced Ada's still-quoted **70.5%** best-in-class figure.

## 4. The NHS-utilization audit: Ceney et al., PLOS ONE 2021

**Citation (fetched [6]):** Ceney A, Tolond S, Glowinski A, Marks B, Swift S, Palser T. "Accuracy of online symptom checkers and the potential impact on service utilisation in the NHS: a study of 136 clinical presentations." PLoS ONE 2021;16(7):e0254088, doi:10.1371/journal.pone.0254088, published July 15, 2021. *(The brief said "Fam Pract" — it is PLOS ONE.)*

**Design:** **"Twelve tools were identified and included."** Vignettes mapped to NICE triage categories: emergent 16, urgent 11, non-urgent 7, self-care 15 ("a total of 50 vignettes"; the title's 136 counts the clinical presentations underlying them).

**Verbatim key results [6]:**

- **"Overall, across all vignettes evaluated, the correct diagnosis was listed first in 37.7% of traversals"**, ranging **"from 22.2% (95% CI 13.6–35.2%) in the least accurate system to 72.0% (95% CI 52.8–88.0%) in the most."**
- **"the correct diagnosis was listed in the top five diagnoses 51.0% (95% CI 46.7–55.1%) of the time"**; **"the likelihood of the correct diagnosis listed at all was 54.2% (95% CI 50.0–58.3%)."**
- Triage: **"Appropriate triage advice across all clinical vignettes tested was given in 57.7% of cases"** — emergent **71.1% (63.4–77.8%)**, urgent **52.1% (42.2–61.8%)**, non-urgent **54.0% (41.8–65.7%)**, self-care **48.9% (40.8–57.1%)**.
- Safety metric (distinct from appropriateness): advice safe **"in 82.6% (95% CI 78.9–85.9%) of all vignettes"**; abstract: **"Safety of disposition advice decreased with condition urgency (being 71.8% for emergency cases vs 87.3% for non-urgent cases)."**
- Over-utilisation: **"51.0% of systems suggested additional resource utilisation above that recommended by national guidelines (range 18.0% to 61.2%)."** Self-care over-referral: **"51.8% (95% CI 43.6–59.9%) of completed traversals suggested a health care service was required."**

## 5. The systematic review: Wallace et al., npj Digital Medicine 2022

**Citation (fetched [7]):** Wallace W, Chandler C, Bacardit J, Yu F, Nadal S. "The diagnostic and triage accuracy of digital and online symptom checker tools: a systematic review." npj Digital Medicine 5:118 (2022), doi:10.1038/s41746-022-00667-w, published 17 August 2022.

**Verbatim key results [7]:**

- Scope: "Of the 177 studies retrieved, 10 studies met the inclusion criteria" — covering **48 different symptom checkers**.
- **"The diagnostic accuracy of the primary diagnosis was low across included studies (range: 19–37.9%)"**; results text: "ranging from 19 to 38%".
- **"Top three diagnostic accuracy, measured in seven studies, ranged from 33 to 58%."**
- **"Triage accuracy (range: 48.8–90.1%) was typically higher than diagnostic accuracy."**
- **"the WebMD symptom checker was assessed eight times and was the most commonly assessed symptom checker in this review"** — its primary diagnostic accuracy "ranged from 3 to 53%".
- Conclusions: "Overall, the diagnostic and triage accuracy of symptom checkers are variable and of low accuracy."; "reliance upon symptom checkers could pose significant patient safety hazards"; "an urgent assessment of how these systems are regulated and implemented is required."

## 6. Humans as the baseline: Schmieding et al., JMIR 2021

**Citation (fetched PMC [8]):** Schmieding ML, Mörgeli R, Schmieding MAL, Feufel MA, Balzer F. "Benchmarking Triage Capability of Symptom Checkers Against That of Medical Laypersons: Survey Study." J Med Internet Res 2021;23(3):e24475, doi:10.2196/24475 (Mar 10, 2021).

**Design:** Re-ran the 45 Semigran vignettes on 15 current checkers; 91 laypersons → 4,095 evaluations; SCs → 532 evaluations.

**Verbatim key results [8]:**

- Laypersons **"60.9%, SD 6.8%; 95% CI 59.5%-62.3%"** mean triage accuracy vs SCs **"58%, SD 12.8%"** — "an average SC has no greater overall triage accuracy than an average user."
- By level: SCs better on emergencies (**80.6%** vs 67.5%) but worse on self-care (**30.6%** vs 46.7%).
- **"an average SC has no greater overall triage accuracy than an average user"**; SCs overtriaged **"182/532, 34.2%"** vs undertriage **"9.2% (49/532)"** — over:under ratio 3.5:1 vs 1.5:1 for laypersons; **"SCs misclassified self-care cases as emergencies 6 times more often than participants did (43/174, 24.7% vs 56/1365, 4.10%)."**
- Strategic conclusion: "Laypersons sometimes require support in deciding when to rely on self-care but it is in that very situation where SCs perform the worst."

## 7. The LLM era, 2023-2026: diagnosis improved, triage safety did not (automatically)

### 7.1 Fraser et al., JMIR mHealth 2023 — ChatGPT vs Ada vs WebMD vs physicians, real ED patients

**Citation:** Fraser H, Crossland D, Bacher I, Ranney M, Madsen T, Hilliard R. JMIR Mhealth Uhealth 2023;11:e49995, doi:10.2196/49995 (Oct 3, 2023) [9]. Design: deidentified self-report data from **40 ED patients** (30 usable for diagnosis, 37 for triage) entered into ChatGPT-3.5, ChatGPT-4.0, WebMD, vs Ada's own stored outputs; final ED diagnoses + blinded review by 3 board-certified emergency physicians.

**Results (abstract figures via PubMed fetch [9]):**

| Tool | Top-1 dx | Top-3 dx | Triage agreement | Unsafe triage | Too cautious |
|---|---|---|---|---|---|
| Ada | 30% (9/30) | 63% (19/30) | 62% | 14% | 24% |
| WebMD | 40% (12/30) | 57% (17/30) | 70% | 19% | 11% |
| ChatGPT-3.5 | 40% (12/30) | 63% (19/30) | 59% | **41%** (P=.009 vs Ada) | 0% |
| ChatGPT-4.0 | 33% (10/30) | 50% (15/30) | 76% | 22% | 3% |
| Physicians (mean) | 47% | 69% | — | — | — |

- Authors' conclusion: "The Ada and WebMD SCs performed better overall than ChatGPT"; unsupervised patient use of ChatGPT not recommended without triage improvements. **The first real-patient head-to-head showed LLM ≈ rule-based on diagnosis, LLM worse on triage safety.**

### 7.2 Kopka et al., npj Health Systems 2025 — do the tools actually help users?

**Citation (fetched PMC [10]):** Kopka M, Wang SM, Kunz S, Schmid C, Feufel MA. "Technology-supported self-triage decision making." npj Health Syst 2025;2:3, doi:10.1038/s44401-024-00008-x (Jan 25, 2025). Design: 600-participant randomized comparison; 27 validated vignettes; laypeople decide alone, then with Ada (SAA) or ChatGPT.

**Verbatim [10]:**

- **"participants increased their self-triage accuracy from 53.2% to 64.5% when using the SAA (OR = 2.52 [1.50–3.55], z = 3.75 p < 0.001)"** — Ada raised human accuracy.
- **"did not show such an increase when using ChatGPT (54.8% pre vs. 54.2% post usage, z = −0.27, p = 0.79)"** — ChatGPT as used by laypeople did not.
- Users resist bad advice: after wrong SAA advice following a correct initial decision, "they remained at a correct solution in 72% of cases (21/29)"; ChatGPT 61% (22/36).
- SAA's biggest effect is self-care recognition: self-care accuracy **"13.1% pre vs. 36.9% post, OR = 8.59"**. Main system-level risk: **false alarms** (increased emergency-seeking).
- Methodological moral: evaluate **human-in-the-loop**, because tool-alone accuracy does not predict team performance.

### 7.3 Hammoud et al., JMIR AI 2024 — 6 checkers, 400 peer-reviewed vignettes

**Citation (fetched PMC [11]):** Hammoud M, Douglas S, Darmach M, Alawneh S, Sanyal S, Kanbour Y. "Evaluating the Diagnostic Performance of Symptom Checkers: Clinical Vignette Study." JMIR AI 2024;3:e46875, doi:10.2196/46875 (Apr 29, 2024). Checkers: **Avey, Ada, K Health, Buoy, Babylon, WebMD** on 400 peer-reviewed vignettes ("each approved by at least 5 out of 7 independent and experienced primary care physicians").

**Verbatim [11]:** Avey (the authors' own product — **conflict of interest**, all authors Avey Inc) achieved "average M1, M3, M5, recall, precision, F1-measure, and NDCG of 67.5%, 87.3%, 90%, 72.9%, 43.7%, 54.6%, and 76.6%" vs physicians "61.2%, 72.5%, 72.9%, 46.6%, 69.5%, 55.3%, and 61.2%". Avey "outperformed Ada, K Health, Buoy, Babylon, and WebMD by averages of 24.5%, 142.8%, 159.6%, 2968.1%, and 175.5%… in listing the vignettes' main diagnoses at the top of their differentials"; spread between best and worst checker: M1 65.3%. Takeaway independent of the COI: **checker-vs-checker spread is enormous**, so "symptom checkers" cannot be treated as one class.

### 7.4 Shan et al., JMIR Med Inform 2025 — meta-analysis of LLMs vs clinicians

**Citation (fetched PMC [12]):** Shan G, Chen X, Wang C, Liu L, Gu Y, Jiang H, Shi T. "Comparing Diagnostic Accuracy of Clinical Professionals and Large Language Models: Systematic Review and Meta-Analysis." JMIR Med Inform 2025;13:e64963, doi:10.2196/64963 (Apr 25, 2025).

**Verbatim [12]:** "A total of 30 studies involving 19 LLMs and a total of 4762 cases were included."; **"For the optimal model, the accuracy of the primary diagnosis ranged from 25% to 97.8%, while the triage accuracy ranged from 66.5% to 98%."**; professionals had higher diagnostic accuracy in **33.7% (20/30)** of studies while "the LLMs, specifically ChatGPT, had higher diagnostic accuracy than humans" in **33.3% (10/30)**; **"20/30 (66.6%) exhibited a high risk of bias."** No pooled rule-based-vs-LLM subgroup exists yet — the literature has not cleanly separated LLM symptom checkers from rule-based ones at meta-analysis level.

### 7.5 Ilicki et al., Scand J Prim Health Care 2025 — the favorable end of the spectrum, with a COI

**Citation (fetched PMC [13]):** Ilicki J, Edman S, Stalfors J, Molin CJ. "Evaluating digital triage symptom checker with historical triage-related adverse events." Scand J Prim Health Care 2025;44(1):1-14, doi:10.1080/02813432.2025.2563517. Design: Triage24 (Platform24; rule-based "digital front door" to Swedish 1177); vignettes built from **69 real triage-related adverse-event cases** reported to the Swedish IVO (2010-2021); 483 trials by 7 physicians, 390 analyzed.

**Verbatim [13]:** "The symptom checker achieved 91% accuracy (95% CI 88–94%)" and "94% safety (95% CI 91–96%)"; 25 under-triaged vs 9 over-triaged trials. Caveats (authors'): all authors "former employees" of the manufacturer; cases skewed urgent (72% immediate); "results from this study should be interpreted with caution." Still methodologically notable: **first vignette set built from real cases with known triage errors** — the direction good external validation should take.

### 7.6 Research-frontier LLM systems

- **AMIE (Google):** Tu et al., "Towards conversational diagnostic artificial intelligence," Nature (2025), s41586-025-08866-7: randomized double-blind crossover, text consultations with patient actors across **149 OSCE-style scenarios**; "AMIE's performance matched or surpassed PCP" — outperforming primary-care physicians on **28 of 32** OSCE axes including diagnostic accuracy. Simulated dialogue, not a deployed checker. [14][15] `WEAK-EVIDENCE` on exact axis counts (paper + Google blog; Nature page paywalled at fetch time).
- **Med-Gemini (Google, 2024):** arXiv report; MedQA 91.1%; clinician-evaluated DDx top-1 ~45% vs 36% GPT-4 on complex cases. `WEAK-EVIDENCE` (preprint + vendor blog). [16][17]
- **Follow-up AMIE work (2026):** reported differential-diagnosis containment of final diagnosis ~90% at chart review in management tasks (DeepMind blog/News-Medical) — `WEAK-EVIDENCE`, secondary only. [18]

### 7.7 Related 2024-2025 benchmarks worth tracking for CHIL positioning

- **HealthBench** (OpenAI, Arora et al., 2025; arXiv:2505.08775) — rubric-based LLM evaluation on realistic medical conversations, including triage safety behaviors. [19]
- **Sequential Diagnosis Benchmark** (Nori et al., Microsoft, 2025; arXiv:2506.22405) — iterative diagnosis as sequential decision making; directly comparable to DEMAT-style multi-round questioning. [19]
- **RepVig framework / Kopka group** — vignette development with "representative design" for layperson-vs-app-vs-LLM triage comparisons. [10]

## 8. The metrics grammar of the field (what reviewers expect)

Consolidating the studies above, a publishable symptom-checker evaluation in 2026 reports:

1. **Diagnostic accuracy:** top-1 ("primary", "M1"), top-3, top-5/top-10, "listed at all"; per-condition and by prevalence (common vs uncommon — Semigran 38% vs 23% [1]); sometimes F1/recall/precision and NDCG (Hammoud [11]), mean reciprocal rank (Bridges/Isabel [20]).
2. **Triage/advice accuracy:** % appropriate advice overall and **by urgency level** (the emergent/urgent/non-urgent/self-care split of Semigran [1], Hill [2], Ceney [6]); against a named standard (Schmitt-Thompson protocols, NICE CKS, RGS).
3. **Safety:** % advice "safe" (not less urgent than warranted) — Ceney's 82.6% overall, decreasing with urgency (71.8% emergency vs 87.3% non-urgent) [6]; Ilicki's 94% [13].
4. **Over-triage** (escalation of self-care/non-urgent; resource-utilisation burden) **and under-triage** (failure to escalate emergencies) **reported separately** — never merged into one "accuracy" number (Hill: 40% over vs 10% under [2]; Schmieding: 34.2% over vs 9.2% under [8]).
5. **Coverage:** % of cases for which the system returns any suggestion (Gilbert: Ada 99% vs Babylon 51.5% [5]) — a system that abstains looks safer but covers less.
6. **Calibration/confidence:** less common in this literature; appears in LLM-era and triage-engine work (Brier scores in AegisMed's own demat benchmark are ahead of most published checker audits here).
7. **Human-in-the-loop performance** (Kopka [10]): user-alone vs user+tool accuracy — increasingly the ethically relevant number.
8. **Method standards:** standardized vignettes entered by a non-clinician (Semigran), physician-approved vignette sets (Hammoud [11]), real-case vignettes from adverse events (Ilicki [13]), blinded clinician ground truth (Fraser [9]), binomial CIs on every proportion, and explicit vignette-methodology critique (testers' "considerable difficulty… adhering to the original vignettes" [13]; idealized unambiguous cases — Kopka group critique).

**Best-in-class scorecard (external evaluations only):**

| Metric | Field (2015-2022) | Best commercial deterministic | LLM era |
|---|---|---|---|
| Top-1 dx | 19-37.9% (SR [7]); 34% [1]; 36% [2] | Ada 70.5% top-3; coverage 99% [4][5] | ChatGPT-3.5 40% top-1, 63% top-3 on real ED cases [9]; AMIE > PCP on simulated OSCE [14] |
| Appropriate triage | 48.8-90.1% (SR [7]); 57% [1] | Ada 71.1%→ (Ceney emergent band); Triage24 91% accuracy/94% safety (favorable real-case vignettes, COI) [13] | ChatGPT-4.0 76% agreement / 22% unsafe vs Ada 62% / 14% [9] |
| Over vs under-triage | over ≫ under everywhere: 40% vs 10% [2]; 34.2% vs 9.2% [8] | 9 over vs 25 under (Triage24) [13] | GPT-3.5: 0% "too cautious" but 41% unsafe [9] |
| Human baseline | laypersons 60.9% ≈ SCs 58% [8]; GPs 82.1% top-3 / 97.0% safe [4] | — | Kopka: app lifts laypeople +11.3 pts; ChatGPT ±0 [10] |

**What changed 2023 → 2026:**

1. LLMs closed the *diagnosis* gap with rule-based checkers and physicians on top-1/top-3 in some settings [12], but their *triage* failure mode inverted: less risk-averse, more unsafe (GPT-3.5 41% unsafe vs Ada 14% [9]) — the field's problem flipped from over-triage to under-triage/unsafe advice.
2. Evaluation focus shifted from "how accurate is the dx list" to "is the disposition safe + does the tool help the human" (Fraser [9], Kopka [10], Ilicki [13]).
3. Benchmarks standardized around patient-facing LLM behavior (HealthBench [19]); sequential/interactive diagnosis became the research frontier [19] — validating DEMAT's multi-round framing.
4. Persistent gap: almost no real-patient prospective evaluations (a 2025 review found only ~5% of healthcare LLM evaluations use real patient data — `WEAK-EVIDENCE`, secondary [21]); the strongest 2025-2026 studies are still vignette-based.
5. COI became a recurring asterisk (Hammoud/Avey [11], Ilicki/Platform24 [13]) — independent replication is the scarce commodity.

---

## 9. Implications for AegisMed (file-level)

1. **`scripts/generate_benchmark_cases.py` / `data/benchmark_cases.json` — the 200 self-generated cases make the 98% top-1 result unpublishedable.** Every study above (Semigran, Hill, Gilbert, Ceney, Fraser) uses vignettes authored outside the system under test, with ground truth from physicians or national guidelines. Rebuild the public benchmark on (a) the 45-vignette Semigran structure (15/15/15 emergency/non-emergent/self-care) with physician-adjudicated labels, and (b) a real-case stratum like Ilicki's. Report binomial 95% CIs on every proportion, as all of these papers do.
2. **`scripts/benchmark/metrics.py` — add the field's triage metrics.** Currently top-1/top-3/top-5 (per `run_benchmark.py`). Add: appropriate-triage-advice % by urgency level, safety % (advice never less urgent than warranted), over-triage rate, under-triage rate (reported separately), and coverage (any-suggestion rate). Without these, AegisMed cannot be compared to a single row of the literature.
3. **`src/core/demat.py` — produce a disposition label so triage metrics exist at all.** DEMAT emits candidates + entropy (`TriageSession.to_dict()`), not an emergent/urgent/non-urgent/self-care decision. Add a deterministic mapping from posterior × red-flag features to the 4-level disposition (e.g., `recommend_care_level()` beside `ENTROPY_STOPPING_THRESHOLD = 0.45`), so `scripts/benchmark/demat_benchmark.py` can score triage arms, not just diagnosis arms.
4. **`src/api/routes/diagnosis.py` — `/emergency-check` is a 2015-grade keyword escalator.** Semigran's worst checkers "always suggested users seek care"; Schmieding showed SCs misclassify self-care as emergency 24.7% vs 4.1% for laypersons. AegisMed's keyword list (English/Hindi, threshold 0.5) has no self-care discrimination. Wire DEMAT posteriors + `when_to_see_doctor` fields from `src/core/disease_kb.py` into the emergency check so the system can *recognize self-care cases* — the exact capability the literature identifies as the weakest everywhere and the most valuable one (Kopka: self-care accuracy 13.1%→36.9% with app support).
5. **`src/agents/nlp/agent.py` — fix negation before any external evaluation.** The repo's verified failure ("no fever, no cough, no chest pain" → extracted as present) is precisely the class of error vignette audits are designed to expose; a negation-blind extractor inflating emergent symptoms will produce garbage-in over-triage in any published run. Deterministic negation-scope handling before `_extract_symptoms()` + adversarial negation cases in `tests/unit/test_nlp_agent.py` are the minimal fix (see 03_clinical_nlp_sota.md).
6. **`src/agents/confidence_scorer.py` — calibration on external vignettes, not synthetic ones.** ECE 0.245 on self-generated data will not survive contact with externally authored cases; Hammoud-style M1/M3/NDCG plus Brier/ECE on an external vignette set is the CHIL-credible package (and AegisMed's `demat_benchmark.py` already computes Brier — extend it to the external set).
7. **Under-triage is the metric to optimize against — but report the over:under ratio honestly.** The field's systematic over-triage (3.5:1 in Schmieding [8]) is treated as the safe failure mode; GPT-3.5's 41% unsafe rate (Fraser [9]) is the cautionary LLM failure. AegisMed's deterministic design should target ≥Ceney's 82.6% safety and *near-zero under-triage on emergent vignettes*, while keeping the over-triage burden below the 51% over-referral level Ceney measured, and say so in the paper.
8. **Position the CHIL paper as methodology, not leaderboard.** With 15 conditions, AegisMed cannot win an accuracy comparison (Isabel: 87.1% top-1 [20]; Avey: 67.5% M1 [11]) — but "entropy-guided question selection vs single-pass, evaluated with human-in-the-loop self-triage gain (Kopka design) on external vignettes" is a novel, publishable claim that no commercial player has published.
9. **`frontend/src/lib/api.ts` + `frontend/src/components/diagnosis/SymptomInput.tsx` — copy the evaluation framing into the UI.** Public release must label outputs as triage advice ("possible causes", "care level"), display confidence honestly, and never fall back to `getDemoResults` silently — the field's evidence base (deficits in both triage and diagnosis, [1]) is the disclaimer text that should ship.
10. **Real-patient evaluation path (IRB was blocked):** the literature shows an acceptable middle path — vignettes *derived from real adverse-event records* (Ilicki [13]) and real patient self-reports replayed through the system (Fraser [9]) do not require treating patients, and are the designs CHIL reviewers will recognize.

---

## 10. Sources

1. Semigran HL, Linder JA, Gidengil C, Mehrotra A. "Evaluation of symptom checkers for self diagnosis and triage: audit study." BMJ 2015;351:h3480 (8 Jul 2015). Full-text PDF: https://media.wbur.org/wp/2015/07/BMJ-Embargoed-Symptom-Checker-study.pdf (fetched and read 2026-10-28). Landing: https://www.bmj.com/content/351/bmj.h3480 — verbatim: "The 23 symptom checkers provided the correct diagnosis first in 34% (95% confidence interval 31% to 37%) of standardized patient evaluations, listed the correct diagnosis within the top 20 diagnoses given in 58% (55% to 62%)…, and provided the appropriate triage advice in 57% (52% to 61%)…"; "appropriate triage advice provided in 80% (95% confidence interval 75% to 86%) of emergency cases, 55% (47% to 63%) of non-emergent cases, and 33% (26% to 40%) of self care cases (P<0.001)"; "iTriage, Symptomate, and Isabel always suggested users seek care and therefore never advised self care"; "Triage advice from symptom checkers is generally risk averse."
2. Hill MG, Sim M, Mills B. Med J Aust 2020;212(11):514-519, doi:10.5694/mja2.50600 (online 18 May 2020) — https://www.mja.com.au/journal/2020/212/11/quality-diagnosis-and-triage-advice-provided-free-online-symptom-checkers-and (fetched) — verbatim: "36 SCs… tested with 48 medical condition vignettes (1170 diagnosis vignette tests, 688 triage vignette tests)"; "listed the correct diagnosis first in 421 of 1170 SC vignette tests (36%; 95% CI, 31–42%)"; "among the top ten results in 681 tests (58%; 95% CI, 53–65%)"; "The advice for 40% of non-urgent and self-care category vignettes was to seek urgent or emergency care"; "for 10% of emergency category vignettes, non-urgent care or self-care was recommended."
3. Hill MG, Sim M, Mills B, "In reply." Med J Aust 2021;214(3):143, doi:10.5694/mja2.50923 — https://cdn.craft.cloud/019efd17-dcc2-707f-8e07-011d00d1146a/assets/issues/mja250923.pdf (fetched, read) — Ada excluded for account-registration wall.
4. Gilbert S, Mehl A, Baluch A, et al. BMJ Open 2020;10(12):e040269, doi:10.1136/bmjopen-2020-040269 — https://bmjopen.bmj.com/content/10/12/e040269 · PubMed https://pubmed.ncbi.nlm.nih.gov/33328258 — GP top-3 82.1%±5.2; Ada 70.5%; GP safe-urgency 97.0%±2.5. (BMJ Open page fetch blocked; figures corroborated by [5] and search abstract.)
5. Medical Device Network, "Significant disparities found in symptom assessment apps" (16 Dec 2020) — https://www.medicaldevice-network.com/news/symptom-assessment-apps (fetched) — coverage/accuracy/safety verbatim quotes; app list; 200 vignettes; 7 GPs.
6. Ceney A, et al. PLoS ONE 2021;16(7):e0254088, doi:10.1371/journal.pone.0254088 (15 Jul 2021) — https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0254088 (fetched) — verbatim quotes as in §4.
7. Wallace W, et al. npj Digit Med 5:118 (17 Aug 2022), doi:10.1038/s41746-022-00667-w — https://www.nature.com/articles/s41746-022-00667-w (fetched via redirect) — verbatim quotes as in §5.
8. Schmieding ML, et al. J Med Internet Res 2021;23(3):e24475, doi:10.2196/24475 — https://pmc.ncbi.nlm.nih.gov/articles/PMC7991983/ (fetched) — verbatim quotes as in §6.
9. Fraser H, Crossland D, Bacher I, Ranney M, Madsen T, Hilliard R. JMIR Mhealth Uhealth 2023;11:e49995, doi:10.2196/49995 (3 Oct 2023) — PubMed abstract https://pubmed.ncbi.nlm.nih.gov/37788063/ (fetched; PMCID PMC10582809) — figures as in §7.1. AHRQ project page: https://digital.ahrq.gov/ahrq-funded-projects/evaluating-diagnostic-decision-support-systems-patients-requiring-urgent/citation/comparison.
10. Kopka M, Wang SM, Kunz S, Schmid C, Feufel MA. "Technology-supported self-triage decision making." npj Health Syst 2025;2:3, doi:10.1038/s44401-024-00008-x (25 Jan 2025) — https://pmc.ncbi.nlm.nih.gov/articles/PMC13354180/ (fetched) — verbatim quotes as in §7.2.
11. Hammoud M, et al. JMIR AI 2024;3:e46875, doi:10.2196/46875 (29 Apr 2024) — https://pmc.ncbi.nlm.nih.gov/articles/PMC11091811/ (fetched) — verbatim quotes as in §7.3; COI disclosed (Avey Inc authors).
12. Shan G, et al. JMIR Med Inform 2025;13:e64963, doi:10.2196/64963 (25 Apr 2025) — https://pmc.ncbi.nlm.nih.gov/articles/PMC12047852/ (fetched) — verbatim quotes as in §7.4.
13. Ilicki J, Edman S, Stalfors J, Molin CJ. Scand J Prim Health Care 2025;44(1):1-14, doi:10.1080/02813432.2025.2563517 — https://pmc.ncbi.nlm.nih.gov/articles/PMC12918410/ (fetched) — verbatim quotes as in §7.5; COI (Platform24 employees).
14. Tu T, et al. "Towards conversational diagnostic artificial intelligence." Nature (2025) — https://www.nature.com/articles/s41586-025-08866-7 · arXiv:2401.05654 (Jan 2024) · PubMed 40205050 — 149 OSCE scenarios; "matched or surpassed PCP"; 28/32 axes.
15. Google Research blog, "AMIE: A research AI system…" (12 Jan 2024) — https://research.google/blog/amie-a-research-ai-system-for-diagnostic-medical-reasoning-and-conversations
16. "Capabilities of Gemini Models in Medicine" (Med-Gemini), arXiv:2404.18416 (2024) — https://arxiv.org/html/2404.18416v2 — MedQA 91.1%; DDx top-1 ~45% vs 36% GPT-4. `WEAK-EVIDENCE`.
17. Google Research blog, "Advancing medical AI with Med-Gemini" (15 May 2024) — https://research.google/blog/advancing-medical-ai-with-med-gemini
18. DeepMind blog / News-Medical (2026) on AMIE follow-up disease-management results — https://deepmind.google/blog/ai-co-clinician ; https://www.news-medical.net/news/20260621/Googlee28099s-AMIE-beats-doctors-on-key-simulated-disease-management-tasks.aspx — "~90%" differential containment. `WEAK-EVIDENCE` (secondary).
19. Arora S, et al. "HealthBench" arXiv:2505.08775 (2025); Nori H, et al. "Sequential Diagnosis Benchmark" arXiv:2506.22405 (2025).
20. Bridges JM, et al. *Diagnosis* (De Gruyter, 2024) — https://www.degruyterbrill.com/document/doi/10.1515/dx-2024-0033/html — "Isabel Pro produced 175 (87.1 %)" of 201 cases vs ChatGPT-4 82.1%.
21. News-Medical summary of a 2025 systematic review: only ~5% of healthcare LLM evaluations use real patient data. `WEAK-EVIDENCE` (secondary; locate the primary review before citing in the paper — how to find out: search PubMed for "large language models healthcare evaluations systematic review real patient data 2025").
