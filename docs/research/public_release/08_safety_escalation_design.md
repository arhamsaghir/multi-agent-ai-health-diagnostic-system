# 08 — Safety & Escalation Design for Consumer-Facing Symptom Assessment

**Status:** Research dossier for AegisMed public-release hardening
**Date:** October 2026 (verification pass completed 28 Oct 2026: headline claims re-verified against primary sources; one mislabeled study corrected — see §2.1)
**Scope:** Red-flag clinical systems, triage protocol logic, deployed-system safety layers, human factors/UI, safety evaluation, special populations
**Evidence rules applied:** ≥3 independent sources for load-bearing claims; verbatim criteria fetched from NICE/CDC/WHO/agency pages and peer-reviewed journals where accessible; `WEAK-EVIDENCE` / `UNKNOWN` markers where the bar is not met.

---

## TL;DR

1. **Under-triage of emergencies is the field's defining failure, including in flagship products.** An independent evaluation of ChatGPT Health (Mount Sinai; *Nature Medicine*, 23 Feb 2026) found it under-triaged **51.6%** of gold-standard emergency cases and over-triaged **64.8%** of non-urgent cases across 960 structured triage scenarios, with inconsistently activated suicide-crisis safeguards — it frequently missed suicidal ideation [1,2]. At EUSEM 2025, an AI triage tool achieved **58.3% sensitivity** for urgent cases vs **73.8%** for nurses [3].
2. **The dominant mechanism of failure is not wrong classification but failure to *ask*.** The only head-to-head red-flag audit (Sutaria et al., BMC Health Services Research 2025) found four commercial checkers asked only **36.9%** of relevant red-flag questions vs **71.8%** for primary-care physicians (Ada: 26.6%; Symptomate: 17.5%), concluding "OSCs in their current form do not adequately seek red flags" [4]. AegisMed's keyword matching has the same shape: it never asks.
3. **Clinicians use machine-checkable numeric gates, not vibes.** NEWS2 (six parameters; aggregate ≥5 = urgent review, ≥7 or a single score of 3 = emergency response) [5,6,7], the UK Sepsis Trust red-flag set (RR ≥25, HR ≥130, SBP ≤90, new confusion ACVPU, temp <36 °C, mottled/non-blanching rash) [8,9,10], NICE CG95 angina typicality (3/2/1-feature rule) [11], FAST/BE-FAST [12,13], and the C-SSRS 6-question suicide screener [14,15,16] are all directly translatable into a rule engine.
4. **Even clinician-operated triage under-triages materially, and its sensitivity swings widely by outcome.** Verified MTS performance figures: sensitivity 79.4% for urgent codes in a 3,002-patient headache cohort (Brigo 2022, single-centre) [17]; **61.5% for sepsis** (Gräff 2017) and **75.0% for life-saving interventions** (Gräff 2019) as re-analyzed in a 2026 systematic review [74]; real-world under-triage of 0.9% (119/13,408 children) with 53% judged clinically severe, concentrated in "unwell child" and dyspnoea flows (Seiger 2011) [18]. A consumer tool should therefore assume its own sensitivity is worse and compensate with over-triggering on cheap-to-check criteria and prominent, action-first UI.
5. **Disclaimers are not a safety mechanism; designed actions are.** Warning-compliance research (Wogalter) shows compliance requires signal word + hazard + consequence + **specific instruction**, delivered prominently [19,20]; real-world NHS 111 failures show passive advice ("stay at home") actively deterred deteriorating patients from re-seeking care [21]. Google/YouTube's crisis-resource pattern (top-of-results card, one-tap call/text, geolocalized number) is the most battle-tested consumer escalation UI [22,23].
6. **Special populations break adult logic silently.** Pregnancy (CDC Hear Her's 15 urgent maternal warning signs [24]; FDA NSAID avoidance from 20 weeks [25]), pediatrics (NICE NG143: fever ≥38 °C under 3 months = red, age-banded thresholds [26,27]; weight-based dosing), and elderly atypical presentations (sepsis presenting as confusion or a fall, not fever [28,29]; polypharmacy blunting physiology [30]) each require separate gating rules.
7. For AegisMed: replace the 12-item `SAFETY_KEYWORDS` list with a structured, tiered red-flag engine that **drives follow-up questions**, add NEWS2-style numeric scoring, restructure `doctor_alert` from a capped boolean into an unbounded structured escalation object, apply fail-safe defaults in the frontend severity normalizer, implement crisis-card UI patterns, and gate release on an adversarial safety-coverage test suite.

---

## 1. Red-Flag Systems in Clinical Practice

### 1.1 Suspected cancer — NICE NG12

NICE NG12 (*Suspected cancer: recognition and referral*, published 2015, updated since — the 2023 update added non-site-specific presentations such as unexplained weight loss; exceptional surveillance Mar 2025) defines hundreds of symptom→action pairs phrased as "consider [referral]" or "suspected cancer pathway referral" (urgent assessment within 28 days). Direct fetching of nice.org.uk was blocked (HTTP 403); criteria below are corroborated by three independent secondary summaries — NICE CKS, Cancer Research UK's NG12 referral summary, and GPnotebook [31,32,33].

Load-bearing, machine-checkable examples (as summarized by NICE CKS, Cancer Research UK, and GPnotebook [31,32,33]):

- Unexplained lump or enlarged lymph node anywhere on the body → suspected cancer pathway referral
- Unexplained bleeding of any site (haemoptysis with other symptoms, rectal bleeding with change in bowel habit, post-menopausal bleeding, haematuria with age-dependent thresholds) → referral
- Dysphagia → upper-GI endoscopy referral (2-week wait)
- New unexplained weight loss, appetite loss, night sweats → age/combination-dependent referral
- Two or more unexplained symptoms from (cough, fatigue, breathlessness, chest pain, weight loss, appetite loss) — or one of these in a person **over 40 who has ever smoked** → chest X-ray (lung-cancer rule) [33]
- New headache with neurological signs → urgent neuro imaging referral
- Unexplained petechiae/bruising in adults → urgent bloods
- Safety-netting is an explicit NG12 requirement: if referral is not indicated, arrange review if symptoms persist or progress [31].

**Translation note:** NG12 criteria are conjunctions of (symptom, age band, persistence, smoking status). A keyword list cannot express "post-menopausal bleeding"; a structured engine needs patient attributes (age, sex, pregnancy status, smoking history) joined to symptom predicates.

### 1.2 Sepsis — red flags, the Sepsis Six, and NEWS2 linkage

The UK Sepsis Trust and NICE NG51 use a two-tier scheme. **Red-flag sepsis** = presumed infection **plus any one** of [8,9,10]:

- New confusion or altered mental state (**ACVPU** score C or worse)
- Respiratory rate ≥ 25/min (or new oxygen requirement to keep SpO₂ ≥ 92%)
- Heart rate ≥ 130/min
- Systolic BP ≤ 90 mmHg
- Not passed urine ≥ 18 hours (urine output < 0.5 ml/kg/h)
- Mottled/ashen skin, cyanosis, or non-blanching rash
- Temperature < 36 °C
- Recent chemotherapy (neutropenic-risk presentation)

Presence of any red flag triggers the **Sepsis Six** within one hour (blood cultures; IV antibiotics; IV fluids; serum lactate; urine-output monitoring; oxygen to SpO₂ ≥ 94%) [8,9]. The UK Sepsis Trust's Sepsis Manual (7th edition, 2024) additionally treats **lactate ≥ 4 mmol/L** as a biochemical red flag [9]. NICE's 2024 NG254 evidence review retains the same red-flag thresholds for risk stratification, with NEWS2 ≥ 5 as the trigger for urgent review [10].

**Consumer-system translation:** the patient-verifiable subset (new confusion, mottled skin, no urine for 18 h, temp < 36 °C, "worst-ever" systemic illness with fever) is directly askable in a symptom checker; the rest (SBP, HR, RR) require either self-reported vitals or a NEWS2-style numeric intake (Section 2.2).

### 1.3 NEWS2 — the numeric deterioration gate

The Royal College of Physicians' NEWS2 (December 2017) aggregates **six physiological parameters** — respiration rate, oxygen saturation (two scales, including a hypercapnic-respiratory-failure scale new in NEWS2), systolic BP, pulse, level of consciousness (ACVPU with "new confusion" added in NEWS2), and temperature — each scored 0–3 [5,6,7]. Clinical response thresholds (corroborated by RCP training material, NICE MIB205, and HF Online training summaries [5,6,7]):

| Aggregate score | Risk | Required response |
|---|---|---|
| 0 | Low | Minimum 12-hourly observation |
| 1–4 | Low | Registered-nurse assessment; 4–6-hourly observations |
| **3 in any single parameter** | — | Urgent review regardless of aggregate |
| 5–6 | Medium | Urgent clinician review; 1-hourly observations; sepsis screen |
| **≥ 7** | High | **Emergency response** — critical-care-competent team; continuous monitoring |

NEWS2 is the single most portable numeric safety gate for a consumer tool: it converts six self-reportable quantities into one triage decision, and it is already the UK's standard for deterioration detection in and out of hospital [5,7].

### 1.4 Chest pain — NICE CG95 typicality rule

NICE CG95 (*Chest pain of recent onset*) defines [11]:

- **Typical angina** — all three of: (1) constricting discomfort in front of chest/neck/shoulders/jaw/arms; (2) precipitated by physical exertion; (3) relieved by rest or GTN within ~5 minutes.
- **Atypical angina** — two of the three.
- **Non-anginal** — one or none.

Suspected ACS (acute, unstable features) → **call 999 for an emergency ambulance** rather than self-transport [11]. A consumer checker must treat the 3/2/1 rule as an intake question battery, and must hard-override any benign verdict when acute features (diaphoresis, radiation, breathlessness) co-occur.

### 1.5 Stroke — FAST / BE-FAST and NICE NG128

The NHS Act FAST mnemonic — **F**ace drooping, **A**rm weakness, **S**peech difficulty, **T**ime to call 999 — is the UK public-facing standard [12]. BE-FAST adds **B**alance (sudden loss of coordination) and **E**yes (sudden vision loss); it was introduced because FAST misses posterior-circulation strokes — in the derivation analysis 42% of missed strokes had gait imbalance/leg weakness and 40% had visual symptoms [13]. NICE NG128 (*Stroke and TIA in over 16s*, May 2019) governs prehospital recognition and mandates emergency response for suspected acute stroke [12,34]. Any FAST/BE-FAST hit in a consumer tool must terminate the conversation and route to 999/911 with one-tap calling.

### 1.6 Suicide risk — PHQ-9 item 9 is not enough; C-SSRS structure

PHQ-9 item 9 ("Thoughts that you would be better off dead or of hurting yourself in some way") is a widely used screen but is **insufficient alone**: validation work shows limited utility against gold-standard measures (Na et al. 2018) and poor validity at the standard cutoff when compared with the C-SSRS (Chung et al. 2023); Viguera et al. (2015) further found item 9 "generated much higher rates of apparently false-positive findings than the" C-SSRS [14,15]. The C-SSRS (Columbia Protocol) screener — recommended by FDA-cited guidance and embedded in NIMH toolkits — is a minimum-two, maximum-six question adaptive screen (confirmed on cssrs.columbia.edu, fetched Oct 2026) [14,16]:

1. "Have you wished you were dead or wished you could go to sleep and not wake up?"
2. "Have you actually had any thoughts of killing yourself?"
   - If YES: "Have you been thinking about how you might do this?"
3. "Have you had these thoughts and somewhat intended to carry them out?" (intent)
4. "Have you started to work out or worked out the details of how to kill yourself? Do you intend to carry out this plan?" (plan)
5. "Have you ever done anything, started to do anything, or prepared to do anything to end your life?" (behavior)

A "YES" to Q2 or above triggers a defined response path: immediate risk stratification, safety planning (Stanley-Brown model), lethal-means counseling, warm handoff, and provision of a 24/7 crisis line (988 in the US; Samaritans 116 123 in the UK) [14,16]. The NIMH Brief Suicide Safety Assessment workflow requires follow-up within 48 hours for any positive screen and emergency psychiatric evaluation for higher-severity answers [16]. **Design implication:** a chatbot must detect ideation lexically (including indirect phrasing: "I don't want to be here anymore", "everyone would be better off without me") and route to a crisis card *before* completing any other reasoning — ChatGPT Health's failure to detect suicidal ideation in the Nature Medicine evaluation [1,2] is the cautionary baseline.

---

## 2. Triage Protocols: What a Consumer System Must Get Right

### 2.1 Manchester Triage System (MTS) — discriminators and documented weakness

MTS assigns one of five priorities via presentation-specific flowcharts and *discriminators* [35,36]:

| Colour | Category | Target time to treatment |
|---|---|---|
| Red | Immediate | 0 min |
| Orange | Very urgent | 10 min |
| Yellow | Urgent | 60 min |
| Green | Standard | 120 min |
| Blue | Non-urgent | 240 min |

Core discriminators: life threat (airway compromise, severe respiratory distress), haemorrhage (uncontrolled/major), pain (graded by severity/persistence), unconsciousness/altered consciousness, plus temperature, heart rate, and mechanism of injury; the highest discriminator present sets the category [35,36]. **Documented failure modes (all figures verified against primary sources or a 2026 systematic review):** MTS sensitivity varies sharply by outcome — 79.4% (95% CI 74.5–84.3) for urgent codes in a 3,002-evaluation non-traumatic-headache cohort, with specificity 54.1% (Brigo et al. 2022, *Journal of Clinical Nursing*, single-centre observational — **not** a meta-analysis, correcting an earlier draft of this dossier) [17]; 61.5% (95% CI 39.3–79.8) for sepsis (Gräff 2017) and 75.0% for life-saving interventions (Gräff 2019), per the 2026 systematic review by Djordjevic et al., which also reports "Under-triage mainly occurs in the MTS categories orange and yellow" and pediatric MTS AUC ≈ 0.7 with sensitivity 57% (Aeimchanbanjong 2017) [74]. Seiger et al. (2011, *Archives of Disease in Childhood*, n=13,408 children) found 0.9% (119) under-triage, of which experts judged 53% (63/119) clinically severe, with "unwell child" and dyspnoea presentations over-represented [18]. Lesson: even structured, clinician-operated discriminators miss a material share of urgent patients, and miss rates blow up for specific syndromes (sepsis, headache, posterior-circulation stroke); consumer tools must be more conservative at the emergency boundary and must not cap or early-exit their questioning.

### 2.2 ESI (Emergency Severity Index) v4 — the algorithmic pattern

ESI v4 (AHRQ-published, the dominant US five-level ED triage algorithm) is a decision tree, not a keyword list [37,38]:

- **ESI-1:** requires an *immediately life-saving intervention* (intubation, defibrillation, emergent medication, massive fluids).
- **ESI-2:** *high-risk situation*, should not wait — explicitly includes **new confusion, lethargy, or disorientation**, severe pain/distress, risk of airway compromise; danger-zone vital signs.
- **ESI-3:** two or more resources predicted; **ESI-4/5:** one or zero resources [37,38].

The ESI pattern maps cleanly onto AegisMed's existing `TRIAGE_FROM_SEVERITY` frontend mapping (`critical→ESI-1 … low→ESI-4`, `frontend/src/components/diagnosis/DiagnosisResults.tsx:54-59`) — but ESI-2's "high-risk situation" arm means *any* of a list of qualitative flags forces Level 2 *regardless of the computed severity*. AegisMed currently has no such override arm.

### 2.3 NHS 111 / NHS Pathways — life-threat-first flow and real failure modes

NHS Pathways (used by NHS 111, 111 online, and UK ambulance services) structures assessment as "an interlinked series of algorithms – or pathways – that link questions and care advice, leading to clinical endpoints," with **life-threatening symptoms assessed at the start of the call** (potentially triggering an ambulance) before lower-urgency branching toward skill-based dispositions (ambulance / clinical-assessment callback / GP / pharmacy / self-care); the report also stresses the system "is not a diagnostic system; rather, it assesses a patient's symptoms at the time of the call" [21,39]. The Healthcare Safety Investigation Branch's 2022 investigation of NHS 111 documented failure modes every consumer triage designer should internalize [21]:

- **Comorbidity blindness:** "The CRS algorithm did not allow for an assessment of caller's comorbidities to establish whether a clinical assessment would be beneficial."
- **Escalation under-firing:** patients with Covid symptoms and risk conditions should have been escalated to a clinician; "However, some patients did not receive a clinical assessment."
- **Self-report trap:** an "overreliance on the Patient's description of their breathlessness as an objectively reportable symptom" (silent hypoxia) — a clinician documented "No red flags" for a patient with laboured breathing and cold hands; the investigation highlights "the importance of pulse oximetry" to identify silent hypoxia.
- **Messaging that suppresses re-contact:** strong "stay at home" messaging "may have impacted on patients' willingness to seek medical advice from elsewhere, even if their condition deteriorated"; safety observation **O/2022/190** explicitly requires review of triage software and safety-netting language "to ensure the language used by health advisors does not deter seriously unwell people from calling back."
- **Remote-assessment ceiling:** clinicians "cannot examine patients, run tests or see body language" — remote assessment must therefore be biased toward escalation, not precision.

These are precisely the failure modes of a keyword-triggered safety layer: it never probes comorbidity, never distinguishes patient from third-person mentions, and its advice text can pacify rather than mobilize.

---

## 3. Safety Layers in Deployed Systems

### 3.1 Ada, Babylon, Symptomate, Healthily — measured, not marketed

The strongest public evidence on deployed safety layers is the Sutaria et al. audit (BMC Health Services Research, 1 Oct 2025), which inputted 51 GP-on-call vignettes (14 requiring emergency triage; 77 red-flag symptoms among the remainder) twice each into Ada, Babylon (as then available), Symptomate, and Healthily — 408 outputs total [4]:

| System | Red-flag question coverage | Note |
|---|---|---|
| Healthily | 60.4% | Best of four; still far below PCPs |
| Babylon | 42.9% | — |
| Ada | 26.6% | Market leader; near-bottom on coverage |
| Symptomate | 17.5% | Worst |
| **PCP comparator** | **71.8%** | p < 0.001 |

Aggregate checker emergency-triage sensitivity was **76.9%** (individual range 52–93%: Ada 92.9%, Healthily 80.8%, Symptomate 82.1%, Babylon 52.0%) vs PCPs' 85.7% (not statistically different), but checkers were significantly **less specific** (83.3% vs 91.9%, p = 0.024) — they over-triage benign cases while missing red-flag *questions*. Note the decoupling: Ada pairs the best emergency sensitivity (92.9%) with near-bottom question coverage (26.6%) — high sensitivity on *presented* symptoms cannot compensate for red flags the system never asks about. The authors' verdict: "OSCs in their current form do not adequately seek red flags," raising "concerns about their safety and effectiveness in primary care" [4].

Company-side descriptions: Ada frames itself as a triage (not diagnostic) tool that flags "red-flag symptoms that would require urgent medical assessment" during a structured interview [40]; Babylon claimed an 85% appropriateness / 93% safety score in its own studies while some of its in-house physicians raised accuracy concerns reported by Forbes in 2018 [41]; Buoy instructs users that for emergency signs (chest pain, difficulty breathing, altered consciousness, suicidal thoughts) they should not wait for the tool's conclusion, and presents care options including the ER [42]. All three descriptions describe *safety nets layered on top* of symptom logic — the same architecture AegisMed needs, minus the measurement.

### 3.2 Google / YouTube crisis-resource routing — the consumer escalation pattern

Google Search and YouTube apply a "help panel over removal" design: queries about suicide/self-harm trigger a prominent **crisis information card at the top of results** — Google's own blog confirms prevention resources are shown "at the top of search results" for suicide-related queries, with the US card routing to call/text **988** and chat at 988lifeline.org [22,75]; helplines are localized by country (support.google.com/websearch/answer/11181469); YouTube overlays equivalent Crisis Resource Panels — "supportive resources such as phone numbers of suicide prevention organizations" (verbatim from the fetched policy page) — on policy-adjacent videos per its Suicide & Self-Harm policy, as an alternative to removal [22,23]. The FCC separately mandates georouting so 988 callers reach their local crisis center [23]. **Transferable design facts:** (a) the intervention is an *action affordance* (call/text/chat buttons), not an informational disclaimer; (b) it fires on query intent, before any content is consumed; (c) routing is jurisdiction-localized. No third-party compliance-rate study of the Google crisis card was found (UNKNOWN — evidence gap), but the pattern's ubiquity across platforms with maximal legal exposure is itself signal.

---

## 4. Human Factors & UI Safety

### 4.1 Do users read disclaimers? Mostly no, and they don't change behavior

- Health-website disclaimers exist to inform users that content is not medical advice, but there is no robust evidence they change subsequent behavior (Charbonneau 2015 review) [43].
- An evidence audit of Apple App Store diagnosis apps found **72% (48/67) include a "not medical advice" disclaimer** — i.e., disclaimers are the compliance default, not a differentiator, and their ubiquity plausibly breeds banner blindness [44].
- The disclaimer is disappearing precisely where the risk is highest: research reported by MIT Technology Review (Jul 2025) found major AI chatbots included medical disclaimers in ~**26%** of health responses in 2022 but **under 1%** by 2025 — AI companies "have stopped warning you that their chatbots aren't doctors" [76].
- Behavioral-disclaimer research outside health (digitally modified images) found labels were "not helpful for their intended purpose" — users processed them and behavior did not change [45].
- General UX/legal literature (browsewrap, EULA skimming) consistently shows users skip dense advisory text; Claggett et al. (2022) show advice acceptance is driven by source credibility and tone, not by disclaimer presence [46].
- **The strongest negative evidence is real-world:** HSIB found NHS 111's reassuring "stay at home" messaging deterred deteriorating patients from re-seeking care [21].

**Conclusion (3+ sources [21,43,44,45,46,76]):** treat the disclaimer as a legal artifact, never as a safety control. Safety must be carried by targeted, structured, action-first interventions.

### 4.2 Warning design that does change behavior — Wogalter's compliance model

Decades of warning research (Wogalter & Laughery) establish that a warning changes behavior only when it combines [19,20]:

1. A **signal word** with severity semantics — DANGER (grave/imminent), WARNING, CAUTION — plus color coding (red/orange/yellow);
2. An explicit **hazard statement** ("this may be a heart attack");
3. A **consequence statement** ("waiting can be fatal");
4. A **specific instruction** ("call 911 now — tap the button below");
5. **Prominence** — placed where the behavior decision happens, not buried in a footer.

This is the evidence-backed template for AegisMed's escalation UI: each red-flag tier should render as signal word + hazard + consequence + one-tap action, positioned at the top of the results view.

### 4.3 Anthropomorphism and over-reliance — 2023–2026 evidence

- **Oxford, May 2025 (Mahdi et al.):** participants using GPT-4o/Command R+/Llama 3 on mock medical scenarios identified the correct condition only ~1/3 of the time and the cause ~45% of the time — *worse* than unassisted participants — with many downplaying serious conditions after reading chatbot output; Mahdi described a "two-way communication breakdown" (users type too little detail; outputs mix good and bad advice), producing overreliance on incorrect answers [47,48].
- **MIT Media Lab, May 2025 (NEJM AI):** people **overtrust AI-generated medical advice even when it is inaccurate**, and the disappearance of disclaimers compounds this — direct evidence that trust calibration cannot be left to model behavior [77].
- **Oxford follow-up, Feb 2026 (1,300 participants, largest to date):** LLMs were no better than standard web search at guiding users to correct health decisions [49].
- Chatbot empathy is itself a hazard: Danish researchers and a Sanford Health specialist warn chatbots can sound comforting while missing real clinical danger [50]; a 2025 study reported chatbots routinely violating mental-health ethics standards in crisis handling [51].
- Anthropomorphic design research (Chen et al. 2025; healthcare avatar studies) shows human-like presentation increases trust in advice independent of its quality — an amplifier for over-reliance [52,53].

**Design consequences for AegisMed:** (a) do not name/personify the agent as a clinician-like persona; (b) phrase outputs as conditional ("if X, seek care now") rather than verdicts; (c) measure over-reliance in evaluation — did the user's intended care-seeking *match* the acuity of the case?

### 4.4 Dark patterns

- Gunawan et al. (FTC PrivacyCon 2022) found **95% of studied apps contained dark patterns** steering users against their interests [54].
- A 2024 review of dark patterns in digital health catalogs nagging, obstruction, sneaking, and forced engagement/notifications as endemic, with elevated ethical stakes for vulnerable health users [55,56].
- Relevant inverse reading for AegisMed: the same levers that manipulate engagement (persistence, prominence, one-tap actions) are exactly what safety escalation needs. The ethical line is target: use dark-pattern-grade salience *only* for user-protective actions (calling 911/988, contacting a clinician), never for retention.

---

## 5. Safety Evaluation: Coverage, Adversarial Testing, Benchmarks

### 5.1 Accuracy ≠ safety: the "safety coverage" concept

Semigran et al. (BMJ 2015; 23 checkers, 45 vignettes) set the baseline: correct diagnosis listed first in 34% of cases; appropriate triage advice in **57%** (95% CI 52–61); notably, checkers advised appropriate urgent care in ~80% of emergent cases but over-referred low-acuity ones [57]. Sutaria 2025 decomposed the safety construct further: a checker can be decent at emergency *triage* (76.9%) while asking only 36.9% of red-flag *questions* — the questioning coverage is the leading indicator of latent risk [4]. **Define safety coverage for AegisMed as:** for a benchmark set of emergencies, the fraction of guideline red-flag questions the system poses (or resolves) before outputting a disposition. Target: ≥ 70% (the PCP benchmark [4]).

### 5.2 Independent evaluations of frontier products (2025–2026)

- **EUSEM 2025 (European Emergency Medicine Congress):** AI triage tool sensitivity 58.3% for true urgent cases vs nurses 73.8%; doctors higher still [3].
- **ChatGPT Health (Nature Medicine, 23 Feb 2026; first independent safety evaluation, 960 triage responses):** under-triaged **51.6%** of physician-adjudicated emergencies; frequently failed to detect suicidal ideation; adequate only on the most obvious presentations [1,2].
- **ECRI Top 10 Health Technology Hazards for 2026:** #1 = "The Misuse of AI Chatbots in Healthcare," with ECRI receiving "dangerously inaccurate information" when testing LLMs on medical-product questions [58].

### 5.3 Red-team benchmarks for medical LLMs

- **MedSafetyBench (Han et al., NeurIPS 2024; arXiv:2403.03744):** "the first benchmark dataset designed to measure the medical safety of LLMs," built on AMA Principles of Medical Ethics, of adversarial queries eliciting unsafe outputs; headline finding: "publicly-available medical LLMs do not meet standards of medical safety," and fine-tuning on MedSafetyBench improves safety while preserving capability [59,60]. Dataset public (github.com/AI4LIFE-GROUP/med-safety-bench) [60].
- **HealthBench (OpenAI, May 2025):** 5,000 realistic health conversations graded against physician-written rubrics that include explicit safety criteria, plus a 1,000-example "Hard" subset on which top models historically scored below ~32% — i.e., failure rates above ~68% on the hardest health-safety examples [61].
- Complementary 2025 frameworks: multi-domain medical red-teaming protocols, MedOmni-45°, and the Health AI Partnership practitioner guidance [62].
- **Gap (UNKNOWN):** little published work exists on *deliberately adversarial users* who minimize or misstate symptoms to bypass emergency detection in symptom checkers; most benchmarks test unintentional ambiguity. AegisMed should treat user-minimization ("I'm probably fine, but…", "it's probably nothing, just…") as a standard test dimension regardless [63].

### 5.4 WHO / ITU / reporting standards

- **WHO (Jan 2024), *Ethics and governance of AI for health: Guidance on large multi-modal models*** — 98 pages, **40+ recommendations** for governments/developers/providers; explicitly covers LMM chatbots answering patients' written queries; core risks: "false, inaccurate, or biased" (hallucinated) outputs with serious health-decision consequences; recommendations center on transparency, human oversight, independent audit, and **post-deployment monitoring** [64,65].
- **ITU/WHO FG-AI4H** benchmarking deliverables define validation/evaluation requirements for health AI [66].
- **CHART (Chatbot Assessment Reporting Tool, 2025):** reporting guideline for health-chatbot evaluation studies — a ready-made template for AegisMed's evaluation write-up [67].

---

## 6. Specific Populations: Concrete Gating Rules

### 6.1 Pregnancy

**Urgent maternal warning signs (CDC "Hear Her" campaign — verbatim list; "seek medical care immediately")** [24]:

> "Severe headache that won't go away or gets worse over time." · "Dizziness or fainting." · "Thoughts about harming yourself or your baby." · "Changes in your vision." · "Fever of 100.4º F or higher." · "Extreme swelling of your hands or face." · "Trouble breathing." · "Chest pain or fast-beating heart." · "Severe nausea and throwing up (not like morning sickness)." · "Severe belly pain that doesn't go away." · "Baby's movement stopping or slowing down during pregnancy." · "Vaginal bleeding or fluid leaking during pregnancy." · "Heavy vaginal bleeding or leaking fluid after pregnancy." · "Swelling, redness, or pain of your leg." · "Overwhelming tiredness."

**Medication gating:** FDA (Oct 2020) recommends avoiding NSAIDs (incl. OTC ibuprofen/naproxen) at **≥ 20 weeks** due to oligohydramnios/fetal kidney risk; contraindicated at **≥ 30 weeks** (ductus arteriosus risk); first-trimester use linked to miscarriage risk [25]. Paracetamol/acetaminophen is the default OTC analgesic in pregnancy [25]. **Gating rules for AegisMed:** collect pregnancy status + gestational age up front; hard-block NSAID recommendations at ≥ 20 weeks; route all 15 Hear Her signs to same-day obstetric/maternity assessment with postpartum variants included.

### 6.2 Pediatrics — why adult checkers break

NICE NG143 (*Fever in under 5s*) uses an age-banded traffic-light system [26,27]:

| Band | Red (high risk) | Amber (intermediate) |
|---|---|---|
| **< 3 months** | **Temperature ≥ 38 °C** → immediate specialist care/sepsis pathway; **temperature < 36 °C** also red (NHS implementations of NG143) | — |
| **3–6 months** | — | **Temperature ≥ 39 °C** → urgent face-to-face assessment |
| All under 5 | Pale/mottled/blue; no response to social cues; weak cry/grunting; non-blanching rash; reduced conscious level; bile-stained vomiting | Pallor; not responding normally; dry mucous membranes; poor feeding; reduced urine output |

Any single red feature → immediate specialist care; any amber feature → face-to-face urgent assessment [26,27]. The traffic-light rule is itself imperfect — a validation study found it missed a substantial share of serious bacterial infections, particularly UTIs [68] — which argues for *more* conservatism, not less, in children. Two further breaks with adult logic: pediatric antipyretic dosing is **weight-based, not age/fixed-dose** [69], and NICE NG143 advises antipyretics only if the child appears distressed — never both paracetamol and ibuprofen routinely, never to suppress the temperature number per se [26]. Dedicated pediatric checkers (e.g., CHOP, Children's National) exist precisely because adult symptom mappings mislead at these ages [70]. **Gating rules:** age < 18 → switch to pediatric symptom/age-band logic; < 3 months + fever (≥ 38 °C or < 36 °C) → emergency; never emit adult OTC dose guidance for children.

### 6.3 Elderly / polypharmacy

- Older adults with sepsis commonly present **atypically** — most often altered mental status/confusion rather than fever; falls, functional decline, weakness, and new incontinence are frequent atypical presentations (falls in 71% of one atypical-presentation case series) [28,29].
- Polypharmacy (commonly defined as > 5–10 medications) blunts the physiologic responses triage relies on — beta-blockers mask tachycardia, antipyretics mask fever [30].
- Validated screening tools exist: STOPP/START (v3, 2023, O'Mahony et al., *Age and Ageing*) for potentially inappropriate prescriptions and prescribing omissions; STOPP-Frail for frail patients [71,72].

**Gating rules:** age ≥ 65 (or reported polypharmacy ≥ 5 medications) → treat new confusion, falls, or functional decline as infection-tier red flags even without fever; suppress numeric-reassurance when vitals are unreliable; recommend medication-list review rather than adding OTC advice on top of unknown regimens.

---

## Red-Flag Minimum Set (symptom pattern → required action)

| # | Symptom pattern (machine-checkable) | Required action (tier) | Source(s) |
|---|---|---|---|
| 1 | Any expression of suicidal ideation, self-harm intent, or "wish to be dead" (incl. indirect: "everyone would be better off without me") | **T0** — terminate triage; show crisis card (988/911 US; Samaritans 116 123 UK) with one-tap call/text; do not generate medical content | C-SSRS screener [14,15]; 988/crisis-card design [22,23]; ChatGPT Health SI failure as baseline risk [1,2] |
| 2 | FAST positive: facial droop, unilateral arm weakness, speech disturbance — or BE-FAST additions (sudden balance loss, sudden vision loss) | **T0** — 999/911 immediately, one-tap call; no self-transport | NHS Act FAST [12]; Aroor 2017 [13]; NICE NG128 [34] |
| 3 | Chest pain with any of: typical-anginal features (CG95 3-feature rule), radiation to arm/jaw/neck, diaphoresis, breathlessness, exertional | **T0** — call 999/911 (not self-transport); ECG-level urgency | NICE CG95 [11]; Buoy emergency-sign set [42] |
| 4 | Infection presumed + any: new confusion (ACVPU ≥ C), RR ≥ 25 (self-report), SBP ≤ 90 (if known), HR ≥ 130, temp < 36 °C, mottled/non-blanching rash, no urine ≥ 18 h, recent chemotherapy | **T0** — emergency; sepsis pathway framing | UK Sepsis Trust red flags [8,9]; NICE NG51/NG254 [10] |
| 5 | Aggregate NEWS2-style score ≥ 7, or any single parameter scoring 3 (e.g., new confusion alone) | **T0** — emergency response | RCP NEWS2 [5,6,7] |
| 6 | NEWS2-style score 5–6 | **T1** — urgent same-day clinician review; run sepsis screen | RCP NEWS2 [5,6,7]; NICE MIB205 [6] |
| 7 | NICE NG12 cancer red flags: unexplained lump/lymphadenopathy, unexplained bleeding (site/age rules), dysphagia, unexplained weight loss, post-menopausal bleeding, ≥2 unexplained symptoms (or 1 if >40 & ex-smoker) | **T1** — suspected-cancer-pathway / urgent GP referral language (28-day pathway) | NICE NG12 [31,32,33] |
| 8 | Any pregnancy/postpartum CDC Hear Her sign (15-item verbatim list above) | **T1** — same-day obstetric/maternity assessment; postpartum variants | CDC Hear Her [24] |
| 9 | Pregnancy ≥ 20 weeks + NSAID recommendation context | **Gate** — block NSAID advice (contraindicated ≥ 30 wks) | FDA drug safety alert [25] |
| 10 | Age < 3 months with fever ≥ 38 °C or temperature < 36 °C | **T0** — immediate emergency assessment | NICE NG143 [26,27]; NHS fever pathways |
| 11 | Age 3–6 months with fever ≥ 39 °C, or any under-5 red feature (non-blanching rash, grunting, reduced consciousness, bile-stained vomiting) | **T1** — urgent face-to-face pediatric assessment | NICE NG143 [26,27] |
| 12 | Age ≥ 65 or polypharmacy (≥ 5 meds) + new confusion, fall, or functional decline ± infection signs | **T1** — urgent assessment; treat as atypical sepsis risk | Clifford 2016 [28]; SAEM [30]; STOPP/START [71] |
| 13 | Uncontrolled major bleeding; unconsciousness; anaphylactic-type presentation (lip/tongue swelling, throat tightness) | **T0** — emergency | MTS discriminators (life threat, haemorrhage, unconsciousness) [35,36] — anaphylaxis row: WEAK-EVIDENCE (not independently fetched; standard NHS guidance) |
| 14 | Vitals danger-zone self-report (any ESI-1 "immediately life-saving intervention" context, e.g., "can't breathe", unresponsive) | **T0** — emergency | ESI v4 [37,38] |

---

## Implications for AegisMed

Grounded in the actual codebase (paths verified October 2026):

1. **Replace `SAFETY_KEYWORDS` with a structured red-flag engine.** `src/api/routes/chat.py:22-26` holds 12 flat strings matched by `keyword in msg_lower` (lines 76–84). This misses negation and third-person mentions ("my dad had a stroke" currently fires an emergency alert), misses unlisted emergencies ("thunderclap headache", "water broke", "blood in stool", "worst headache of my life", indirect suicidality: "I don't want to be here anymore"), and cannot express conjunctions. Create `src/safety/red_flags.py` with tiered, structured rules: each rule = `{rule_id, tier: T0|T1|T2, pattern: regex/phrase set, negation-guard, requires: patient attributes (age, pregnancy status, gestational age), action, message_key, source_refs}` implementing the 14-row minimum set above. Emit structured `RedFlagHit` objects, not a boolean.
2. **Make escalation drive follow-up questions (safety coverage), not just output flags.** Sutaria 2025's core finding is that checkers fail by *not asking* [4]. The engine in `src/safety/red_flags.py` should expose `missing_red_flag_questions(context)` that the NLP/synthesis pipeline uses to ask 1–2 targeted follow-ups (fever? new confusion? chest-pressure radiation? last menstrual period?) before finalizing. Track coverage: fraction of benchmark red-flag questions asked, target ≥ 70%.
3. **Add a NEWS2-style scoring agent under `src/agents/`.** New `src/agents/vitals/agent.py`: intake of RR, SpO₂, SBP, HR, temperature, ACVPU self-report; output aggregate score with bands (0 / 1–4 / 5–6 / ≥7 / single-param-3) mapped to T1/T0 actions per RCP [5,6,7]. Wire into `doctor_alert` logic.
4. **Un-harden and un-cap the red-flag/doctor-alert path.** In `src/agents/rule_based_synthesis.py`: `_build_red_flags` (lines 325–340) does naive substring matching and truncates to `flags[:3]` — never truncate safety output; and `doctor_alert = severity in ("critical","high") or len(red_flags) > 0` (line 199) collapses structured risk into one boolean. Replace with a structured `escalation` object `{tier, triggers[], action, rationale[], coverage_gaps[]}` carried through the API response.
5. **Fix the severity-vocabulary mismatch and fail-soft default.** `src/agents/nlp/agent.py:253-262` `_assess_severity` returns `"mild"|"moderate"|"high"` while `frontend/src/lib/api.ts:393-397` `normalizeSeverity` accepts `"critical"|"high"|"moderate"|"low"` and **defaults unknown values to "moderate"** — a fail-soft default on a safety-bearing field. Invert it (unknown → highest-suspicion handling or explicit re-ask), and unify the two severity vocabularies through one shared enum.
6. **UI: action-first escalation panels instead of disclaimers.** In `frontend/src/components/diagnosis/DiagnosisResults.tsx`, `TRIAGE_FROM_SEVERITY` (lines 54–59) renders severity badges; per Wogalter [19,20] and the Google crisis-card pattern [22,23], T0/T1 results must render a top-of-card panel with: signal word (EMERGENCY/URGENT), hazard statement, consequence statement, and a **one-tap action button** ("Call 911", "Call 988", "Find urgent care") localized by jurisdiction — not a text notice. Show the same panel in `chat.py`-fed conversations when `safety_alert` fires; keep the `DISCLAIMER` (chat.py:29) as legal footer only. Avoid clinician-persona styling (anthropomorphism risk) [52,53].
7. **Population gates.** Use the existing `patient_context` (age already flows through `downloadReport`, `DiagnosisResults.tsx:187`) to add: pregnancy status + gestational age question; block NSAID advice ≥ 20 weeks [25]; pediatric branch (< 18) switching to NG143 age-banded fever logic (< 3 mo ≥ 38 °C → T0) and weight-based dosing language only [26,27]; ≥ 65 / polypharmacy branch treating new confusion/falls as sepsis-tier flags [28,30].
8. **Suicide-crisis path in chat independent of the LLM.** ChatGPT Health failed SI detection [1,2]; `SAFETY_KEYWORDS` catches only "suicidal". Add the C-SSRS-derived lexical screen (Q1–Q5 constructs + indirect phrasings) as a T0 pre-LLM gate in `send_message` that returns the crisis card and *skips* normal generation.
9. **Adversarial safety test suite as a release gate.** New `tests/test_safety_redteam.py`: (a) Semigran's 45 public vignettes (Zenodo, doi:10.1136/bmj.h3480) [57] with assertion "every emergent vignette escalates"; (b) MedSafetyBench-style adversarial prompts [59,60]; (c) user-minimization variants ("I'm probably fine but…"), negation/third-person variants, and pediatric/pregnant variants of each T0 pattern; (d) a CI-asserted safety-coverage metric. Also assert *no* escalation fires on benign negation cases to bound over-triage (Sutaria showed checkers already over-triage: 83.3% vs 91.9% specificity [4]).
10. **Safety netting + post-market monitoring hooks.** Every non-T0 response must include Jones-BJGP-style safety netting: expected course, worrying symptoms to watch, and a concrete "seek care if…" threshold [73]; log every `RedFlagHit` (rule_id, tier, disposition shown) to support WHO-recommended post-deployment monitoring [64,65] and CHART-style evaluation reporting [67].

---

## Sources

1. ChatGPT Health independent safety evaluation (Mount Sinai; *Nature Medicine*, 23 Feb 2026) — under-triaged 51.6% of gold-standard emergency cases, over-triaged 64.8% of non-urgent cases across 960 structured triage scenarios; inconsistently activated suicide-crisis safeguards; frequently failed to detect suicidal ideation. Coverage: Digital Health, 27 Feb 2026, https://www.digitalhealth.net/2026/02/chatgpt-health-fails-to-flag-over-50-of-medical-emergencies — "ChatGPT Health incorrectly triages more than half of medical emergencies"; Mount Sinai publication record: https://scholars.mssm.edu/en/publications/chatgpt-health-performance-in-a-structured-test-of-triage-recomme.
2. Practice Business coverage of same study, https://practicebusiness.co.uk/news-study-finds-chatgpt-health-misses-half-of-serious-medical-emergencies — "under-triaged 52% of gold-standard emergency cases"; adequate only on clearly obvious emergencies.
3. EUSEM 2025 (European Emergency Medicine Congress, Berlin, Sep–Oct 2025) study: AI triage tool sensitivity 58.3% for true urgent cases vs nurses 73.8%. Coverage: Nursing Times, 3 Oct 2025, https://www.nursingtimes.net/emergency-and-critical-care/nurses-are-better-than-artificial-intelligence-at-triaging-patients-03-10-2025; Hospital Health, 9 Oct 2025, https://www.hospitalhealth.com.au/content/technology/article/is-ai-better-than-doctors-and-nurses-at-triaging-ed-patients--219043256 — "Doctors still outperform AI in medical emergencies" (Yahoo/Euronews, 30 Sep 2025).
4. Sutaria S et al., "Evaluating the use of red flags by online symptom checkers," *BMC Health Services Research* 2025;25:1263, published 1 Oct 2025, https://pmc.ncbi.nlm.nih.gov/articles/PMC12486864/ — verbatim from fetched text: four UK OSCs (Ada, Babylon, Symptomate, Healthily); emergency-triage sensitivity "OSCs 76.9% (95% CI 59.3–87.9%) vs PCPs 85.7%"; specificity "83.3% vs 91.9% (p = 0.024)"; red-flag coverage "OSCs asked only 36.9% (95% CI 30.1–44.2%) of relevant red-flag symptoms vs 71.8% for PCPs (p < 0.001)"; per-system coverage Healthily 60.4%, Babylon 42.9%, Ada 26.6%, Symptomate 17.5%; "OSCs in their current form do not adequately seek red flags."
5. Royal College of Physicians, NEWS2 resource page, https://www.rcp.ac.uk/resources/national-early-warning-score-news-2 (updated Dec 2017) — "Six simple physiological parameters form the basis of the scoring system"; parameters: respiration rate, oxygen saturation (with hypercapnic scale new in NEWS2), systolic BP, pulse, consciousness (ACVPU, "new confusion" added), temperature.
6. NICE MIB205 (NEWS2 briefing), https://www.nice.org.uk/advice/mib205/chapter/The-technology — confirms six-parameter aggregate scoring; score 0 → minimum 12-hourly review. Threshold bands corroborated by HF Online NEWS2 guide (18 Aug 2026), https://uk.hfonline.org/news2-score-guide-healthcare-support-workers — "A NEWS2 score of 7 or above reaches the high-risk emergency-response threshold"; 1–4 low; 5–6 moderate; single-parameter 3 → urgent response.
7. NHS Scotland NEWS2 chart, https://www.rightdecisions.scot.nhs.uk/media/2564/news2-874.pdf (full scoring tables; PDF not machine-fetchable — bands corroborated across [5,6]).
8. NHS England patient safety alert on sepsis recognition, https://www.england.nhs.uk/2014/09/psa-sepsis (page gated; criteria corroborated via [9,10]).
9. UK Sepsis Trust, *Sepsis Manual*, 7th edition (Jul 2024), https://sepsistrust.org/wp-content/uploads/2024/07/Sepsis-Manual-7th-Edition-2024-V1.0.pdf — adult red-flag sepsis = presumed infection + any of: RR ≥ 25, new O₂ requirement to keep SpO₂ ≥ 92% (88% COPD), HR ≥ 130, SBP ≤ 90 mmHg (or drop > 40 from baseline), new confusion/altered mental state (ACVPU), mottled/ashen/cyanotic skin or non-blanching rash, not passed urine ≥ 18 h (< 0.5 ml/kg/h), temp < 36 °C, lactate ≥ 4 mmol/L (biochemical), recent chemotherapy (neutropenic risk); any red flag → Sepsis Six within 1 h. Criteria corroborated by Geeky Medics sepsis management summary and Plymouth University clinical paper (Mead 2018).
10. NICE NG254 (sepsis risk stratification evidence review, 2024) — retains red-flag thresholds; NEWS2 ≥ 5 triggers urgent review; ACVPU embedded. https://www.nice.org.uk/guidance/ng254 (via search summary).
11. NICE CG95, *Chest pain of recent onset* — typical angina = all three features (constricting discomfort chest/neck/shoulders/jaw/arms; precipitated by exertion; relieved by rest/GTN ~5 min); atypical = two; non-anginal = one/none; suspected ACS → call 999. https://www.nice.org.uk/guidance/cg95 (page blocked 403; criteria via implementation study PMC4336864 and guideline summaries).
12. NHS "Act FAST" stroke campaign (Face-Arms-Speech-Time; call 999 on any single sign), https://www.saltcoatsgrouppractice.scot.nhs.uk/act-fast-how-to-recognise-the-signs-of-a-stroke and nhs.uk/actFAST ("Face or Arm or Speech, at the first sign, it's Time to call 999"); NICE NG128 scope, https://www.nice.org.uk/guidance/ng128/documents/final-scope-2 (May 2019 guideline, prehospital recognition and triage).
13. Aroor S et al. (2017), "BE-FAST (Balance, Eyes, Face, Arm, Speech, Time) — reducing the proportion of strokes missed using the FAST assessment," *Stroke* (AHA), https://www.ahajournals.org/doi/full/10.1161/strokeaha.116.015169 — of strokes missed by FAST, 42% had gait imbalance/leg weakness, 40% visual symptoms (70% either); FAST misses up to 40% of posterior-circulation strokes; adding Balance and Eyes reduced unidentified strokes from 14.1% to 4.4%.
14. C-SSRS (Columbia Protocol), Columbia Lighthouse Project, https://cssrs.columbia.edu/the-columbia-scale-c-ssrs/ (fetched Oct 2026) — adaptive screener "condensed to a minimum of two and a maximum of six questions"; verbatim items: "Have you wished you were dead or wished you could go to sleep and not wake up?"; "Have you been thinking about how you might kill yourself?"; preparatory-behavior item ("collecting pills, getting a gun, giving valuables away, or writing a suicide note"); ideation severity Q1–5 + behavior; risk/level-of-care recommendations driven by yes/no answers plus recency and severity.
15. Na PJ et al. (2018), PubMed 29477096 — PHQ-9 item 9 "is an insufficient assessment tool" alone; Chung et al. (2023), PubMed 36181915 — poor validity of item 9 vs C-SSRS at standard cutoff; Viguera AC et al. (2015), *J Clin Psychiatry* / PubMed 26278339 — PHQ-9 item 9 "generated much higher rates of apparently false-positive findings than the" C-SSRS.
16. NIMH Brief Suicide Safety Assessment (BSSA) adult outpatient toolkit, https://www.nimh.nih.gov/sites/default/files/documents/research/research-conducted-at-nimh/asq-toolkit-materials/adult-outpatient/bssa-outpatient-adult-asq-nimh-toolkit.pdf — positive screen → follow-up call within 48 h; emergency psychiatric evaluation criteria; Stanley-Brown safety planning; 988 provision.
17. Brigo F, Turcato G, Zaboli A, et al. (2022), "The Manchester Triage System's performance in clinical risk prioritisation of patients presenting with headache in emergency department," *Journal of Clinical Nursing* 31(17-18):2553-2561, doi:10.1111/jocn.16073 — **single-centre retrospective observational study (n=3,002 triage evaluations), not a meta-analysis** (verified via PubMed abstract, Oct 2026): "The sensitivity of the MTS for urgent codes (yellow, orange and red) was 79.4% (95% CI 74.5-84.3), with a specificity of 54.1% (95% CI 52.9-55.3)."
18. Seiger N et al. (2011), "Undertriage in the Manchester triage system: an assessment of severity and options for improvement," *Archives of Disease in Childhood* 96(7):653-657, doi:10.1136/adc.2010.206797 — 13,408 children; 0.9% (119/13,408) under-triaged; 53% (63/119) judged clinically severe; dyspnoea and "unwell child" presentations over-represented among under-triaged children.
19. Wogalter MS (1987), "Effectiveness of warnings," *Human Factors* 29(5), https://journals.sagepub.com/doi/10.1177/001872088702900509 — effective warnings require signal word + hazard + consequence + instruction statements.
20. Wogalter MS & Laughery KR (1996), "WARNING! Sign and label effectiveness," https://www.safetyhumanfactors.org/wp-content/uploads/2022/09/104WogalterLaughery11996-copy.pdf — warnings serve to inform AND change behavior; DANGER/WARNING/CAUTION severity-color hierarchy (red/orange/yellow).
21. Health Services Safety Investigations Body (HSIB/HSSIB), *Response of NHS 111 to the Covid-19 pandemic*, investigation report, 29 Sep 2022, https://www.hssib.org.uk/patient-safety-investigations/response-of-nhs-111-to-the-covid-19-pandemic/investigation-report/ — verbatim (fetched): "an interlinked series of algorithms – or pathways – that link questions and care advice, leading to clinical endpoints"; "life-threatening symptoms are assessed at the start of the call"; "The CRS algorithm did not allow for an assessment of caller's comorbidities…"; "overreliance on the Patient's description of their breathlessness as an objectively reportable symptom"; clinician documented "No red flags"; "stay at home" messaging "may have impacted on patients' willingness to seek medical advice from elsewhere, even if their condition deteriorated"; observation O/2022/190: review safety-netting language so it "does not deter seriously unwell people from calling back"; clinicians "cannot examine patients, run tests or see body language."
22. YouTube "You Are Not Alone" (blog, Nov 2021) and Suicide/Self-Harm policy, https://support.google.com/youtube/answer/2802245 — Crisis Resource Panels shown on sensitive search queries/videos, linking to local confidential helplines (988 in US).
23. 988 Suicide & Crisis Lifeline (SAMHSA), https://988lifeline.org/ — "available 24/7/365… call, text, or chat"; FCC georouting mandate routes to local crisis centers; Crisis Text Line CONNECT→741741; IASP findahelpline.com for localization.
24. CDC "Hear Her" campaign — Urgent Maternal Warning Signs, https://www.cdc.gov/hearher/news-media/article-urgent-warning-signs.html — verbatim 15-item list reproduced in Section 6.1 (fetched); "Pregnant and postpartum women need to seek medical care immediately."
25. FDA Drug Safety Communication, 15 Oct 2020 — avoid NSAIDs at 20 weeks and later of pregnancy (oligohydramnios, fetal kidney issues); contraindicated ≥ 30 weeks (ductus arteriosus); first-trimester miscarriage risk. Corroborated by University of Utah Pharmacy alert, https://pharmacyservices.utah.edu/alerts/2020/10/fda-recommends-avoiding-use-of-nsaids-pregnancy-20-weeks-or-later-because-they-can; UpToDate, *Use and risks of NSAIDs in pregnancy*.
26. NICE NG143, *Fever in under 5s: assessment and initial management* (2019), https://www.nice.org.uk/guidance/ng143/chapter/recommendations — traffic-light system; full guideline text, https://www.ncbi.nlm.nih.gov/books/NBK552086 (26 Nov 2021); traffic-light table PDF: https://emsj.ca/wp-content/uploads/2023/12/NICE-Traffic-light-system-for-identifying-risk-of-serious-illness-of-children-5.pdf.
27. RCEM Learning, "A child with a fever" (12 Sep 2018), https://www.rcemlearning.co.uk/modules/a-child-with-a-fever-pem-induction — "NICE has a colour coded traffic light system… with 1 red or 1 amber [feature requiring assessment]"; < 3 months fever ≥ 38 °C = red; 3–6 months ≥ 39 °C = amber.
28. Clifford KM et al. (2016), "Challenges with Diagnosing and Managing Sepsis in Older Adults," https://pmc.ncbi.nlm.nih.gov/articles/PMC4804629/ — older adults "often present with atypical, nonspecific symptoms," most commonly altered mental status/confusion rather than fever.
29. Nederlands Tijdschrift voor Geneeskunde, atypical presentation in elderly — geriatric syndrome present in 99% of atypical presentations; falls most frequent (71%).
30. SAEM CDEM curriculum, "Atypical Presentations of Critical Illness in Older Adults," https://www.saem.org/about-saem/academies-interest-groups-affiliates2/cdem/for-students/online-education/m4-curriculum/group-m4-geriatrics/atypical-presentations-of-critical-illness-in-older-adults — "polypharmacy and medication effects can blunt or mask physiologic responses" (beta-blockers, antipyretics); Cleveland Clinic, polypharmacy ≈ >5–10 medications, https://consultqd.clevelandclinic.org/emergency-geriatricians-triage-older-adults-for-polypharmacy-issues.
31. NICE CKS, "Lung and pleural cancers — recognition and referral," https://cks.nice.org.uk/topics/lung-pleural-cancers-recognition-referral — urgent chest X-ray within 2 weeks for age ≥ 40 with unexplained features (2+ risk-factor features or 1 if ever smoked); Cancer Research UK, "NICE (NG12) suspected cancer referral guidelines" summary, https://www.cancerresearchuk.org/health-professional/diagnosis/primary-care/suspected-cancer-referral-guidelines/nice-ng12 — downloadable per-site criteria (lumps, dysphagia, post-menopausal bleeding); both confirm NG12 action language ("suspected cancer pathway referral" vs "consider") and safety-netting.
32. GPnotebook — NICE urgent cancer referral guidance, https://gpnotebook.com — unexplained bleeding/bruising/petechiae in adults, lumps/enlarged lymph nodes, neurological symptoms as urgent triggers.
33. GP Reasoning — suspected cancer referrals: symptom, age, action, https://gpreasoning.uk — lung rule: ≥2 unexplained symptoms (cough, fatigue, breathlessness, chest pain, weight loss, appetite loss), or one in a person > 40 who has ever smoked → chest X-ray.
34. NICE NG128, *Stroke and transient ischaemic attack in over 16s: diagnosis and initial management* (May 2019), https://www.nice.org.uk/guidance/ng128.
35. Manchester Triage System overview (flowcharts, five categories, 0/10/60/120/240-min targets), https://legacy.cfmt.org/libweb/m5IvWR/3AD125/ManchesterTriageSystem.pdf; Santos et al. (2013) on MTS v2 discriminators, https://www.grupoportuguestriagem.pt/wp-content/uploads/2021/01/Artigo-Cienti%CC%81fico-Manchester-Triage-System-Version-II-and-Resource-Utilisation-in-Emergency-Department.pdf.
36. MTS discriminator categories (life threat, haemorrhage, pain, unconsciousness, temperature, heart rate, mechanism of injury), https://m.medicalalgorithms.com/manchester-triage-system-mts.
37. AHRQ, *Emergency Severity Index (ESI): A Triage Tool for Emergency Department Care, Version 4* — ESI Implementation Handbook (AHRQ Publication No. 12-0014; Appendix B algorithm; available via AHRQ archive/NCBI Bookshelf), https://www.ahrq.gov/sites/default/files/publications2/files/esitriagealgorithm-v4_0.pdf (403-blocked; criteria corroborated via the Appendix B algorithm text — "A. Immediate life-saving intervention required: airway, emergency medications…" — plus [38] and TriageIQ walkthrough, https://www.triageiq.com/blog/esi-triage-algorithm): ESI-1 = immediately life-saving intervention; ESI-2 = high-risk situation / confused-lethargic-disoriented / severe pain-distress; ESI-3 = ≥2 resources; ESI-4/5 = 1/0 resources.
38. Espejo T et al. (2025), *Journal of Emergency Medicine*, ESI 5th-version update emphasizing abnormal vitals in low-acuity patients, https://www.jem-journal.com/article/S0736-4679(25)00288-4/pdf.
39. NHS Pathways description (skill-based disposition, Directory of Services, CAS escalation within 2 h), via HSIB [21] and NHS 111 service overviews.
40. Ada Health help center ("Can Ada give me a medical diagnosis?"), https://ada.com/help/can-ada-give-me-a-medical-diagnosis-can-ada-diagnose-medical-conditions — triage recommendation output, red-flag symptom flagging during structured interview; German consumer-protection testing context via MedCity News tag coverage.
41. Babylon: company-reported 85% appropriateness / 93% safety triage scores (Apr 2020 coverage); internal physician accuracy concerns reported by Forbes 2018 (via GovTech, May 2021), https://www.govtech.com — cautionary gap between claimed and independently assessed safety; Sutaria 2025 measured Babylon red-flag coverage at 42.9% [4].
42. Buoy Health emergency-sign handling — instructs users not to wait for tool output for chest pain, difficulty breathing, altered consciousness, suicidal thoughts; presents care options including ER; JMIR characterization: Carmona et al. (2022), PMC9440406.
43. Charbonneau DH (2015), "Health Disclaimers and Website Credibility Markers," Wayne State University, https://digitalcommons.wayne.edu/cgi/viewcontent.cgi?article=1126&context=slisfrp — disclaimers inform non-advice status; behavioral-effect evidence lacking.
44. Evidence audit of health/medical apps on Apple App Store (2024), https://www.researchgate.net/publication/382912030 — 72% (48/67) of diagnosis apps include a "not medical advice" disclaimer.
45. "Consumer warning versus systemic change: Disclaimer labels on digitally modified images" (2020), https://www.researchgate.net/publication/343401428 — disclaimer labels "not helpful for their intended purpose" (no behavioral change).
46. Claggett MS et al. (2022), "The Effects of Website Traits and Medical Skepticism on Patients' Willingness to Follow Online Medical Advice," PubMed 35179506 — persuasion driven by authorship/tone/credibility, not disclaimers.
47. Oxford Internet Institute / Oxford study (May 2025), coverage: Cybernews, https://cybernews.com/news/ai-chatbots-health-advice-risks-oxford; TechCrunch (5 May 2025) — participants with chatbots identified correct condition ~1/3 of the time, cause ~45%; worse than unassisted; Mahdi: "two-way communication breakdown"; participants downplayed serious conditions.
48. Mahdi A et al. (2025), Oxford — overreliance on incorrect chatbot answers when outputs mix good and bad advice.
49. University of Oxford news (10 Feb 2026), "New study warns of risks in AI chatbots giving medical advice," https://www.ox.ac.uk/news/2026-02-10-new-study-warns-risks-ai-chatbots-giving-medical-advice (403-blocked; corroborated by BBC, https://www.bbc.com/news/articles/c3093gjy2ero and Reuters, 9 Feb 2026) — 1,300-participant study, largest to date; LLMs no better than standard search for health decisions.
50. Sanford Health behavioral-health specialist and Danish researcher warnings — chatbots "comfort users while" missing clinical danger (Oct 2025 coverage).
51. Futurity coverage (Oct 2025) — study finding AI chatbots "routinely violate mental health ethics standards," including crisis mishandling.
52. Chen et al. (2025), "From Stigma to Acceptance: Ethical Implications of Anthropomorphic Design in Healthcare Chatbots," ResearchGate — human-like design shapes trust independent of advice quality.
53. Healthcare-in-Europe (Jun 2023) — chatbot avatar appearance (human-like vs logo) biases perceived advice quality.
54. Gunawan J et al. (2022), "A Comparative Study of Dark Patterns Across Mobile and Web," FTC PrivacyCon 2022, https://www.ftc.gov/system/files/ftc_gov/pdf/PrivacyCon-2022-Gunawan-Pradeep-Choffnes-Hartzog-Wilson-A-Comparative-Study-of-Dark-Patterns-Across-Mobile-and-Web-Modalities.pdf — 95% of studied apps contained dark patterns.
55. "Dark patterns: manipulative design strategies in digital health" (2024), PubMed 38332141 — catalog and risk assessment of dark patterns in health apps.
56. CEUR Vol-3720, "Towards Understanding Dark Patterns in Commercial Health Apps," https://ceur-ws.org/Vol-3720/paper2.pdf — elevated stakes: vulnerable users, sensitive data.
57. Semigran HL et al. (2015), "Evaluation of symptom checkers for self diagnosis and triage: audit study," *BMJ* 2015;351:h3480 — 23 checkers, 45 vignettes; correct diagnosis first in 34%; appropriate triage in 57% (95% CI 52–61); ~80% appropriate urgent-care advice on emergent cases; vignette dataset on Zenodo (doi:10.1136/bmj.h3480 supplement).
58. ECRI, *Top 10 Health Technology Hazards for 2026* — #1 "Misuse of AI chatbots in health care" (first time an AI-related technology has topped the list); coverage: HAP (Hospital and Healthsystem Association of Pennsylvania), 20 Feb 2026, and HIT Consultant, https://1technation.com/top-tech-dangers-ecris-top-10-health-technology-hazards-for-2026.
59. Han T, Kumar A, Agarwal C, Lakkaraju H (2024), "MedSafetyBench: Evaluating and Improving the Medical Safety of Large Language Models," NeurIPS 2024, https://arxiv.org/abs/2403.03744 — verbatim (fetched): "the first benchmark dataset designed to measure the medical safety of LLMs"; grounded in AMA Principles of Medical Ethics; "publicly-available medical LLMs do not meet standards of medical safety"; fine-tuning "improves their medical safety while preserving their medical performance."
60. MedSafetyBench dataset/code, https://github.com/AI4LIFE-GROUP/med-safety-bench (CC BY-NC-SA 4.0).
61. HealthBench (OpenAI, May 2025) — 5,000 realistic health conversations graded against physician-written rubrics with explicit safety criteria; 1,000-example "Hard" subset on which top models historically scored below ~32% (PureAI coverage, 13 May 2025, https://pureai.com/articles/2025/05/13/openai-healthbench.aspx; Kingy.ai deep-dive, 12 May 2025; leaderboard: https://llm-stats.com/benchmarks/healthbench-hard).
62. Multi-domain medical red-teaming framework (2025), arXiv; Medical Red Teaming Protocol (Jul 2025); Health AI Partnership red-teaming guidance (Dec 2024).
63. Evidence gap (UNKNOWN): no substantial peer-reviewed study found on deliberately adversarial users minimizing symptoms to bypass emergency detection in symptom checkers; psychiatric triage study (15 chatbots, 112 vignettes) and practitioner eval write-ups are the closest analogues.
64. WHO, *Ethics and governance of artificial intelligence for health: Guidance on large multi-modal models*, ISBN 978-92-4-008475-9, 98 pp (publication page: https://www.who.int/publications/i/item/9789240084759, fetched Oct 2026); announced 18 Jan 2024, https://www.who.int/news/item/18-01-2024-who-releases-ai-ethics-and-governance-guidance-for-large-multi-modal-models — "over 40 recommendations" for governments, technology companies, and health-care providers; risks include hallucinated/false/inaccurate/biased outputs, explicitly including chatbots answering patients' written queries; themes: transparency, human oversight, independent audit, post-deployment monitoring.
65. WHO (Oct 2024), *Considerations on the regulation of AI for health* (draft) — six regulatory considerations incl. transparency/documentation, risk management, data quality, post-market monitoring.
66. ITU/WHO Focus Group on AI for Health (FG-AI4H) benchmarking deliverables (finalized Sep 2023) — validation/evaluation/benchmarking requirements for health AI.
67. CHART (Chatbot Assessment Reporting Tool) reporting guideline (2025) — standardized transparent reporting for health-chatbot evaluation studies.
68. De S et al. (2013), traffic-light rule validation — missed a substantial proportion of serious bacterial infections, particularly UTIs (Flinders University repository).
69. Pediatric antipyretic dosing is weight-based, not fixed-dose (pediatric dosing chart guidance, e.g., https://www.kidsvillepeds.com/blog/1476886-fever-dosing-by-weight-a-pediatricians-chart-for-parents).
70. CHOP Symptom Checker, https://www.chop.edu/symptom-checker; Children's National Symptom Checker, https://childrensnational.org/get-care/symptom-checker — pediatric-specific triage tools (existence evidence for age-segregated assessment).
71. O'Mahony D et al., STOPP/START criteria, *Age and Ageing* (2008; v2 2015; v3 2023), https://academic.oup.com/ageing/article/44/2/213/2812233; BGS application guidance, https://www.bgs.org.uk/application-of-stoppstart-criteria-to-reduce-polypharmacy-among-elderly-patients-a-geriatric.
72. STOPP-Frail (27 criteria for frail older patients), https://www.cgakit.com/stopp-frail.
73. Jones CHD et al. (2019), "Safety netting for primary care: evidence from a literature review," *BJGP* — safety-netting advice should include expected illness course, worrying symptoms to look out for, and specific when/how-to-re-seek instructions; Ayodapo AO & Odeyemi D (2023), "Safety netting concept in primary care," https://pmc.ncbi.nlm.nih.gov/articles/PMC10811715.
74. Djordjevic JZ et al. (2026), "Manchester Triage System: Effectiveness, Limitations, and Future Directions" (systematic review), https://pmc.ncbi.nlm.nih.gov/articles/PMC13512649 (fetched Oct 2026) — verbatim: sepsis "MTS sensitivity was 61.5% (95% CI 39.3 to 79.8)" (Gräff 2017); life-saving interventions "sensitivity of 75.0%, a negative predictive value (NPV) of 99.2%" (Gräff 2019); pediatric "AUC of 0.7 (95% CI, 0.66–0.74), sensitivity of 57% and specificity of 69%" (Aeimchanbanjong 2017); "Under-triage mainly occurs in the MTS categories orange and yellow"; discriminator subjectivity: "symptom interpretation and discriminator selection can vary significantly among triage nurses."
75. Google, "Suicide prevention resources on Google Search" (The Keyword blog), https://blog.google/products-and-platforms/products/search/suicide-prevention-resources-on-google-search/ — prevention resources shown at the top of search results for suicide-related queries; US card routes to 988 (call/text) and 988lifeline.org chat; country-specific helpline reference: https://support.google.com/websearch/answer/11181469.
76. MIT Technology Review (21 Jul 2025), "AI companies have stopped warning you that their chatbots aren't doctors," https://www.technologyreview.com/2025/07/21/1120522/ai-companies-have-stopped-warning-you-that-their-chatbots-arent-doctors — medical disclaimers in chatbot health responses fell from ~26% (2022) to under 1% (2025); corroborated by eMarketer (25 Jul 2025).
77. MIT Media Lab / *NEJM AI* (May 2025), "People overtrust AI-generated medical advice despite low accuracy," https://www.media.mit.edu/publications/NEJM-AI-people-overtrust-ai-generated-medical-advice-despite-low-accuracy — overtrust persists even when the advice is wrong; authors link the risk to the disappearance of disclaimers.
