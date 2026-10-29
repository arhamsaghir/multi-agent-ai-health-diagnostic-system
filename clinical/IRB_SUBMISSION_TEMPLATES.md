# IRB Submission Templates — AegisMed Retrospective Validation

**Status: `BLOCKED: user action`.** These templates are drafted for the
reviewing institution's IRB/ethics committee. Placeholders in `[…]` must
be completed by the faculty PI and the clinical co-investigator before
submission; the study may not begin until approval and the data access
agreement are in hand. Companion documents: `VALIDATION_PROTOCOL.md`
(design) and `VALIDATION_HARNESS_DESIGN.md` (analysis tooling).

---

## Template 1 — Protocol Synopsis (IRB form narrative)

**Title:** Retrospective evaluation of a multi-agent clinical decision
support system (AegisMed) for diagnostic triage accuracy and calibration.

**Principal Investigator:** [faculty PI name, department]
**Student investigator:** Arham Saghir, B.Tech candidate, [department]
**Clinical co-investigator:** [licensed physician name, registration no.]
**Category requested:** Expedited / minimal risk — retrospective chart
review of de-identified extracts; no interaction with patients; no
change to clinical care.

**Background.** AegisMed is a clinical decision support prototype that
ranks differential diagnoses from a presenting narrative (and optional
chest radiograph) using an active questioning strategy (DEMAT) and
evidential arbitration. Its performance has been characterised only on
synthetic cases; the Phase 3 benchmark (200 synthetic cases, top-1
98.0% vs 93.0% single-pass, p=0.0339 — a retired self-generated
measurement, not an accuracy result; see `data/benchmarks/RETIREMENT.md`)
cannot be generalised to clinical
encounters.

**Aim.** Estimate top-1/top-3 accuracy, calibration (ECE, Brier), triage
efficiency, and exploratory safety endpoints on ≥350 retrospective adult
encounters (target 500 screened), comparing the DEMAT arm to the
system's own single-pass arm.

**Methods summary.** The honest broker produces Safe-Harbor
de-identified extracts (§7 of the protocol: all 18 identifier classes
removed, dates shifted per patient, ages >89 banded, two-pass free-text
scrub). Research staff run both pipeline arms on each extract. No
third-party LLM is used in validation runs; report synthesis uses the
deterministic rule-based fallback so no data leaves institutional
custody. Only aggregate results are retained.

**Risks.** The only plausible risks are (a) re-identification from
residual free-text identifiers — mitigated by two-pass scrubbing and
honest-broker key custody — and (b) incidental findings in the research
record — not applicable, as no individual results are returned to care
teams and the system is not used for care during the study.

**Consent request.** **Waiver of individual consent** is requested under
[45 CFR 46.116(f) / national equivalent]: the research is minimal risk,
uses only de-identified retrospective data, could not practicably be
carried out without the waiver (contacting patients for consent on
completed encounters would be disproportionate), and patients retain
their rights through the data governance board's oversight of the
export.

**Data retention.** Extracts destroyed within 90 days of study closure;
aggregate artefacts retained.

---

## Template 2 — Data Use Agreement checklist

To be executed between [institution] and the research unit before export.

- [ ] Purpose limitation: diagnostic-accuracy research only; no model
      training on patient data; no commercial use.
- [ ] Permitted users: named study personnel only (PI, co-investigator,
      student investigator); no subcontractors.
- [ ] De-identification standard: HIPAA Safe Harbor 18 identifiers,
      attested by the honest broker (method statement attached).
- [ ] No re-identification attempts; no contact with patients.
- [ ] Location of analysis: [institution-controlled environment]; no
      upload to external services (LLM providers included).
- [ ] Security controls: encrypted at rest and in transit; access log.
- [ ] Incident reporting: suspected breach reported to [office] within
      24 hours.
- [ ] Retention and destruction schedule: 90 days post-closure,
      certified in writing.
- [ ] Publication policy: aggregate statistics only; no cell sizes
      below 11; case narratives quoted only with IRB-approved redaction.
- [ ] Termination clause: export recalled on agreement breach.

---

## Template 3 — Consent-waiver justification (one page)

**Study:** AegisMed retrospective validation · **Request:** waiver of
informed consent for use of de-identified retrospective encounters.

1. **Minimal risk.** The study analyses already-complete encounters via
   de-identified extracts; no intervention, no contact, no change to
   care. The only risk is re-identification, addressed by Safe-Harbor
   de-identification, per-patient date shifting, two-pass text scrubbing,
   and honest-broker key custody (re-identification keys are not
   accessible to the research team).
2. **Could not practicably proceed without waiver.** The cohort is
   completed encounters from routine care; contacting each patient to
   consent to a chart review of their past visit would impose burden
   disproportionate to minimal-risk research and would introduce
   selection bias that undermines the safety endpoints.
3. **Not adverse to rights and welfare.** Patients receive care
   unchanged; no individual result is generated for clinical use; the
   waiver is overlayed by the data governance board's approval of the
   export scope.
4. **De-identification attestation.** The honest broker attests the
   extracts meet the Safe-Harbor standard; the research dataset carries
   only study pseudonyms.

**Alternatives considered.** Prospective consent collection was rejected
as infeasible for retrospective encounters and unnecessary given the
de-identification standard; limited-dataset route was rejected because
the study design requires free-text presenting narratives, which the
limited-dataset route would still require scrubbing to the same standard.

---

## Submission checklist (before upload to the IRB portal)

- [ ] Protocol v1.0 (`clinical/VALIDATION_PROTOCOL.md`) converted to the
      institution's template and signed by PI + clinical co-investigator.
- [ ] Conflict-of-interest disclosures for all study personnel.
- [ ] Honest-broker de-identification method statement attached.
- [ ] Draft data use agreement (Template 2) attached.
- [ ] Recruitment materials: N/A (retrospective, no contact).
- [ ] Data safety monitoring: N/A (no prospective intervention); interim
      de-identification audit scheduled once at 10% export.
- [ ] All `BLOCKED: user action` items in `VALIDATION_PROTOCOL.md` §9
      resolved or explicitly time-boxed.
