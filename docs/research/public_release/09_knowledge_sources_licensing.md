# Medical Knowledge Sources & Licensing (S9)

**Scope:** what terminology, guideline, drug, and patient-education sources can a
consumer symptom-checker legally build on in 2026 — with India as the primary
market — and what the licensing actually permits.

**TL;DR:** Almost the entire clinical-terminology layer AegisMed needs is free
or public domain: SNOMED CT is free inside India (member country, no-cost
Affiliate License), ICD-11 is free and explicitly licenses "clinical decision
support" and "AI training" uses, RxNorm/RxNav drug data is public domain, and
MedlinePlus Connect gives a free authoritative patient-education API keyed by
ICD-10/RxNorm codes. The two real licensing traps are (1) WHO guideline text
— CC BY-NC-SA, i.e. **non-commercial** — which the current AegisMed RAG corpus
already embeds, and (2) NICE content, which requires paid written permission
outside the UK. There is no mature open-source symptom-checker engine: the
field leader (Infermedica) is fully proprietary, which means a self-built
engine over open terminologies is both the viable path and the novelty story.

---

## 1. SNOMED CT — free in India (member country)

SNOMED International charges nothing for use in Member countries; **India is a
Member country** (54 Members globally). Use requires a no-cost **Affiliate
License** obtained via the MLDS portal; India's National Resource Centre for
EHR Standards (NRCeS) documents the local registration path.

- "SNOMED International does not charge for Affiliate Licensing or for use of
  SNOMED CT in Member countries." — [snomed.org/get-snomed](https://www.snomed.org/get-snomed)
- India member page incl. the free Global Patient Set:
  [snomed.org/members/india](https://www.snomed.org/members/india)
- "If you intend to use, deploy, or distribute SNOMED CT within a Member
  country (like India), you must obtain a free Affiliate License." —
  [SNOMED CT License FAQ](https://ihtsdo.freshdesk.com/support/solutions/articles/4000217735-what-license-do-i-need-in-order-to-use-snomed-ct-and-where-do-i-get-it-)
- India registration guidance: [NRCeS — SNOMED CT](https://www.nrces.in/standards/snomed-ct); portal: [MLDS](https://mlds.ihtsdotools.org)
- Free use also extends to low-income territories per NLM:
  [nlm.nih.gov/healthit/snomedct/snomed_licensing.html](https://www.nlm.nih.gov/healthit/snomedct/snomed_licensing.html)

**Implication:** every finding/symptom/procedure code the KB needs is
licensable at ₹0 for an Indian deployment — the excuse "we use a hand-written
15-disease dict because terminologies are expensive" does not exist.

## 2. ICD-11 — free, explicitly licenses CDS + AI training

WHO provides free access to ICD-11 and a REST ICD API (OAuth2 on the WHO-hosted
version; a locally installable version also exists). WHO states ICD-11
licensing "supports lawful use for research, public health, clinical decision
support, and AI training across all WHO Member States."

- ICD API: [icd.who.int/icdapi](https://icd.who.int/icdapi) · License doc:
  [icd.who.int/docs/icd-api/license](https://icd.who.int/docs/icd-api/license)
- WHO FAQ: [ICD-11 implementation](https://www.who.int/standards/classifications/frequently-asked-questions/icd-11-implementation)
- WHO-FIC licensing hub: [who.int/standards/classifications/who-fic-interoperability-hub](https://www.who.int/standards/classifications/who-fic-interoperability-hub)
- No-key alternative for coding lookups: NLM Clinical Table Search Service
  offers a free ICD-11 search API "as is" ([lforms-service-vip.nlm.nih.gov](https://lforms-service-vip.nlm.nih.gov))

**Implication:** AegisMed's condition keys ("type 2 diabetes" strings) can be
replaced with ICD-11 codes end-to-end for free, which is also what FHIR/ABDM
exchanges expect.

## 3. RxNorm / RxNav — public domain drug data, keyless APIs

RxNorm (NLM) is treated as public domain (CC0-labeled distributions); the
RxNav REST APIs require **no key or registration**; NLM states use is allowed
"in commercially available systems," and the prescribable-content subset
"will remain in the public domain, and no license will be required."

- No-credential API profile: [qveris.ai/providers/rxnav](https://qveris.ai/providers/rxnav)
- Public-domain labeling: [Kaggle NLM RxNorm metadata](https://www.kaggle.com/datasets/nlm-nih/nlm-rxnorm/metadata)
- Commercial-use statement: [datasets/commons issue #223](https://github.com/datasets/commons/issues/223)
- Prescribable subset, NLM Tech Bull 2012: [nlm.nih.gov/pubs/techbull/so12](https://www.nlm.nih.gov/pubs/techbull/so12/brief/so12_umls_rxnorm_spl.html)

WEAK-EVIDENCE: exact current terms of the RxNav Drug–Drug Interaction API —
verify at [rxnav.nlm.nih.gov](https://rxnav.nlm.nih.gov) before building the
future medication-safety feature.

**Implication:** drug names, interactions, and NDC lookups for a future
"medication" input field cost nothing and need no key.

## 4. UMLS Metathesaurus — free, but license-gated redistribution

NLM charges nothing for UMLS but requires a signed license; historically
"LICENSEE is prohibited from distributing the UMLS Metathesaurus or subsets of
it"; since ~2019 redistribution of derived products with attribution is
relaxed, but some source vocabularies (SNOMED CT outside the US) keep separate
restrictions. QuickUMLS (F1 ≈ 0.72–0.74, ~135× faster than MetaMap) requires
this license.

- License page: [nlm.nih.gov/research/umls/knowledge_sources/metathesaurus/release_license_agreement.html](https://www.nlm.nih.gov/research/umls/knowledge_sources/metathesaurus/release_license_agreement.html)
- Historical prohibition text (2007AC): [nlm.nih.gov/research/umls/archive/pdfs/2007AC.pdf](https://www.nlm.nih.gov/research/umls/archive/pdfs/2007AC.pdf)
- Background/analysis: [PMC1839427](https://pmc.ncbi.nlm.nih.gov/articles/PMC1839427)

**Implication:** use the **UMLS REST API + SNOMED CT direct download (India
affiliate)** rather than shipping Metathesaurus subsets in the repo — the
current KB pattern of vendoring content in-repo is exactly what UMLS prohibits.

## 5. Patient-education content — MedlinePlus Connect (free)

MedlinePlus Connect is a free NLM web service that links **ICD-10, RxNorm, and
LOINC codes** to authoritative patient-education health topics — i.e., a
code-keyed, professionally reviewed "explain this condition to the patient"
API. (AegisMed currently generates `patient_explanation` from the LLM with a
rule-based fallback.)

- Service listing: [catalog.data.gov](http://catalog.data.gov) (MedlinePlus Connect for EHRs)
- Free-service confirmation: [NNLM](https://news.nnlm.gov)
- MedlinePlus Health Topics as a UMLS terminology: [NCBO BioPortal](https://bioportal.bioontology.org)

**Implication:** ground the patient-facing explanation pane in MedlinePlus
content keyed by the diagnosis code — reviewed content beats generated text
for safety and for regulator optics.

## 6. India-specific: ABDM / NRCeS FHIR — the national on-ramp

India's ABDM defines a **FHIR R4 Implementation Guide** (NRCeS ABDM IG, v6.5.0)
and an open sandbox with HIP/HIU APIs; health data is exchanged
consent-managed through gateways rather than centrally stored; production
connection requires passing government **certification milestones (M1/M2/M3)**.

- IG: [nrces.in/ndhm/fhir/r4](https://nrces.in/ndhm/fhir/r4)
- HIP/HIU guidelines: [abdm.gov.in PDF](https://abdm.gov.in/strapicms/uploads/HIP_HIU_Guidelines_f85df336ec.pdf)
- Consent/HDM analysis: [cybersigmacs.com/knowledge-center/abdm-health-data](https://cybersigmacs.com/knowledge-center/abdm-health-data)
- ABHA consent-based design study: [PMC10064942](https://pmc.ncbi.nlm.nih.gov/articles/PMC10064942)
- Certification milestones: [qualysec.com/abdm-integration-checklist](https://qualysec.com/abdm-integration-checklist)

**Implication:** AegisMed already speaks FHIR R4 — targeting the ABDM profile
set (instead of generic FHIR) is the single highest-credibility integration
for an India launch and bundles the consent architecture with it.

## 7. Guideline text — the two traps (WHO non-commercial; NICE paid)

- **WHO publications are CC BY-NC-SA 3.0 IGO**: reuse permitted with
  attribution for **non-commercial** purposes only, ShareAlike for
  adaptations ([who.int/copyright](https://www.who.int/copyright); license
  guide: [forumforopen.org](https://forumforopen.org/what-we-do/resources/open-science-resources/a-guide-to-creative-commons-licenses)).
  **The current AegisMed FAISS corpus embeds "WHO Guidelines — Acute
  Gastroenteritis" passages** (`data/vector_store/medical_knowledge_meta.json`)
  — a latent non-commercial clause on any monetized deployment.
- **CDC content is US public domain** (17 U.S.C. §105), freely reproducible
  with attribution, except embedded third-party material
  ([stacks.cdc.gov copyright policy](https://stacks.cdc.gov)).
- **NICE (UK)**: free UK reuse under the NICE UK Open Content Licence with
  attribution; **international/app syndication requires written permission
  and is subject to a fee** ([nice.org.uk/reusing-our-content](https://www.nice.org.uk/reusing-our-content);
  [UK licence](https://www.nice.org.uk/reusing-our-content/nice-uk-open-content-licence);
  [international](https://www.nice.org.uk/reusing-our-content/use-of-our-content-internationally);
  [syndication API / ECD10](https://www.nice.org.uk/corporate/ecd10)).

**Implication:** rebuild the RAG corpus on public-domain sources (CDC, NIH/
MedlinePlus, US federal guidance, Indian national programs/ICMR with
permission) plus WHO *citations* rather than embedded WHO *text* — or get a
commercial license from WHO before monetizing.

## 8. Open-weight medical LLMs — permissive options exist

| Model | License | Commercial use |
|---|---|---|
| BioMistral 7B | Apache 2.0 | Fully allowed (most permissive) |
| MedGemma 4B/27B (Google, May–Jul 2025) | Gemma Terms of Use | Allowed, with usage restrictions; not cleared for clinical decision-making |
| OpenBioLLM 8B/70B | Llama 3 Community License | Allowed under Meta policy; research-oriented |

- BioMistral collection paper: [Semantic Scholar](https://www.semanticscholar.org/paper/13b8934468665ecb586f491d7f9f6c460cb095e5)
- MedGemma release/analysis: [medium.com/@mahernaija](https://medium.com/@mahernaija/unlocking-the-future-of-medical-ai-with-medgemma-a1d3c75fba56)
- All three model cards carry "requires professional validation/regulatory
  compliance" language.

**Implication:** AegisMed's free-tier OpenRouter dependence (OmniRoute tunnel,
503 resets) has a permissive self-hostable escape hatch (BioMistral/MedGemma on
the same CPU container) if synthesis quality justifies the RAM.

## 9. No mature open-source symptom-checker engine exists

The leading engine (Infermedica) is fully proprietary: ~96% condition accuracy
claimed, 26 languages, 30M+ checkups, free developer tier ≈ 2,000 API calls
(English only), pricing on request; its medical KB is explicitly not open.
Comparable open engines are absent — surveys of the space find only
freemium/wrapper projects.

- [infermedica.com/solutions/infermedica-api](https://infermedica.com/solutions/infermedica-api)
- Free-tier FAQ: [developer.infermedica.com FAQ](https://developer.infermedica.com/documentation/overview/faq)
- Proprietary-KB statement: [Infermedica blog](https://infermedica.com/blog/articles/building-a-trusted-quality-digital-medical-knowledge-base)
- Landscape overview: [altexsoft.com symptom-checker APIs](https://www.altexsoft.com/blog/symptom-checker-apis)

**Implication:** "A deterministic, terminology-grounded, self-hosted triage
engine" is a genuinely open niche — the patent story and the product story
converge here.

## 10. Integration standard — CDS Hooks + FHIR terminology

HL7 CDS Hooks (STU 2.0.1) defines hook-based external CDS invocation from EHR
workflows; terminology validation runs through FHIR terminology servers
(Ontoserver — native SNOMED CT/LOINC, powers Australia's NCTS; HAPI FHIR has a
built-in terminology component; the public `tx.fhir.org/r4` is a free
reference endpoint).

- Spec: [cds-hooks.hl7.org/STU2](https://cds-hooks.hl7.org/STU2)
- Ontoserver docs: [ontoserver.csiro.au](https://www.ontoserver.csiro.au/docs/5.0/config-all.html)
- HAPI terminology/CDS discussion: [community.fhir.org](http://community.fhir.org/t/fhir-and-terminology-server/2778),
  [hapi-fhir#5238](https://github.com/hapifhir/hapi-fhir/issues/5238)

**Implication:** the "hospital-side" AegisMed mode should be a CDS Hook, not a
parallel UI — it reuses the FHIR layer AegisMed already has and makes the
clinician product distributable without portal credentials.

---

## Sources

1. [SNOMED International — Get SNOMED CT](https://www.snomed.org/get-snomed) (accessed 2026-10-27) — "does not charge for Affiliate Licensing or for use of SNOMED CT in Member countries."
2. [SNOMED International — India member page](https://www.snomed.org/members/india) (accessed 2026-10-27).
3. [SNOMED CT License FAQ — Affiliate License requirement in Member countries](https://ihtsdo.freshdesk.com/support/solutions/articles/4000217735) (accessed 2026-10-27).
4. [NLM — Licensing SNOMED CT](https://www.nlm.nih.gov/healthit/snomedct/snomed_licensing.html) (accessed 2026-10-27).
5. [NRCeS India — SNOMED CT](https://www.nrces.in/standards/snomed-ct) (accessed 2026-10-27).
6. [WHO ICD API](https://icd.who.int/icdapi) and [ICD-11 license docs](https://icd.who.int/docs/icd-api/license) (accessed 2026-10-27) — "supports lawful use for research, public health, clinical decision support, and AI training."
7. [NLM Clinical Table Search Service — ICD-11](https://lforms-service-vip.nlm.nih.gov) (accessed 2026-10-27) — "provided 'as is' and free of charge."
8. [Kaggle NLM RxNorm — CC0/public-domain metadata](https://www.kaggle.com/datasets/nlm-nih/nlm-rxnorm/metadata) (accessed 2026-10-27).
9. [GitHub datasets/commons #223 — NLM commercial-use statement](https://github.com/datasets/commons/issues/223) (accessed 2026-10-27).
10. [NLM Tech Bull 2012 — RxNorm prescribable subset public domain](https://www.nlm.nih.gov/pubs/techbull/so12/brief/so12_umls_rxnorm_spl.html) (accessed 2026-10-27).
11. [UMLS License Agreement](https://www.nlm.nih.gov/research/umls/knowledge_sources/metathesaurus/release_license_agreement.html); [2007AC appendix — redistribution prohibition](https://www.nlm.nih.gov/research/umls/archive/pdfs/2007AC.pdf); [PMC1839427](https://pmc.ncbi.nlm.nih.gov/articles/PMC1839427) (accessed 2026-10-27).
12. [catalog.data.gov — MedlinePlus Connect for EHRs](http://catalog.data.gov); [NNLM — free NLM service](https://news.nnlm.gov) (accessed 2026-10-27).
13. [NRCeS — FHIR Implementation Guide for ABDM v6.5.0](https://nrces.in/ndhm/fhir/r4); [ABDM HIP/HIU guidelines PDF](https://abdm.gov.in/strapicms/uploads/HIP_HIU_Guidelines_f85df336ec.pdf); [ABDM certification checklist](https://qualysec.com/abdm-integration-checklist); [PMC10064942](https://pmc.ncbi.nlm.nih.gov/articles/PMC10064942) (accessed 2026-10-27).
14. [WHO copyright policy](https://www.who.int/copyright) — CC BY-NC-SA 3.0 IGO for publications (accessed 2026-10-27).
15. [CDC content copyright policy](https://stacks.cdc.gov) — US public domain (accessed 2026-10-27).
16. [NICE — Reusing our content](https://www.nice.org.uk/reusing-our-content), [UK Open Content Licence](https://www.nice.org.uk/reusing-our-content/nice-uk-open-content-licence), [International use](https://www.nice.org.uk/reusing-our-content/use-of-our-content-internationally), [ECD10 syndication](https://www.nice.org.uk/corporate/ecd10) (accessed 2026-10-27).
17. [Infermedica API](https://infermedica.com/solutions/infermedica-api), [developer FAQ](https://developer.infermedica.com/documentation/overview/faq), [KB blog](https://infermedica.com/blog/articles/building-a-trusted-quality-digital-medical-knowledge-base), [AltexSoft landscape](https://www.altexsoft.com/blog/symptom-checker-apis) (accessed 2026-10-27).
18. [BioMistral / MedGemma / OpenBioLLM licensing summaries](https://www.semanticscholar.org/paper/13b8934468665ecb586f491d7f9f6c460cb095e5), [MedGemma analysis](https://medium.com/@mahernaija/unlocking-the-future-of-medical-ai-with-medgemma-a1d3c75fba56) (accessed 2026-10-27).
19. [HL7 CDS Hooks STU 2](https://cds-hooks.hl7.org/STU2); [Ontoserver docs](https://www.ontoserver.csiro.au/docs/5.0/config-all.html); [HAPI terminology threads](https://github.com/hapifhir/hapi-fhir/issues/5238) (accessed 2026-10-27).

## UNKNOWN — how to find out

- Exact WHO ICD-11 attribution clause wording → read the PDF at icd.who.int/docs/icd-api/license before release.
- RxNav Drug–Drug Interaction API current terms → rxnav.nlm.nih.gov API pages.
- Whether ICMR/Indian national guidelines carry reusable licenses → ICMR publications portal.
- MedGemma 27B RAM requirements for the CPU-only AegisMed container → benchmark locally before committing.
