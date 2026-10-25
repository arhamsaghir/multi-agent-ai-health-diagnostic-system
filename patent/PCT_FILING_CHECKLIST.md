# AegisMed — PCT International Application Filing Checklist

**Document Version:** 1.0 · **Date:** 2026-10-25 ·
**Status: `BLOCKED: legal` — strictly gated on the provisional
application being filed first.** No PCT step below may be executed until
the provisional application number exists (`BLOCKED: user action`, see
`FILING_CHECKLIST.md`). This document is a procedural map for the
applicant and patent counsel, not legal advice; all fees and deadlines
must be confirmed by counsel before reliance.

**Invention title (as disclosed):** *System and Method for Dynamic
Entropy-Minimizing Active Clinical Triage and Evidential Multi-Agent
Diagnostic Conflict Arbitration.*

## 1. Priority anchor

| Item | Value |
|---|---|
| Priority document | Phase 3 provisional (IPO Form 1/2 route or USPTO §111(b) route) |
| Priority date `D0` | **TBD — insert the actual provisional filing date** (expected window: October 2026) |
| Paris Convention window | `D0 + 12 months` — PCT application must be filed on or before this date |
| Absolute novelty guard | The CHIL manuscript (`paper/phase3-paper/main.pdf`) and any public defense material must remain embargoed until `D0`-anchored protection is in place — see §6 |

## 2. Route selection

### Option A — IPO as Receiving Office (RO) *(default, per `FILING_CHECKLIST.md`)*
- File PCT request (IPO RO/ISA worksheet) through `ipindia.gov.in`
  e-filing with the PCT request form (PCT/RO/101) adapted for IPO RO use.
- Applicant/inventor: Arham Saghir & AegisMed contributors; address for
  service via the registered Indian patent agent (Form 26 already on the
  provisional checklist).
- International Search Authority election: ISA selection (e.g., [ISA
  chosen by counsel]) made on filing or within 1 month.

### Option B — USPTO/IB as Receiving Office
- File via USPTO Patent Center (EFS-Web successor) as RO/US, claiming
  priority to the §111(b) provisional.
- Same 12-month window; US national-phase treatment later becomes a
  formality (§351 national stage) rather than a fresh filing.

**Decision gate (counsel):** RO choice affects ISA quality, fees, and
language; both preserve the Paris priority date identically.

## 3. Timeline (all dates keyed to `D0`)

| Deadline | Event | Owner | Status |
|---|---|---|---|
| `D0` | Provisional filed; application number secured | User + agent | `BLOCKED: user action` |
| `D0 + 8 months` (recommended) | PCT prior-art search commissioned internally; specification consolidated (provisional text + 4.1 FHIR embodiments addendum) | Counsel + inventors | Pending `D0` |
| `D0 + 12 months` | **PCT international application filed** (RO per §2), priority claimed | Counsel | `BLOCKED: legal` |
| `D0 + 16 months` (target) | International Search Report + Written Opinion received | ISA | — |
| `D0 + 18 months` | International publication (WO) — embargo ends per publication | WIPO RO/IB | — |
| `D0 + 19 months` | Chapter II demand (optional, only if Written Opinion is adverse) | Counsel | — |
| `D0 + 30 months` | **National-phase entry deadline** (most offices; confirm per-office) | Counsel | — |
| `D0 + 30/31 months` | Regional-phase entry (EPO), supplementary search where elected | Counsel | — |

## 4. National-phase entry map (30 months from `D0` unless noted)

| Office | Route | Notes |
|---|---|---|
| India (IPO) | National phase | Priority origin; Section 3(k)/3(i) defense per `PATENT_AGENT_BRIEF.md` |
| USPTO | §371 national stage | If RO/US used, continuation from provisional; §101 Alice strategy per brief |
| EPO | Regional phase | Single examination, unitary effect optional; computer-implemented invention (G-II) approach |
| United Kingdom | National / EPO validation | High-choice flexibility, lower cost |
| Japan (JPO) | National phase | Claim-fee structure differs; J-PlatPat translations required |
| China (CNIPA) | National phase | Mandatory filing agent; invention-utility model dual not applicable to PCT |
| Canada (CIPO) | National phase | English filings accepted |
| Australia (IP Australia) | National phase | Innovation-patent alternative no longer available; standard patent only |

Offices beyond this list are optional and cost-driven; counsel should
prune to markets with credible clinical-CDSS commercialization.

## 5. Cost anchors (indicative, verify at filing)

| Item | Approximate |
|---|---|
| PCT filing fee (electronic, RO) | ~1,330–1,630 CHF (incl. transmittal + search fee; ISA-dependent) |
| International publication fee | ~1,600 CHF (deducted from search fee overpayment where applicable) |
| National-phase entry per office | ~2,000–6,000 USD equivalent each incl. translations + agents |
| Total 30-month programme (8 offices) | Order of 40,000–60,000 USD — **budget decision required by `D0 + 18 months`** |

## 6. Embargo status through the PCT window

- **Novelty embargo remains in force from now until international
  publication (`D0 + 18 months`).** The 4.1 FHIR interoperability layer
  (`src/core/fhir_mapping.py`, `src/api/routes/fhir.py`) and the
  containerized deployment are new embodiments added under this embargo;
  they are covered by the claim addendum (`FHIR_INTEROP_CLAIM_ADDENDUM.md`).
- Do not publish, demo publicly, or upload the CHIL manuscript before
  the priority-securing filing exists. The OpenReview upload (Phase 3
  blocked item) stays gated on the same condition.

## 7. Blocked-item register

| Item | Status |
|---|---|
| Provisional application number (priority anchor `D0`) | `BLOCKED: user action` |
| PCT filing decision (RO choice, ISA election, office set) | `BLOCKED: legal` — counsel |
| Fee budget approval for the 8-office national phase | `BLOCKED: user action` |
| Claim-set consolidation for PCT (provisional + FHIR addendum) | Ready in draft — `FHIR_INTEROP_CLAIM_ADDENDUM.md`; counsel review required |
