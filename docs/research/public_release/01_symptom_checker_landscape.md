# S1 — The Symptom-Checker Landscape as of 2026: Commercial and Notable Research Systems

**Commissioned:** 2026-10-28 · **Scope:** S1 (`01_symptom_checker_landscape.md`)
**Method:** ~15 web searches + direct fetches of vendor pages, journal pages, and paper PDFs (October 2026). Verbatim quotes carry URL + publisher + date. Claims with <3 independent sources are marked `WEAK-EVIDENCE`; unresolved gaps are marked `UNKNOWN — how to find out`.

## TL;DR

The consumer symptom-checker market bifurcated after 2023. Rule/Bayesian-era products (Ada, Infermedica, Your.MD/Healthily, Buoy, WebMD) survived by either (a) getting regulated — Ada re-certified under EU MDR as Class IIa in Dec 2022, Infermedica certiﬁed Class IIb under EU MDR — and selling B2B to health systems and insurers, or (b) fading quietly (Buoy, Healthily) — and one, Babylon, the loudest AI-medicine story of 2018-2021, collapsed entirely: a $4.2B SPAC peak became a Chapter 7 filing in Aug 2023 and UK assets sold for ~£500,000. The 2023-2026 wave of general-purpose LLMs commoditized the *conversation* layer but exposed a gap in *accountability*: OpenAI launched **ChatGPT Health** (Jan 7, 2026) as a sandboxed health tab used by 40M+ people daily for health questions, while every regulated vendor's 2026 architecture converges on the same hybrid pattern — an LLM conversational front end over a deterministic, certifiable triage engine, with RAG grounding and hard escalation guardrails. Nobody publishes a headline "top-1 diagnostic accuracy" number anymore; the regulated players publish *triage safety* and *care-intent shift* metrics instead. AegisMed's 15-condition KB and pattern-NLP stack is roughly a decade behind the commercial frontier on coverage and language, but its architecture (entropy-guided questioning + deterministic synthesis + explicit escalation) is structurally aligned with where the regulated market landed — provided it is positioned and evaluated as a *triage* system, not a diagnostician.

---

## 1. The commercial players, one by one

### 1.1 Ada Health (Berlin) — the Bayesian-era leader, now a regulated B2B platform

- **Architecture:** Probabilistic (Bayesian-network-style) reasoning engine over a structured symptom-condition ontology, with an adaptive question-asking interview that narrows differential hypotheses. Ada's own materials emphasize combining probabilistic/ML output with controlled, safe advice pathways. [1][2]
- **Published accuracy (independent):** In the Gilbert et al. vignette study (BMJ Open 2020; 8 apps vs 7 GPs, 200 vignettes), Ada was the best app: correct condition in top-3 **70.5%** vs **82.1% (±5.2)** for GPs, and the broadest coverage (a condition suggestion **99%** of the time). GPs' *safe urgency advice* was **97.0% (±2.5)**; Ada, Babylon and Symptomate were the only apps close to it. [3][4]
- **Regulatory:** "Ada's symptom assessment platform" is a **CE-marked Class IIa regulated medical device**, and the company announced **EU MDR certification in December 2022**. [5][6] This is the strongest regulatory posture of any consumer symptom checker found in this sweep.
- **Business model:** B2B2C — free consumer app + enterprise deployment into health systems and insurers (e.g., Sutter Health's "Scout", Bayer partnership per company materials); clinician-hours invested (>1M claimed on company pages). [5][6]
- **Status 2026:** Active and widely cited as the reference point for patient-facing AI in clinician-facing market reviews. [7]
- `WEAK-EVIDENCE` — exact condition-coverage count: third-party reviews say "thousands of conditions" but no authoritative public count was found (figures like "14,000/15,000" conflate ICD-10 code counts from unrelated sources). UNKNOWN — how to find out: Ada's clinical white paper (ada.com, May 2021) or a direct product-data request; also check their EU MDR technical-file *scope* statement, which typically enumerates covered conditions.
- `WEAK-EVIDENCE` — languages: multiple reviews list 7 consumer-app languages (en, de, fr, es, pt, it, sw), with newer enterprise claims of "10+". [8]

### 1.2 Babylon Health (UK) — the collapse that defines the cautionary tale

- **What it was:** UK digital-health unicorn; symptom-checker/consultation app; ran **GP at Hand**, an NHS digital-first GP practice; listed via SPAC in 2021 at a peak valuation **over $4.2 billion**. [9][10]
- **What happened:** After a planned take-private deal with MindMaze collapsed, Babylon filed for **Chapter 7 bankruptcy in the US on Aug 9, 2023** [11]; "substantially all" UK assets were sold to US firm **eMed Healthcare UK**, with administrators confirming in September 2023 that two divisions including GP at Hand were transferred [9][12]. Reported sale price for the UK business: **£500,000 (~$620,000)**. [10][13]
- **Claims vs reality:** In 2018 Babylon claimed its chatbot "beats GPs at a medical exam" (BBC, Jun 2018) [14]; a 2020 company-affiliated study across **1,671 test cases** claimed **77% accuracy vs 71% for the GPs tested** [15][16]. Independent commentary called the 2018 comparison "no more than clever PR" [17]; press documented a missed heart attack complained of to the MHRA (Telegraph, Jul 2018) [18]; the official NHS evaluation of GP at Hand concluded it could **not make robust conclusions about safety and effectiveness** [19].
- **Lessons (as summarized by WIRED, INFORMS Analytics, Mansfield Advisors):** replacing clinicians with an algorithm is much harder than claimed; loss-making NHS contracts and aggressive scaling on an unproven model were fatal; AI overpromising created regulatory and reputational fragility. [9][20][21]
- Note: Babylon was **excluded** from Hill et al.'s Australian audit and (per the authors' reply letter) registration-walled apps including Ada were excluded from the original MJA audit for feasibility reasons — relevant when reading "36 checkers tested" claims. [22]

### 1.3 Infermedica (Poland) / Symptomate — the B2B triage-engine model

- **Architecture:** Probabilistic inference engine exposed as an API (`/diagnosis`, `/suggest`, `/explain`, `/triage`); the interactive interview selects the most informative next question to narrow a ranked condition list. Symptomate is the consumer app built on the same engine. [23][24]
- **Regulatory (verbatim, vendor site, fetched 2026-10-28):** "is certified as a Class IIb medical device under EU MDR and registered with the UK MHRA." [25] Class IIb is a *higher* risk class than Ada's IIa — notable for triage software.
- **Scale claims (vendor, verbatim):** "30M+ checkups"; "Trusted by health systems in 30+ countries"; case studies: "Healthdirect Australia diverted 50% of intended ED visits to lower acuity care. Optum increased patient engagement by 19%." [25]
- **Independent accuracy:** In Gilbert et al. 2020, Symptomate was the *lowest* accuracy of 8 apps (top-3 **27.5%**) with coverage **61.5%** — the vendor's engine quality and the consumer app's measured performance must not be conflated. [3][4] `WEAK-EVIDENCE` — "750+ conditions, ~94% accuracy" figures circulate in third-party tool directories only. [26]
- **Business model:** B2B API licensing to insurers, hospitals, telehealth (e.g., Sana Kliniken AG, Germany, 2020). [24][27]

### 1.4 K Health (US/Israel) — records-grounded AI, pivoted to health-system B2B

- **Architecture:** AI assessment trained on millions of anonymized medical records ("personalized… based on real people like you"), now an "AI knowledge agent" architecture where LLMs are "grounded with medical truth and the individual's medical history" (company CPO), with licensed clinicians in the loop for actual care. [28][29]
- **Regulatory posture:** **No FDA clearance for the symptom checker found**; operates as an information/triage layer in front of licensed clinicians — the dominant regulatory posture for US patient-facing checkers. [28] `WEAK-EVIDENCE` (single review source for the "no clearance" claim).
- **Business:** Peak valuation **$1.4B** at a **$142M Series E (2021)**; later raised **$59M in a down round** [30]; total raised ~$375M (secondary). Now sells AI-enabled virtual primary care to health systems: Northwell Health launch (Nov 21, 2025) [31]; Hartford HealthCare "PatientGPT" (Mar 2026) [32] `WEAK-EVIDENCE` (single trade source for PatientGPT).

### 1.5 Isabel Healthcare (UK/US) — professional DDx, not consumer triage

- **Architecture:** Symbolic NLP (SNLP) engine searching a database of disease-presentation "illness scripts"; clinician enters signs/symptoms, gets a ranked differential. [33][34]
- **Coverage:** "over 10,000 conditions" across ages/specialties (marketplace listing) [35] `WEAK-EVIDENCE`.
- **Independent accuracy:** Bridges et al. 2024 (*Diagnosis*, 201-case test set): "Isabel Pro produced 175 (87.1%)" correct top diagnoses vs **ChatGPT-4 at 82.1%**, with better mean reciprocal rank. [36] Earlier reviews report Isabel capturing ~95% of inpatient discharge diagnoses and ~90% of must-not-miss diagnoses. [34]
- **Business model:** B2B clinician tool via EBSCO Health, paired with BMJ Best Practice; RCT evidence of improving clinicians' diagnostic reasoning (company FAQ). [33][37] This is the segment **above** AegisMed's consumer niche — worth studying for knowledge-base design, not UX.

### 1.6 Buoy Health (US) — the ML chatbot that went quiet

- **Architecture:** Conversational assistant combining ML/NLP with a doctor-curated clinical data model; founded out of Harvard Innovation Labs (Andrew Le). Coverage describes Bayesian-style probabilistic updating; no primary technical doc confirms "Bayesian network" — `WEAK-EVIDENCE` on the exact algorithm. [38][39]
- **Status:** Still operating through 2026 (live site, tracker listings, ~$74M raised; last major press was the 2020 **$37.5M** round and CVS MinuteClinic partnership). No shutdown/acquisition found. Measured third-party accuracy: top-3 **43%** in Gilbert et al. 2020, coverage 88.5%. [3][4][40]
- Read on 2026: a company that neither regulated nor pivoted visibly — the LLM wave squeezed its differentiation without killing it.

### 1.7 WebMD / Mayo Clinic — the portal checkers

- **Architecture:** Symptom *body-map + rule/decision-tree* checkers embedded in content portals; Mayo's tool maps a primary symptom to possible causes with Mayo-authored content. [41][42]
- **Measured accuracy:** WebMD is the single most-studied checker — assessed **8 times** in Wallace et al.'s systematic review, with primary diagnostic accuracy ranging **3% to 53%** across studies [43]; in Fraser et al. 2023 (real ED patients) WebMD: top-1 **40%**, top-3 **57%**, triage agreement **70%**, unsafe advice **19%** [44].
- **Business model:** free, ad/sponsorship-funded content ecosystem; the checker is an engagement feature, not a regulated device. No CE/FDA posture found.
- The pairing "WebMD vs AI checkers" is now a standard benchmark contrast (see 02 file). [44][45]

### 1.8 Your.MD / Healthily (UK) — rebranded, alive, low-signal

- Rebranded as **Healthily**; $30M Series A (Oct 2020) [46]; coverage **64.5%** and mid-table accuracy in Gilbert 2020 [4]; Walmart.com partnership (2022); 2025-2026 product "Dot" positioned as a "health-navigation product" [7][47]. ToS show "© 2017–2026 Your.MD Ltd. UK dba Healthily" — still operating; **no shutdown/acquisition found** (contrary to occasional rumors). [48]

### 1.9 LLM-first entrants (2023-2026) — the new wave

- **ChatGPT / ChatGPT Health (OpenAI).** Launched **Jan 7, 2026**: a dedicated health tab inside ChatGPT. Features (verbatim, via Axios reporting): "make sense of lab tests, navigate health insurance claims, and figure out what is causing various symptoms"; users can "bring in electronic medical records and other data from apps like Apple Health and MyFitnessPal"; OpenAI claims "more than 40 million people using it daily for medical and health insurance questions"; privacy framing: "information shared in the health tab won't be used in other types of chats," health "memories" viewable/deletable. [49][50] It is explicitly not a diagnosis device and not HIPAA-covered (OpenAI is not a medical provider) — the largest *de facto* symptom checker on earth with no CE/FDA posture.
- **Google AMIE (research).** LLM-based "Articulate Medical Intelligence Explorer" optimized for diagnostic dialogue via self-play; evaluated in a randomized double-blind crossover study of text consultations with patient actors across **149 OSCE-style scenarios**; "AMIE's performance matched or surpassed PCP" — outperforming primary-care physicians on 28 of 32 OSCE axes including diagnostic accuracy (Nature, 2025; arXiv Jan 2024). All results are simulated; not a product. [51][52][53]
- **Google Med-Gemini (research, 2024).** Multimodal medical model family; MedQA 91.1%; in a clinician-evaluated differential-diagnosis exercise, top-1 ~45% vs 36% for baseline GPT-4 on complex cases (`WEAK-EVIDENCE` — arXiv report + Google blog only). [54][55]
- **Hybrid "AI agent on certified engine" pattern (commercial 2026):** Mediktor — already CE/FDA-certified triage engine — wrapped with a conversational "AI Medical Agent" [56]; K Health's LLM "knowledge agent" grounded in records + clinicians [28]; Mount Sinai/Epic-integrated AI triage pairing AI with expert-authored triage rules inside the EHR [57]; Healthily's Dot; AskPatient (Patient.info) with "stated limits excluding diagnosis, personalised treatment and emergency care." [7]
- **Agentic RAG in medicine** (research 2025-2026): open systems integrating retrieval, re-ranking, evidence grounding, and diagnosis generation (e.g., vkola-lab/Medical-Agentic-RAG), with RAG still framed as the primary hallucination-control mechanism for clinical safety. [58][59]

### 1.10 Usage backdrop (why this matters for a public release)

- KFF Tracking Poll (Mar 2026): "Over one-third (36%) of adults ages 18 to 29 report using AI tools or chatbots for physical health information or advice." [60]
- Pew Research (2026): 22% of US adults get health information from AI chatbots at least sometimes; users rate convenience over accuracy. [61]
- ONS (Mar 2025, UK): only 17% used AI chatbots for health information, and most distrusted its accuracy. [62]
- OpenAI's own launch figure: 40M+ daily health-related questions. [49]

---

## 2. What "state of the art commercial" means technically in 2026

Synthesizing the vendor and market-review evidence above:

1. **Conversational front end (LLM) + deterministic triage core.** The emerging default is an LLM doing dialogue, empathy, and summarization, while a *certified*, rule/probabilistic engine makes the care-disposition call (Mediktor, K Health, Mount Sinai pattern). [28][56][57]
2. **Regulation as moat.** EU MDR Class IIa (Ada) and Class IIb (Infermedica) certification is what unlocks health-system/insurer contracts; US players mostly hide behind clinician-in-the-loop models instead of seeking 510(k) clearance for the checker itself. [5][25][28]
3. **B2B2C distribution.** The consumer-direct app business (2015-era model) lost to distribution through insurers, employers, and health systems (Ada enterprise, Infermedica/Healthdirect, K Health/Northwell). [5][25][31]
4. **Metrics reframed.** Vendors now market *triage safety*, *diversion of unnecessary ED visits*, *care-intent shift*, and *engagement*, not diagnostic top-1 (e.g., Infermedica's "99.6% reduction in patients unsure which care to seek", "50.5% change their care intent"). [25]
5. **Grounding and guardrails.** RAG over curated guidelines, hard keyword/red-flag escalation layers, and scoped disclaimers ("does not provide a definitive diagnosis") are table stakes. [2][59][7]
6. **Multimodality is arriving.** Text-only is treated as a ceiling; photo input (dermatology) is the first commercial multimodal wedge. [63] `WEAK-EVIDENCE` (vendor blog).
7. **The Babylon lesson is institutionalized.** No 2026 player claims "AI beats doctors" in consumer marketing; claims are scoped to navigation and safety of advice. [20][21]

**2023 → 2026 deltas:** (a) general-purpose LLMs took over free-form triage conversations (ChatGPT Health, 40M daily users) without any device certification; (b) the regulated incumbents repositioned as enterprise infrastructure; (c) architecture consensus shifted from monolithic Bayesian engines to hybrid LLM+deterministic+RAG; (d) the accuracy conversation moved from "diagnosis %" to "triage safety + escalation" (see 02 file); (e) two high-profile decommissionings (Babylon's collapse; quiet stagnation of Buoy/Healthily) proved the standalone-consumer-app model is economically fragile.

---

## 3. Implications for AegisMed (file-level)

1. **`src/core/disease_kb.py` — the 15-condition ceiling is a positioning problem before it is a modeling problem.** Every serious player covers 3 orders of magnitude more conditions (Symptomate ~750+, Isabel 10,000+). Either grow the KB (ICD-10-anchored entries like the current `DISEASE_DATABASE` schema already supports) or scope the product claim explicitly ("common adult acute presentations"). Add per-condition `red_flags` and a `care_level_hint` field — every competitor's KB carries triage metadata alongside diagnosis metadata.
2. **`src/core/demat.py` — add a disposition output, not just candidates.** `TriageSession.to_dict()` returns top-4 candidates and entropy; the commercial standard is a 4-level disposition (emergent / urgent / non-urgent / self-care) as in Ada/Infermedica/Symptomate and the evaluation literature. Add a `recommend_care_level()` derived from the posterior (e.g., P(emergent-capable condition) > θ₁ → emergent) so DEMAT produces *triage advice*, which is the regulated, marketable, and measurable artifact.
3. **`src/api/routes/diagnosis.py` — evolve `/emergency-check` from keyword lists to structured red-flag logic.** The current English/Hindi keyword trigger (threshold 0.5) is the 2015-era pattern (Semigran's worst performers did exactly this and *never* advised self-care). Keep over-triage bias but make it condition-aware: DEMAT's posterior over "cardiovascular disease"/"pneumonia" etc. should drive escalation, with keywords as a floor, not the ceiling.
4. **`src/agents/synthesis/agent.py` — keep Gemini for explanation only; never let it own triage.** The 2026 consensus pattern is LLM-for-language, deterministic-engine-for-disposition. `generate_report()` should be constrained to explaining the DEMAT/KB-derived disposition; the existing `doctor_alert` flag is the right shape — make it a *derived* field from the triage core, not from LLM prose.
5. **`frontend/src/lib/api.ts` — remove the silent `getDemoResults` fallback before any public exposure.** `diagnose()` falls back to fabricated demo results on API error. Babylon's collapse was substantially a trust story; a public user receiving silently-fake diagnoses on a network failure is a worse trust failure. Fail loudly with a "service unavailable" state instead.
6. **Regulatory posture decision (doc, then product):** Ada (IIa) and Infermedica (IIb) set the reference. AegisMed's public release should explicitly target "information + triage aid, not diagnosis" wording everywhere (frontend copy, disclaimers) and record the FDA CDS / EU MDR scoping analysis in `docs/research/public_release/07_regulatory_pathways.md` before launch, per the S7 scope.
7. **B2B2C, not D2C, is where the surviving companies ended up.** If AegisMed wants a deployment story beyond the FYP demo, the FHIR R4 surface (`src/core/fhir_mapping.py`, `src/api/routes/fhir.py`) is the asset that matters — it is exactly the health-system integration layer that Northwell/K Health bet on. Invest there rather than in consumer-app polish.
8. **Copy the vendor-metrics reframing for the paper and patent narrative.** Infermedica markets "care-intent shift" and "reduction in unsure patients"; Ada markets safety-of-advice. AegisMed's DEMAT benchmark should report entropy reduction *and* triage-safety/diversion metrics (see 02 file) — this matches both the CHIL audience and the commercial frame.
9. **Position honestly vs the LLM wave.** ChatGPT Health reaches 40M daily users with no certification; AegisMed's differentiator must be *accountability* (auditable KB, deterministic triage, FHIR) — the same ground Mediktor/Mount Sinai stake out. `src/agents/rule_based_synthesis.py` (deterministic fallback) is a feature to advertise, not a stub to hide.

---

## 4. Sources

1. Ada Health, "AI symptom assessments and beyond" white paper (May 2021) — https://www.ada.com — probabilistic engine, safe-advice architecture. (located via search; white paper itself not fetched)
2. MedCity News (Dec 2020), coverage of the 8-app GP comparison — physicians outperformed all 8 checkers; Ada best at 70.5% top-3.
3. Gilbert S, Mehl A, Baluch A, et al. "How accurate are digital symptom assessment apps for suggesting conditions and urgency advice? A clinical vignettes comparison to GPs." BMJ Open 2020;10(12):e040269 — https://bmjopen.bmj.com/content/10/12/e040269 · PubMed 33328258. GP top-3 82.1%±5.2; Ada 70.5%; GP safe-advice 97.0%±2.5.
4. Medical Device Network, "Significant disparities found in symptom assessment apps" (Dec 16, 2020) — https://www.medicaldevice-network.com/news/symptom-assessment-apps — verbatim: "The most comprehensive app was Ada, which provided a condition suggestion 99% of the time, followed by WebMD at 93% and Buoy at 88.5%"; "Babylon, which was able to provide a condition suggestion only 51.5% of the time, followed by Symptomate at 61.5% and Your.MD at 64.5%"; "Ada was rated as the most accurate, with the right condition in its top three suggestions 71% of the time"; "The next most accurate was Buoy with 43% accuracy, with the lowest scorer being Symptomate with only 27.5% accuracy"; apps: "Ada Health, Babylon, Buoy, K Health, Mediktor, Symptomate, WebMD and Your.MD"; "Each app was tested once against every vignette. Seven external GPs were also tested with the vignettes."
5. Ada Health, "Ada Health Receives EU-MDR Certification for AI-Powered Symptom Assessment Platform" (Dec 15, 2022) — https://about.ada.com/ — CE-marked Class IIa regulated medical device.
6. Ada Health Care Utilization Solutions page — https://about.ada.com/ — "CE-marked Class IIa regulated medical device"; ">1M clinician hours".
7. Iatrox, "Patient-Facing AI in 2026: What Clinicians Should Know" (Nov 1, 2025) — https://www.iatrox.com/blog/patient-facing-ai-health-tools-2025-ada-khealth-buoy-aide-mirror-nhs — "Buoy offers symptom discussion and care navigation, and Healthily presents Dot as a health-navigation product"; "AskPatient: … 'stated limits excluding diagnosis, personalised treatment and emergency care'".
8. Third-party app-store/vendor reviews of Ada language support (intech.media, UpdateStar) — 7 consumer languages. `WEAK-EVIDENCE`.
9. Healthcare Dive, "Babylon sells UK business as digital health company" (Aug 18, 2023) — https://www.healthcaredive.com/news/Babylon-Chapter-7-bankruptcy/691218 — "'Substantially all' of Babylon's UK assets were sold to U.S.-based healthcare services firm eMed last week"; Chapter 7 filing.
10. Forbes, "Bankrupt Digital Health Company Babylon Sells UK Assets For Just $620,000" (Katie Jennings, Sep 19, 2023) — https://www.forbes.com/sites/katiejennings/2023/09/19/bankrupt-digital-health-company-babylon-sells-uk-assets-for-just-620000 — £500,000 sale; vs $4.2B peak valuation.
11. Fierce Healthcare, "Babylon closes US business, lays off employees after Mindmaze take-private deal collapses" (Sep 5, 2023) — https://www.fiercehealthcare.com/digital-health/babylon-closes-us-business-lays-employees-after-mindmaze-take-private-deal-collapses
12. MobiHealthNews, "Babylon Health sells majority of UK assets to eMed" (Sep 2023) — https://www.mobihealthnews.com/news/babylon-health-sells-majority-uk-assets-emed
13. Wikipedia, "Babylon Health" — administration Sept 2023; £500k sale; $4.2B peak (retrieved via search summaries Oct 2026; corroborated by [9][10]).
14. BBC News, "Babylon claims its chatbot beats GPs at medical exam" (Jun 27, 2018) — https://www.bbc.com/news/technology-44635134
15. MobiHealthNews, "Babylon study finds new AI more effective than GPs at medical diagnosis" (Aug 2020) — https://www.mobihealthnews.com/news/emea/babylon-study-finds-new-ai-imagination-more-effective-gps-medical-diagnosis — 1,671 test cases; 77% vs 71% GPs. `WEAK-EVIDENCE` (company-affiliated study; peer-review status contested).
16. The Times, "Medical app from British healthcare company Babylon Health beats the doctor to right diagnosis" (Aug 2020) — https://www.thetimes.com/uk/healthcare/article/medical-app-from-british-healthcare-company-babylon-health-beats-the-doctor-to-right-diagnosis-hhm0rs8cp
17. Pulse Today, "Babylon's chatbot claims were no more than clever PR" (2018) — https://www.pulsetoday.co.uk/views/technology/babylons-chatbot-claims-were-no-more-than-clever-pr
18. The Telegraph, "AI doctor app Babylon fails to diagnose heart attack — complaint" (Jul 13, 2018) — https://www.telegraph.co.uk/technology/2018/07/13/ai-doctor-app-babylon-fails-diagnose-heart-attack-complaint
19. Pulse Today, "Babylon GP at Hand evaluation will not determine whether service is safe" (Dec 2018) — https://www.pulsetoday.co.uk/news/technology/babylon-gp-at-hand-evaluation-will-not-determine-whether-service-is-safe
20. WIRED, "The Fall of Babylon Is a Warning for AI Unicorns" (Sep 19, 2023) — via search summary; experts: "it's very hard to replace human clinicians with an algorithm". (direct fetch 404'd; headline via search)
21. INFORMS Analytics, "The Fall of Babylon" (Nov 2023) — https://pubsonline.informs.org/do/10.1287/LYTX.2023.04.10/full ; Mansfield Advisors, "Three Key Lessons from Babylon Health's Demise".
22. Hill MG, Sim M, Mills B, reply letter. Med J Aust 2021;214(3):143 — https://cdn.craft.cloud/019efd17-dcc2-707f-8e07-011d00d1146a/assets/issues/mja250923.pdf (fetched) — verbatim: "Three websites and four Apple Store and two Google Play smartphone applications (apps) (including Ada) were similarly excluded, as users are required to register an account."
23. Infermedica Help Center, Engine implementation — https://help.infermedica.com/implementation — /diagnosis, /suggest, /explain, /triage interview endpoints.
24. Infermedica blog, "Sana Kliniken AG implements symptom checker from Infermedica" (Aug 18, 2020) — https://infermedica.com/blog/articles/sana-kliniken-ag-implements-symptom-checker-from-infermedica
25. Infermedica homepage (fetched 2026-10-28) — https://infermedica.com/ — verbatim: "is certified as a Class IIb medical device under EU MDR and registered with the UK MHRA."; "30M+ checkups"; "Trusted by health systems in 30+ countries"; "Healthdirect Australia diverted 50% of intended ED visits to lower acuity care. Optum increased patient engagement by 19%."; "reduction in patients unsure which care to seek 99.6%"; "change their care intent once guided by virtual triage 50.5%".
26. AI Central Resources, Infermedica tool review — https://www.aicentralresources.com/tool/infermedica — "750+ medical conditions… ~94% accuracy". `WEAK-EVIDENCE` (non-peer-reviewed directory).
27. AI Central Resources, Infermedica review — deployment in 30+ countries.
28. RFP.wiki / Center4Research / K Health CPO (Ran Shaul) statements — https://www.rfp.wiki/...k-health ; https://www.center4research.org/comment-ai-medical-devices-healthcare — AI trained on anonymized records; LLMs "grounded with medical truth and the individual's medical history"; no FDA clearance of the checker found.
29. Iatrox, "K Health review (UK clinicians)" (Dec 2025) — https://www.iatrox.com/blog/k-health-review-uk-clinicians-ai-physician-mode-evidence — clinician-in-loop model.
30. Calcalist/CTech, "Unicorn K Health raises $59 million in down round" — https://www.calcalistech.com/ctechnews/article/h1f58cfc3 — "K Health suffered a decrease in valuation from the $1.4 billion it reached when it raised a $142 million Series E in 2021."
31. Coverager, "Northwell Health launches AI-powered virtual primary care platform with K Health" (Nov 21, 2025) — https://coverager.com/northwell-health-launches-ai-powered-virtual-primary-care-platform-with-k-health
32. MedicalChat coverage of Hartford HealthCare "PatientGPT" (Mar 2026) — `WEAK-EVIDENCE` (single trade source).
33. EBSCO Health, "Isabel — Clinical Decision Support Tool" — https://about.ebsco.com/health-care/products/isabel — "Physicians around the world use Isabel to help construct or broaden a differential diagnosis."
34. Ren (2019), JCHLA review of Isabel — https://journals.library.ualberta.ca/jchla/index.php/jchla/en/article/view/29418/21562 — SNLP engine; ~95% capture of discharge diagnoses; ~90% of must-not-miss.
35. Avia Health Marketplace, Isabel listing — https://marketplace.aviahealth.com/compare/64687/67866 — "over 10,000 conditions". `WEAK-EVIDENCE`.
36. Bridges JM et al. (2024), *Diagnosis* (De Gruyter) — https://www.degruyterbrill.com/document/doi/10.1515/dx-2024-0033/html — verbatim: "Isabel Pro produced 175 (87.1 %)…" correct on 201-case set vs ChatGPT-4 82.1%.
37. Isabel Healthcare FAQs — https://www.isabelhealthcare.com/isabel-faqs — RCT evidence of improved diagnostic reasoning.
38. Healthcare IT Today, interview with Andrew Le (Dec 11, 2019) — https://www.healthcareittoday.com/2019/12/11/navigating-the-healthcare-system-is-miserable-can-ai-bots-help — ML trained with physician input.
39. Elion Health, AI symptom checkers category — https://elion.health/categories/ai-symptom-checkers/products — Buoy description. Bayesian-specific claim `WEAK-EVIDENCE`.
40. Bloomberg company profile, Buoy Health Inc — https://www.bloomberg.com/profile/company/1530276D:US — Andrew Le CEO; still active.
41. WebMD Symptom Checker app listing — https://apps.apple.com/us/app/webmd-symptom-checker/id295076329
42. RxEconsult, "Evaluation of WebMD and Other Symptom Checkers" — https://www.rxeconsult.com/healthcare-articles/Evaluation-Of-WebMd-And-Other-Symptom-Checkers--848 — Mayo tool maps primary symptom to causes.
43. Wallace W et al. "The diagnostic and triage accuracy of digital and online symptom checker tools: a systematic review." npj Digit Med 5:118 (Aug 17, 2022) — https://www.nature.com/articles/s41746-022-00667-w — verbatim: "the WebMD symptom checker was assessed eight times and was the most commonly assessed symptom checker in this review"; its primary diagnostic accuracy "ranged from 3 to 53%".
44. Fraser H, Crossland D, Bacher I, Ranney M, Madsen T, Hilliard R. "Comparison of Diagnostic and Triage Accuracy of Ada Health and WebMD Symptom Checkers, ChatGPT, and Physicians for Patients in an Emergency Department: Retrospective Study." JMIR Mhealth Uhealth 2023;11:e49995 (Oct 3, 2023) — https://pubmed.ncbi.nlm.nih.gov/37788063/ — WebMD: top-1 40% (12/30), top-3 57% (17/30), triage agreement 70%, unsafe 19%.
45. JMIR mHealth e49995 citation page — https://mhealth.jmir.org/2023/1/e49995 — Ada/WebMD/ChatGPT/physician ED comparison.
46. Mercom Capital / MobiHealthNews coverage of Your.MD $30M Series A (Oct 2020).
47. Healthily press release (June 2025) — cold/flu/COVID triage pilot; Walmart.com partnership (2022).
48. healthily.app / healthily.ai terms — "© 2017–2026 Your.MD Ltd. UK dba Healthily". Still operating.
49. Axios via Benton Institute, "OpenAI adds ChatGPT Health for medical questions" (Jan 7-8, 2026) — https://www.benton.org/headlines/openai-adds-chatgpt-health-medical-questions — verbatim: "OpenAI is expanding its capabilities by adding a dedicated health tab to ChatGPT"; users can "bring in electronic medical records and other data from apps like Apple Health and MyFitnessPal"; "make sense of lab tests, navigate health insurance claims, and figure out what is causing various symptoms"; "more than 40 million people using it daily for medical and health insurance questions"; "information shared in the health tab won't be used in other types of chats"; "A small group will test the feature first."
50. Silicon Republic, "OpenAI tries tackling privacy concerns with new ChatGPT Health" (Jan 2026) — https://www.siliconrepublic.com/machines/openai-tries-tackling-privacy-concerns-with-new-chatgpt-health (403 on fetch; headline via search). KFF Health News morning breakout, same date.
51. Tu T, et al. "Towards conversational diagnostic artificial intelligence." Nature (2025) — https://www.nature.com/articles/s41586-025-08866-7 — "AMIE's performance matched or surpassed PCP"; 28/32 OSCE axes; 149 scenarios.
52. Tu T, et al. arXiv:2401.05654 (Jan 2024) — AMIE preprint.
53. Google Research blog, "AMIE: A research AI system for diagnostic medical reasoning and conversations" (Jan 12, 2024) — https://research.google/blog/amie-a-research-ai-system-for-diagnostic-medical-reasoning-and-conversations
54. "Capabilities of Gemini Models in Medicine" (Med-Gemini), arXiv:2404.18416 (2024) — https://arxiv.org/html/2404.18416v2 — MedQA 91.1%; clinician-evaluated DDx top-1 ~45% vs 36% GPT-4 baseline on complex cases. `WEAK-EVIDENCE` (preprint + vendor blog).
55. Google Research blog, "Advancing medical AI with Med-Gemini" (May 15, 2024) — https://research.google/blog/advancing-medical-ai-with-med-gemini
56. Barcelona Health Hub, "Discover how Mediktor is redefining the future of digital triage" — https://barcelonahealthhub.com/en/news/discover-how-mediktor-is-redefining-the-future-of-digital-triage — CE/FDA-certified engine + conversational "AI Medical Agent".
57. UCSF Codex case study, "Check symptoms, get care: Mount Sinai's AI triage solution" — https://codex.ucsf.edu/check-symptoms-get-care-mount-sinais-ai-triage-solution — AI paired with expert-authored triage rules in EHR workflow.
58. vkola-lab/Medical-Agentic-RAG (GitHub, 2025-2026) — https://github.com/vkola-lab/Medical-Agentic-RAG — retrieval + re-ranking + evidence grounding + diagnosis generation.
59. "6 reasons why RAG is still relevant in 2026" (LinkedIn analysis) — RAG as primary hallucination-control in clinical contexts. `WEAK-EVIDENCE` (opinion piece; corroboration in [58]).
60. KFF Tracking Poll on Health Information and Trust: "Use of AI for Health Information and Advice" (Mar 25, 2026) — https://www.kff.org/public-opinion/kff-tracking-poll-on-health-information-and-trust-use-of-ai-for-health-information-and-advice — verbatim: "Over one-third (36%) of adults ages 18 to 29 report…"
61. Pew Research Center, "Users of social media and AI chatbots for health information…" (Apr 2026) — https://www.pewresearch.org/science/2026/04/07/users-of-social-media-and-ai-chatbots-for-health-information-are-more-likely-to-say-they-are-convenient-than-accurate — 22% at least sometimes.
62. ONS (UK), AI chatbot use for health information (Mar 2025) — 17% of adults, most distrusting accuracy.
63. AutoDerms, "AI symptom checkers and skin: why text needs a photo" (2026) — https://autoderm.ai/blog/ai-symptom-checkers-skin-gap — text-only underperformance; photo input improves triage. `WEAK-EVIDENCE` (vendor blog).
