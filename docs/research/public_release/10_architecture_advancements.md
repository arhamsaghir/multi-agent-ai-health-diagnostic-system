# Architecture Advancements for Medical Decision Support (S10)

**Scope:** the architectural patterns that separate a 2025-26-grade consumer
diagnostic assistant from a 2023-grade one — retrieval, generation discipline,
evaluation, orchestration, and privacy.

**TL;DR:** The 2026 consensus architecture for consumer symptom assessment is
an **LLM conversation layer over a deterministic, certified triage core, with
guideline-grounded RAG** (cross-ref `01_symptom_checker_landscape.md` §LLM
era). The concrete advancements AegisMed lacks, in order of measured impact:
hybrid retrieval (BM25+dense — consistently better recall than dense-only),
schema-constrained generation (structured outputs measurably enable diagnosis
workflows), guideline-bound generation (Almanac: +18% accuracy, and ungrounded
LLM citations were 31% fabricated), rubric-based LLM-judge evaluation (ordinal
agreement with physician panels is achievable), and multi-agent orchestration
with a verification step (Mount Sinai: better accuracy at up to 65× fewer
compute resources than naive ensembles).

---

## 1. Retrieval: hybrid beats dense-only, and grounding beats parametric

- A 2026 public-health RAG study comparing dense, sparse, and hybrid retrieval
  across embedding models and corpus variants found **hybrid retrieval
  consistently improves recall** ("Healthier LLMs", takara.ai summary of
  arXiv:2607.06641 — fetch the arXiv page for exact deltas before citing
  numbers; WEAK-EVIDENCE on magnitude).
- The **MIRAGE benchmark** (Ning et al., "Benchmarking Retrieval-Augmented
  Generation for Medicine", Findings of ACL 2024) established the standard
  method: retrieve into a medical corpus, then measure whether grounding
  changes model predictions — this is the evaluation AegisMed's 25-query
  self-eval should be replaced by.
- Agent-verified cross-ref: Almanac (guideline-grounded ChatGPT) **+18%
  accuracy over vanilla ChatGPT**, and 31% of ungrounded citations "completely
  fabricated" (details in `04_llm_agentic_diagnosis_sota.md` §RAG).

**AegisMed today:** dense-only FAISS, 500 passages, no BM25 leg, no citation
enforcement in the synthesis output (`src/agents/rag/agent.py` returns raw
`knowledge` text; `src/agents/synthesis/agent.py` does not require per-claim
citations).

## 2. Generation discipline: schema-constrained outputs are a measured win

- "Structured Outputs Enable General-Purpose LLMs to be Used for Diagnosis"
  (Mar 2025, ResearchGate) — a seven-step clinical-diagnosis cognitive process
  enforced by structured outputs improved accuracy and completeness of medical
  answers (fetch for exact N/accuracy; WEAK-EVIDENCE on magnitude).
- Constrained decoding state of the art moved from token-masked JSON-schema
  enforcement to **draft-conditioned constrained decoding (DCCD, Feb 2026)**,
  separating semantic planning from syntactic enforcement to fix the quality
  degradation naive masking causes ([HuggingFace DCCD](https://huggingface.co/papers/2602.06567) — verify ID).
- A **clinical safety/hallucination evaluation framework** for LLM outputs
  exists as a reusable protocol (medRxiv, Sep 2024).

**AegisMed today:** the synthesis agent parses free-form LLM JSON with a
try/except fallback to rule-based generation (`src/agents/synthesis/agent.py`,
`src/llm/openrouter_client.py:generate_json`) — no schema guarantee, so a
malformed response silently degrades the whole report.

## 3. Evaluation: rubric-based LLM-judge with physician anchoring

- "Can LLMs Score Medical Diagnoses and Clinical Reasoning as Well as Expert
  Panels?" (Lanfrica record) — uncalibrated LLM-jury scores are systematically
  **lower** than clinician panels but preserve **ordinal agreement**;
  calibration against a physician panel is mandatory before use.
- PRISMA scoping review of LLM-as-a-Judge in healthcare (Semantic Scholar) and
  the healthcare LLM-judge automation paper (May 2026, ResearchGate) document
  the rubric patterns; practical guidance favors PASS/FAIL or 3-point scales,
  one criterion per rubric line.
- OpenAI HealthBench is the template at scale: 5,000 conversations, 48,562
  physician-written weighted rubric criteria including negative points
  (cross-ref `06_datasets_evaluation.md` §HealthBench).

**AegisMed today:** no automated report-quality evaluation exists; the PDF
report is verified only by eye.

## 4. Orchestration: multi-agent with verification, not ensemble-for-its-own-sake

- Mount Sinai's orchestrated multi-agent healthcare systems **outperform single
  agents while using up to 65× fewer computing resources** than naive
  parallel-expert ensembles (Mount Sinai news release — fetch for the exact
  study; WEAK-EVIDENCE on the 65× figure).
- The JAMIA 2026 orchestrator–specialist framework for **secondary headache
  diagnosis** improved accuracy and transparency (Wu et al.,
  [academic.oup.com/jamia/article/33/10/1910/8719545](https://academic.oup.com/jamia/article/33/10/1910/8719545))
  — this is both a pattern to adopt and **direct prior art** (cross-ref `11_patent_prior_art.md`).
- MDAgents' adaptive solo-vs-team routing (NeurIPS 2024) remains the reference
  for when to escalate from one agent to a team (cross-ref `04_llm_agentic_diagnosis_sota.md`).

**AegisMed today:** fixed sequential pipeline for every input (`src/agents/
orchestrator/agent.py` `_build_graph`); no verification/critic step between
synthesis and delivery; no adaptive depth.

## 5. Privacy: local inference is credible, numbers are blog-grade

2025-26 practitioner literature shows strong momentum for quantized local LLMs
in health (GGUF/4-bit) driven by PHI-never-leaves-device, zero cloud cost, and
offline use (GoCodeo Jun 2025; sahin.io guide; practitioner accounts on
r/Qwen_AI). **All specific performance numbers found are WEAK-EVIDENCE**
(blog-grade, no benchmarks fetched).

**AegisMed today:** all synthesis goes through the OmniRoute SSH tunnel
(`config/settings.py omniroute_base_url = http://localhost:20128/v1`) — a
single point of failure that also ships symptom text off-box; the CPU-only
container cannot currently host a competitive LLM.

## 6. Reliability engineering the field now assumes

- Timeout + fallback chains exist in AegisMed (`openrouter_client.py`), but the
  research consensus is to pair them with **deterministic degradation that is
  visibly labeled** — cross-ref the triage-safety findings in
  `01`/`08`: silent fallback to "a plausible-looking report" is the exact
  anti-pattern (`frontend/src/lib/api.ts` demo-results-on-error is the worst
  instance).
- Session/state: FHIR R4 + consent-managed exchange (ABDM) is the national
  pattern in India (cross-ref `09_knowledge_sources_licensing.md` §ABDM).

---

## Sources

1. [Healthier LLMs: RAG for Public Health (arXiv:2607.06641 via takara.ai)](https://tldr.takara.ai/p/2607.06641) — hybrid retrieval improves recall (accessed 2026-10-27).
2. [Benchmarking RAG for Medicine (MIRAGE)](https://www.researchgate.net/publication/384207131_Benchmarking_Retrieval-Augmented_Generation_for_Medicine) (accessed 2026-10-27).
3. [Fine-tuning/RAG/hybrid adaptation for clinical decision-making — systematic review](https://magazine.ingentium.com/2026/09/19/fine-tuning-retrieval-augmented-generation-and-hybrid-adaptation-of-language-models-for-clinical-decision-making-in-health-care-systematic-review) (accessed 2026-10-27).
4. [Structured Outputs Enable General-Purpose LLMs to be Used for Diagnosis](https://www.researchgate.net) (Mar 2025, accessed 2026-10-27).
5. [DCCD — draft-conditioned constrained decoding (Feb 2026)](https://huggingface.co/papers/2602.06567) (ID to verify, accessed 2026-10-27).
6. [A Framework to Assess Clinical Safety and Hallucination (medRxiv, Sep 2024)](https://www.medrxiv.org) (accessed 2026-10-27).
7. [Can LLMs Score Medical Diagnoses as Well as Expert Panels?](https://lanfrica.com/en/record/can-llms-score-medical-diagnoses-and-clinical-reasoning-as-well-as-expert-panels) (accessed 2026-10-27).
8. [LLM-as-a-Judge in Healthcare — PRISMA scoping review](https://www.semanticscholar.org/paper/b0df1011ceca3a396fed711c911547c30474789d) (accessed 2026-10-27).
9. [Automating Evaluation of AI Text Generation in Healthcare with LLM-as-a-Judge](https://www.researchgate.net/publication/391081789) (May 2026, accessed 2026-10-27).
10. [Wu et al., Orchestrator–specialist multi-agent CDSS, JAMIA 2026](https://academic.oup.com/jamia/article/33/10/1910/8719545) (accessed 2026-10-27).
11. Mount Sinai news — multi-agent healthcare, up to 65× fewer compute resources (via search; primary study to fetch, WEAK-EVIDENCE).
12. Local-LLM health practice literature: [GoCodeo (Jun 2025)](https://www.gocodeo.com), [sahin.io guide](https://sahin.io), [r/Qwen_AI practitioner thread](https://www.reddit.com/r/Qwen_AI/comments/1tiwrf3/local_llm_privacy_first_doctor) (WEAK-EVIDENCE, accessed 2026-10-27).
13. [OpenAI HealthBench](https://openai.com/index/healthbench/) — template (full data in `06_datasets_evaluation.md`).

## Implications for AegisMed

1. **Retrieval** (`src/agents/rag/agent.py`): add a BM25 leg (e.g., `rank_bm25`
   over the same corpus) and reciprocal-rank-fusion with FAISS; keep the
   500-passage corpus but version it per guideline release.
2. **Citation enforcement** (`src/agents/synthesis/agent.py`): require every
   recommendation in the report to carry a retrieved-source ID; reject
   regeneration if a claim lacks one (grounded-generation contract, not
   best-effort).
3. **Schema-guaranteed synthesis**: replace `generate_json` try/except with
   schema-constrained generation (OpenRouter structured outputs or local
   grammar masking); on failure, degrade to the rule-based report **labeled as
   such** in the UI, never silently.
4. **Kill the fabricated-fallback** (`frontend/src/lib/api.ts`
   `getDemoResults` on API error) — replace with an explicit error state.
5. **Verification node** in the graph (`src/agents/orchestrator/agent.py`):
   a cheap critic pass over the synthesized report (red-flag presence,
   citation coverage, severity/doctor-alert consistency) before delivery —
   the JAMIA/Mount Sinai pattern.
6. **Adaptive depth** (MDAgents pattern): solo fast-path for low-entropy
   presentations; full team only when DEMAT entropy stays high after round 1.
7. **LLM-judge eval harness** (`scripts/benchmark/`): rubric-based report
   grading (safety, grounding, actionability, calibration) calibrated against
   the DxBench/HealthBench rubric style, reported with CIs.
8. **Privacy roadmap**: quantify a quantized BioMistral/MedGemma 4B on the CPU
   container as a fallback synthesizer; keep OmniRoute as primary but make the
   off-box PHI path an explicit product decision.
9. **Event transparency**: SSE already streams agent steps — add per-step
   uncertainty + provenance fields so the UI can show *why* the report says
   what it says.
