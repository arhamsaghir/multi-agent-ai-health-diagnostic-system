# Patent & Prior-Art Landscape (S11)

**Scope:** what already exists in patents and top-tier publications around
symptom-triage engines, agentic diagnosis, and entropy-driven questioning —
read against AegisMed's claimed novelties (DEMAT entropy-based active triage,
EN-SCAF risk bounding, MCRC-DS, the multi-agent orchestration).

**TL;DR:** The raw algorithmic idea at the heart of DEMAT — *"pick the next
question that maximizes information gain over a differential-distribution
distribution"* — is the textbook mechanism of existing decision-tree triage
engines and is treated as a standard, unpatentable ML building block; granted
patents in this space wrap the mechanism inside **system claims** (specific
interfaces, multi-stage pipelines, EHR integration, voice). Meanwhile the
**multi-agent LLM diagnosis** space now has direct, recent, top-tier prior art:
an orchestrator–specialist CDSS for secondary headache in JAMIA (2026),
MDAgents at NeurIPS 2024, AMIE in Nature (2025), and a dedicated "diagnostic
questioning efficiency" benchmark (Q4Dx, Sci Rep, Jan 2026). The defensible
patent surface is narrower than the current provisional language implies: the
deterministic *extract → entropy → bounded-question-bank → triage-band*
mechanism with conformal-before-agreement calibration, cold-start behavior on
an open terminology, and the specific system architecture — not "entropy
triage" or "multi-agent diagnosis" as such.

---

## 1. Symptom-checker patents — the claim shapes that get granted

- **WO2023095069A1** — "Adaptive disease prediction system in an AI
  symptom-checker chatbot" (2023, WO): an AI chatbot triaging a wide variety
  of diseases in **under-3-minute conversations**. The closest single
  symptom-checker patent; claims center on the adaptive prediction pipeline
  inside a conversational interface
  ([patents.google.com/patent/WO2023095069A1](https://patents.google.com/patent/WO2023095069A1/en)).
- **US9142066B2** — "Multi-stage diagnostic system and method": seeks
  diagnostic information from successive information sources when earlier ones
  are insufficient — the classic multi-stage interviewing shape
  ([patents.google.com/patent/US9142066](https://patents.google.com/patent/US9142066)).
- **US11031107B2** — capturing patient indicator values (question answers) and
  integrating them with a CDSS during diagnosis
  ([patents.google.com/patent/US11031107B2](https://patents.google.com/patent/US11031107B2/en)).
- **EP3762942B1** — health models diagnosing conditions manifested in the
  patient's **voice** ([patents.google.com/patent/EP3762942B1](https://patents.google.com/patent/EP3762942B1/en)) —
  relevant if AegisMed ever merges its Whisper voice path into triage.
- **US10,930,401 (Petriage)** — AI triage for care-urgency with ~97% accuracy
  claimed, granted in the *veterinary* space — shows the "urgency assessment
  score" claim shape is grantable
  ([petriage.com](https://petriage.com/2021/02/23/petriage-awarded-first-ever-patent-for-online-ai-driven-pet-symptom-checker-a-97-plus-accurate-tool-for-assessing-urgency-of-seeking-care)).
- A Sep 2026 **PatSnap landscape review** of digital symptom-checker/triage
  patents exists and maps assignees/IPC composition — order it or use the
  public summary as the starting map
  ([patsnap.com blog](https://www.patsnap.com/resources/blog/rd-blog/digital-symptom-checker-triage-patent-landscape-patent-landscape)).

**Claim-shape lesson:** every granted artifact above pairs the algorithm with
a concrete system boundary (interface, latency budget, data source, staging).
None claims "information gain question selection" in the abstract.

## 2. The entropy/information-gain core is off-patent by nature

Searches across Google Patents surfaces confirm: selecting the next question
to maximize information gain over a differential is the algorithmic basis of
existing decision-tree triage engines and standard ML curricula; patents in
this area wrap it in system claims (patient interfaces, EHR integration,
voice models, multi-stage pipelines). Practitioner analyses also flag **§101
abstract-idea / medical-diagnostic-eligibility** hurdles for purely
computational diagnostic correlations:

- Eligibility analysis: [meddeviceonline.com](https://www.meddeviceonline.com/doc/how-to-navigate-patent-eligibility-of-ai-driven-diagnostics-0001);
  [IPWatchdog on diagnostic patent eligibility](https://ipwatchdog.com/2019/04/14/patent-eligibility-of-medical-diagnostics-inventions-where-are-we-now-and-where-is-there-to-go)
- Search recipe for the professional prior-art pass: Google Patents with
  `(adaptive OR iterative) AND ("next question" OR "question selection") AND
  (diagnosis OR triage) AND ("information gain" OR entropy)` plus CPC
  **G16H50/20** (diagnosis-focused healthcare informatics).

**Implication:** the provisional's DEMAT framing must be narrowed from
"entropy-based triage" to the specific deterministic mechanism + calibration
+ system integration, or it will not survive examination.

## 3. Academic prior art now sits directly on the orchestration claim

- **Wu et al., JAMIA 2026** — "Orchestrator–specialist multi-agent clinical
  decision support system" improving **secondary headache diagnosis** accuracy
  and transparency
  ([academic.oup.com/jamia/article/33/10/1910/8719545](https://academic.oup.com/jamia/article/33/10/1910/8719545)).
  An orchestrator routing to specialist agents, in a clinical specialty, in a
  top informatics journal — this is the closest architectural prior art and it
  post-dates nothing AegisMed can claim priority on if the provisional was
  filed earlier; check the filing date against the provisional's priority date.
- **MDAgents** (NeurIPS 2024, arXiv:2404.15155) — adaptive solo-vs-team LLM
  agent composition; won 7/10 benchmarks (cross-ref `04`).
- **AMIE / McDuff et al., Nature 2025** — LLM diagnostic dialogue beating
  PCPs on 28/32 axes; top-1 29.2% / top-10 59.1% on 302 NEJM CPC cases
  (cross-ref `04`).
- **Q4Dx** (Sci Rep, Jan 2026) — benchmarks "diagnostic questioning
  efficiency," noting info-gain metrics "have not yet been widely adopted in
  medicine" — the honest current-art statement about DEMAT's space
  (cross-ref `04`).

## 4. Babylon's collapse — the cautionary prior-art holder is gone

Babylon Health entered Chapter 7 (US) and UK administration in Aug–Sep 2023
after the MindMaze merger fell through; **eMed Healthcare UK** bought
substantially all UK assets for a reported ~£500,000 against a former $4.2B
valuation. Searches surfaced **no standalone, publicly reported sale of
Babylon's triage patent portfolio** — the IP disposition records are sparse.

- [Healthcare Dive — Chapter 7](https://www.healthcaredive.com/news/Babylon-Chapter-7-bankruptcy/691218)
- [MobiHealthNews — eMed buys UK assets](https://www.mobihealthnews.com/news/babylon-health-sells-majority-uk-assets-emed)
- [Telecare Aware — receivership timeline](https://telecareaware.com/babylon-health-shuts-us-operations-goes-into-uk-receivership)

UNKNOWN — how to find out: pull the USPTO Assignment Database
(assignments.uspto.gov) for transfers from Babylon Holdings entities during
2023, and the Delaware Chapter 7 asset schedule, before finalizing freedom-to-
operate claims around conversational triage.

## 5. Where AegisMed's defensible surface actually is

Synthesizing §1–4 with the measurement findings (cross-refs `02`, `04`, `05`):

1. **Deterministic, terminology-grounded triage core** (SNOMED/ICD-11 free in
   India — `09`): the engine + bounded question bank + explicit out-of-scope
   refusal, as a self-hosted system. No open equivalent exists (`09` §9).
2. **Conformal-before-agreement calibration**: conformal sets computed *before*
   multi-agent agreement blending (agreement-after-conformal collapses
   coverage 90%→74% — cross-ref `05`). This sequencing appears novel in the
   consumer-triage context; a claims-worthy engineering mechanism.
3. **Safety-band output contract**: disposition bands (emergency/urgent/
   routine/self-care) with under-triage-biased defaults and measured
   sensitivity on emergency vignettes — the field's documented weak spot is
   under-triage (`01`, `08`), so a *measured* safety guarantee is
   differentiating.
4. **System claims**: orchestrator→specialist graph with a verification node,
   deterministic fallback labeled in UI, and the ABDM/FHIR consent-managed
   integration (`09` §6) — the claimable system boundary.

---

## Sources

1. [WO2023095069A1 — Adaptive disease prediction AI symptom-checker chatbot](https://patents.google.com/patent/WO2023095069A1/en) (accessed 2026-10-27).
2. [US9142066B2 — Multi-stage diagnostic system and method](https://patents.google.com/patent/US9142066) (accessed 2026-10-27).
3. [US11031107B2 — Patient indicator capture with CDSS](https://patents.google.com/patent/US11031107B2/en) (accessed 2026-10-27).
4. [EP3762942B1 — Voice-manifested condition diagnosis](https://patents.google.com/patent/EP3762942B1/en) (accessed 2026-10-27).
5. [Petriage — US 10,930,401, urgency-triage grant](https://petriage.com/2021/02/23/petriage-awarded-first-ever-patent-for-online-ai-driven-pet-symptom-checker-a-97-plus-accurate-tool-for-assessing-urgency-of-seeking-care) (accessed 2026-10-27).
6. [PatSnap — digital symptom checker triage patent landscape (Sep 2026)](https://www.patsnap.com/resources/blog/rd-blog/digital-symptom-checker-triage-patent-landscape-patent-landscape) (accessed 2026-10-27).
7. [Wu et al., JAMIA 2026 — orchestrator–specialist CDSS for secondary headache](https://academic.oup.com/jamia/article/33/10/1910/8719545) (accessed 2026-10-27).
8. [MDAgents, arXiv:2404.15155 / NeurIPS 2024](https://arxiv.org/abs/2404.15155) (accessed 2026-10-27).
9. [Healthcare Dive — Babylon Chapter 7](https://www.healthcaredive.com/news/Babylon-Chapter-7-bankruptcy/691218); [MobiHealthNews — eMed acquisition](https://www.mobihealthnews.com/news/babylon-health-sells-majority-uk-assets-emed); [Telecare Aware](https://telecareaware.com/babylon-health-shuts-us-operations-goes-into-uk-receivership) (accessed 2026-10-27).
10. [meddeviceonline.com — AI diagnostics patent eligibility](https://www.meddeviceonline.com/doc/how-to-navigate-patent-eligibility-of-ai-driven-diagnostics-0001); [IPWatchdog — diagnostics §101](https://ipwatchdog.com/2019/04/14/patent-eligibility-of-medical-diagnostics-inventions-where-are-we-now-and-where-is-there-to-go) (accessed 2026-10-27).

## Implications for AegisMed

1. **Re-scope the provisional's DEMAT claims** (with patent counsel): from
   "entropy-based triage" to the deterministic mechanism — bounded question
   bank + triage bands + out-of-scope refusal + conformal-before-agreement
   calibration — as a system claim with the SNOMED/ICD-11 cold-start story.
2. **Run a professional prior-art search** against CPC G16H50/20 with the
   §2 search recipe BEFORE the PCT decision; the JAMIA 2026 paper must be
   cited to the examiner proactively, not discovered by them.
3. **Check Babylon's IP disposition** (USPTO assignments, Chapter 7 asset
   schedule) before asserting freedom to operate in conversational triage.
4. **File the sequencing insight** (conformal sets before agreement blending,
   with the 90%→74% collapse as motivation) — it is concrete, measurable, and
   currently unclaimed in the literature found.
5. **Do not claim "multi-agent diagnosis"** as invention; the JAMIA/NeurIPS/
   Nature record makes that a rejection magnet. Claim the *selection policy*
   and *safety contract* instead.
6. **Paper positioning (CHIL):** lead with the honest evaluation on external
   vignettes (DxBench protocol) rather than the internal 98% — the internal
   number is now indefensible against AgentClinic/Q4Dx reviewers
   (cross-ref `04`, `06`).
7. **Keep the 12-question bank bounded and versioned** — the "bounded bank"
   element is part of the distinguishable mechanism; document its construction
   methodology in the spec.
