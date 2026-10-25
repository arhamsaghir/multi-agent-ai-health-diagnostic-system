# Draft Addendum — FHIR R4 Interoperability Dependent Claims

**Prepared for:** Registered Patent Agent / Counsel
**Date:** 2026-10-25
**Status: DRAFT — for counsel review only. Not legal advice; claim
language, antecedent basis, and statutory compliance must be settled by
counsel. Embodiments described here were implemented in Phase 4.1
(`src/core/fhir_mapping.py`, `src/api/routes/fhir.py`, 15 passing tests)
and are covered by the novelty embargo until priority-securing filings
exist.**

## Purpose

Extend the 12-claim provisional set with dependent claims covering the
HL7 FHIR R4 interoperability embodiments, so that the PCT
international application (see `PCT_FILING_CHECKLIST.md`) claims not
only the triage/arbitration engines but also the standards-based
clinical-system integration that makes them deployable inside hospital
EHR ecosystems. Interoperability claims also strengthen the
technical-effect story relied on for the computer-implemented-invention
hurdles (India §3(k), US §101): mapping to FHIR R4 is the concrete,
verifiable bridge between the invention's internal evidence state and
real clinical record systems.

## New dependent claims (draft numbering continues the provisional set)

**Claim A** *(method, depends on the independent DEMAT method claim 1)*
The method of claim 1, further comprising serialising the arbitrated
differential diagnosis and triage state into an HL7 FHIR R4 Bundle
comprising: (i) a Patient resource carrying the encounter demographics;
(ii) one Condition resource per ranked differential candidate, each
expressing the candidate's posterior probability; (iii) a RiskAssessment
resource enumerating per-outcome probability decimals and carrying a
triage-severity annotation; wherein the Bundle is exchanged with an
external clinical record system over the same request-response
transaction that invoked the method.

**Claim B** *(method, depends on Claim A)*
The method of claim A, wherein the triage state further comprises the
Shannon diagnostic entropy of the differential, and the FHIR Bundle
additionally comprises an Observation resource whose value quantity
expresses said entropy in bits, whereby a consuming record system can
track diagnostic-ambiguity collapse across encounters.

**Claim C** *(method, depends on Claim A)*
The method of claim A, wherein the FHIR Bundle further comprises a
DocumentReference resource whose content attachment carries the
clinician-oriented narrative and a non-clinical-use disclaimer, encoded
such that the narrative survives round-trip export and re-import by a
conforming FHIR consumer.

**Claim D** *(method, depends on Claim A)*
The method of claim A, further comprising receiving an inbound FHIR R4
Bundle as the sole encounter input, extracting symptom observations from
Observation resources (value-string or coded display text) and Condition
resources, and deriving demographics from the Patient resource including
age computed from a birth date, wherein the active questioning of claim 1
operates on the extracted symptom state without any non-FHIR input
channel.

**Claim E** *(system, depends on the independent system claim)*
A system according to the independent system claim, wherein the
orchestration layer exposes the arbitrated differential through an
HTTP interface that (i) accepts a FHIR R4 Bundle with media type
`application/fhir+json` and returns a FHIR R4 Bundle of the same media
type, and (ii) exports a previously arbitrated encounter identified by
a session identifier as a FHIR R4 Bundle equivalent to the one produced
at arbitration time, whereby externally persisted encounters and live
arbitrations are indistinguishable to a consuming record system.

**Claim F** *(system, depends on Claim E)*
The system of claim E, wherein the interface validates all inbound and
outbound resources against the FHIR R4 normative models at
construction time, rejecting non-conforming bundles prior to any
inference, whereby downstream arbiters receive only structurally
valid clinical data.

## Technical-effect notes for counsel

1. **Round-trip equivalence is the inventive hook.** The mapping layer
   preserves the arbitrated evidence state (ranked posterior, entropy,
   severity note, narrative) through serialisation and re-import —
   `session_to_bundle` → `bundle_to_diagnosis_request` round-trip is
   test-verified (export→import equivalence test in
   `tests/unit/test_fhir_mapping.py`). Interoperability layers in prior
   art exchange flat codes, not the arbitration's evidence state.
2. **Entropy as a first-class FHIR Observation** (Claim B) is believed
   novel: diagnostic uncertainty becomes a recordable, trackable
   clinical observation rather than an internal implementation detail.
3. **Standards-anchored claim drafting strategy:** frame the FHIR layer
   as the *technical means* by which the DEMAT/EN-SCAF engines achieve
   the clinical-integration effect — consistent with the
   computer-implemented-invention posture in `PATENT_AGENT_BRIEF.md`
   (India §3(k) technical-contribution argument; US §101
   integration-into-practical-application argument).

## Traceability (claims → implementation → evidence)

| Draft claim | Implementation | Tests |
|---|---|---|
| A | `diagnosis_response_to_bundle()` (Patient, Condition×n, RiskAssessment) | `tests/unit/test_fhir_mapping.py::test_response_bundle_*` |
| B | entropy Observation, `valueQuantity` bits | `test_entropy_observation_*` |
| C | DocumentReference narrative (base64) + disclaimer | `test_narrative_round_trip` |
| D | `bundle_to_diagnosis_request()` (Observation/Condition/Patient extraction, computed age) | `test_inbound_*`, `test_empty_bundle_rejected` |
| E | `POST /api/fhir/diagnose`, `GET /api/fhir/diagnosis/{id}` | `tests/test_fhir_endpoints.py` |
| F | `fhir.resources` R4B model validation at construction; 400 on malformed | `test_malformed_bundle_rejected` |

## Integration into the PCT specification

On consolidation (`D0 + 8 months` per the PCT checklist), counsel should:
1. insert these dependent claims into the claim set under counsel's own
   numbering,
2. add a short "Standards-Based Clinical Interoperability" embodiment
   section describing the mapping (the traceability table above is the
   source of truth),
3. update FIG. 2/FIG. 4 references if the drawings are extended with a
   FHIR exchange diagram (`scripts/patent/generate_patent_figures.py`
   can regenerate the bundle).
