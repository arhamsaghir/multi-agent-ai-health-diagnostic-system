# Spec: `publication-truth`

**Module id:** `publication-truth` · **Wave:** 0–1 · **Owner:** principal investigator
**Closes gaps:** 7, 16 (partial) · **Depends on:** `w0-benchmark-honesty`
**Blocks:** `w3-patent`
**Status:** not started — **phase A is urgent**

## Objective

**Every claim the project publishes describes something the code can defend.**

This module covers the paper, the patent specification, and the repository
documentation. It is separated from the engineering modules because it has a
different nature: it is not a code change, it has legal consequences, and it
is on a clock that engineering is not.

Two facts make it urgent:

1. **The paper's abstract asserts 98.0% top-1 accuracy.** That number is
   circular. It appears in the abstract, the results table, the analysis, and
   the conclusion. A reviewer who notices the oracle is the system under test
   will not evaluate the rest of the paper.

2. **The patent claims may be anticipated by the literature.** The research
   dossier records that information-gain-based triage selection is prior art,
   and that a 2026 JAMIA paper on the orchestrator–specialist pattern is
   directly relevant. A provisional filing locks a priority date; **new matter
   generally cannot be added later to benefit from that date.** If the claims
   are to be re-scoped to the defensible contract — deterministic bounded
   bank, conformal-before-agreement, safety band — that re-scoping should
   happen *before* filing, not after.

## In scope

- `paper/phase3-paper/main.tex` — the claims, results, and framing.
- `paper/phase3-paper/main_humanized.tex` — the parallel draft.
- `paper/SUBMISSION_CHECKLIST.md` and `SUBMISSION_CHECKLIST.md` — status
  accuracy.
- `patent/specification/provisional_patent_specification.md` — the claims and
  their alignment with the code.
- `patent/PATENT_AGENT_BRIEF.md`, `patent/PATENT_PORTFOLIO_SUMMARY.md` — the
  brief given to counsel.
- `docs/research/public_release/11_patent_prior_art.md` — the prior-art
  evidence this module relies on.
- Repository README and docs that make performance claims.

## Out of scope

- Writing the paper. This module corrects and re-scopes claims; it does not
  author new prose beyond what correctness requires.
- The prior-art search itself — that is `w3-patent`, and it is a
  professional search by counsel.
- Producing the replacement accuracy numbers — `w1-external-eval`.
- Blinding the manuscript for submission — that is a later, separate artifact
  after the numbers land.

## Two phases

| Phase | Depends on | Work | When |
|---|---|---|---|
| **A — Retract and re-scope** | `w0-benchmark-honesty` | Remove the circular accuracy claim; re-scope the patent claims to the defensible contract; correct repo docs | Now — before filing |
| **B — Replace with honest numbers** | `w1-external-eval`, `w1-conformal` | Insert externally measured results with CIs; update the patent's quantitative examples | After Wave 1 |

Phase A must complete before the provisional filing. Phase B must complete
before any public presentation or conference submission.

## Current state (verified)

**In `paper/phase3-paper/main.tex`:**

| Line | Claim |
|---|---|
| `:41` (abstract) | 98.0% top-1, 93.0% baseline, +5.0%, p = 0.0339, 100.0% top-3, 53.7% entropy reduction, ECE −55.7%, Brier −62.1% |
| `:69` | "+5.0% gain in Top-1 accuracy (p = 0.0339)" over 200 standardized cases |
| `:228` | Results table: Top-1 98.0% (196/200) vs 93.0% (186/200); Top-3 100.0% |
| `:234` | ECE 0.2451 vs 0.5528 |
| `:250` | "+5.0% in Top-1 accuracy (p = 0.0339, McNemar's test with Edwards continuity correction)" |
| `:253` | Brier 0.5296 → 0.2005; ECE 0.5528 → 0.2451; "This proves that active mutual information questioning sharpens true probabilities" |
| `:261` | Figure: category-specific top-1 breakdown, N = 200 |
| `:282-283` | Per-category claims: cardiovascular 42.9% → 100.0% (+57.1%); pneumonia 57.1% → 100.0% (+42.9%) |
| `:300` | Conclusion: "98.0% Top-1 diagnostic accuracy, 100.0% Top-3 coverage, and a 53.7% reduction in Shannon entropy in under 2 questions" |

**Two additional problems visible in the same file:**

- `:41` claims an "Ontological Knowledge Graph Pruning Gate" that "traverses
  UMLS Metathesaurus and SNOMED-CT directed acyclic graphs." The research
  dossier records that **no open-source self-built symptom-condition
  knowledge graph with red-flag criteria exists** — the system uses a
  hand-written 15-condition dictionary with ICD-10 strings. This is a
  description of work that does not exist in the code.
- `:41` claims "Multimodal Conformal Risk-Controlled Synthesis, generating
  dynamically sized prediction sets with provable 1 − α distribution-free
  coverage guarantees." The code has no conformal implementation —
  `src/agents/confidence_scorer.py` is an availability/agreement blend with
  measured ECE 0.245.

**In the patent:** `patent/specification/provisional_patent_specification.md`
and `patent/PATENT_AGENT_BRIEF.md` carry claims of entropy-based triage and
multi-agent diagnosis broadly — which the research identifies as prior art.

**Related status documents:** `SUBMISSION_CHECKLIST.md:30` states "The Phase
3 research benchmark, patent portfolio, and conference paper draft are
packaged and verified." That is accurate as a statement about artifacts
existing, but reads as a statement about validity, which is the problem this
module addresses.

## Requirements

**R1 — The circular accuracy claim is removed from the paper.** No form of
"98% top-1 accuracy on 200 cases" survives in the abstract, results,
analysis, or conclusion.

**R2 — The comparison against the single-pass baseline is removed or
re-framed.** The +5.0% / p = 0.0339 result compares DEMAT against a baseline
on the same circular cases. The McNemar test is a valid test of that
comparison; it is simply a comparison whose subject is not clinical accuracy.

**R3 — The mechanism is preserved.** The entropy reduction, information-gain
question selection, and the 1.92-inquiry average are *mechanism* properties,
not accuracy claims. They may be retained if they are (a) re-framed as
properties of the triage mechanism on self-generated cases, and (b) clearly
labeled as such. Discarding the mechanism would throw away the strongest
part of the contribution.

**R4 — Claims describing unimplemented systems are removed.** The UMLS/SNOMED
knowledge-graph pruning gate and the conformal risk-controlled synthesis
claims must either be backed by working code or be reframed as *proposed
extensions*. Given that `w1-conformal` and `w1-kb-v2` will implement
conformal prediction and coded knowledge, the recommendation is to reframe
phase A as "proposed" and update in phase B when the code exists.

**R5 — The paper's contribution is restated around what it genuinely is.**
The defensible contribution is: **an entropy-driven triage core whose purpose
is to ask, in a domain where commercial symptom checkers ask only 36.9% of
red-flag questions, with under-triage as the field's characteristic failure.**
That is a mechanism contribution, it is supported by the code, and it is
exactly the contribution the research's strategy paragraph identifies.

**R6 — The patent claims are re-scoped to the defensible contract.** The
target claim set is: deterministic bounded-bank triage + conformal applied
before agreement blending + a safety band the LLM cannot widen. This is
narrower than the current claims and is what the research identifies as
novel.

**R7 — The provisional filing happens after re-scoping.** The filing
checklist's `D0` anchor is TBD; the re-scope must be complete before `D0` is
set. Recommendation: complete phase A, then file.

**R8 — Prior art is proactively addressed.** The JAMIA 2026 paper must be
identified and cited to the examiner rather than discovered by them. The
patent brief must include the specific anticipatory references.

**R9 — Every quantitative claim carries its provenance.** Each number in the
paper states the dataset, the baseline, and the uncertainty. If the number is
not externally measured, it is labeled as such.

**R10 — Repository documentation states the same thing as the paper.** A
reader who reads the README must not come away with a different impression
than a reader of the paper.

## Acceptance criteria

- [ ] The grep guard from `w0-benchmark-honesty` returns zero unlabeled hits
      across the paper.
- [ ] No sentence in the paper claims clinical accuracy from self-generated
      cases.
- [ ] Every claim about a system component corresponds to code that exists,
      or is explicitly labeled as a proposed extension.
- [ ] The paper's contribution statement is consistent with the research's
      strategy paragraph and with the code.
- [ ] The patent specification contains no claim broader than the re-scoped
      contract, and the brief cites the anticipatory references.
- [ ] `SUBMISSION_CHECKLIST.md` states the accuracy situation accurately.
- [ ] The README's performance statements match the paper's.
- [ ] The principal investigator has signed off on the re-scoped claim set
      before filing.

## Files in scope

| File | Change |
|---|---|
| `paper/phase3-paper/main.tex` | Retract; re-scope; reframe; update status |
| `paper/phase3-paper/main_humanized.tex` | Parallel changes |
| `paper/SUBMISSION_CHECKLIST.md` | Accurate status |
| `SUBMISSION_CHECKLIST.md` | Accurate status |
| `patent/specification/provisional_patent_specification.md` | Re-scoped claims |
| `patent/PATENT_AGENT_BRIEF.md` | Anticipatory references |
| `patent/PATENT_PORTFOLIO_SUMMARY.md` | Claim-to-code mapping updated |
| `README.md` | Performance statements |
| `docs/research/public_release/11_patent_prior_art.md` | Cite it; do not edit it |

## Design notes

**Why phase A precedes filing rather than following it.** A provisional
filing establishes a priority date for what is *disclosed at that time*. New
matter added afterwards generally cannot claim that date. The current claims
cover entropy-based information-gain triage — which the research says is
prior art. Filing them first would secure a priority date on claims that may
not be patentable, and would not secure one on the claims that are. The
re-scope is a few days of work. The cost of getting it wrong is the patent.

**Why the paper should keep the mechanism.** The strongest available
contribution is not "we achieved high accuracy" — that number cannot be
defended. It is "we built a triage engine whose whole purpose is to ask the
right question, and here is the evidence that asking is the scarce skill in
this field." The research supplies the field benchmark (36.9% ask-coverage;
34–62% top-1 for commercial checkers) that makes this claim meaningful.

**Why "proposed extension" is an honest label.** `main.tex:41` describes a
knowledge-graph pruning gate and conformal synthesis that do not exist in the
code. Rather than deleting the vision — it is a good one and Wave 1 will
implement conformal prediction — label it as a proposed extension and update
it when the code lands. A clearly labeled proposal is publishable; an
unimplemented claim presented as implemented is not.

**On the 200-case figures in the appendix.** The per-category breakdowns at
`:282-283` (cardiovascular 42.9% → 100.0%, pneumonia 57.1% → 100.0%) are
computed on the same circular cases. They are the most visually striking
numbers in the paper and the least defensible. Expect them to draw the
sharpest reviewer attention.

## Boundaries

- **Always:** get the principal investigator's sign-off before changing
  claims; keep the citation trail to the research dossiers; preserve the
  mechanism contribution; label every proposal as a proposal.
- **Ask first:** any change to the patent specification (counsel reviews
  every edit); any change to the paper's title or abstract framing; setting
  the `D0` filing date.
- **Never:** submit, upload, or publicly present the manuscript before the
  provisional filing exists; leave an unimplemented system described as
  implemented; delete the mechanism contribution along with the accuracy
  claim; cite a prior-art paper the project has not actually read.

## Success criteria

The paper, the patent, and the repository docs describe a system that exists
and make no accuracy claim that the system's own data cannot support. The
patent's claims cover the narrow, defensible contract.

## Open questions

1. **Does the paper's venue change?** A mechanism contribution with
   externally measured numbers is a different paper from an accuracy
   contribution on synthetic cases. CHIL remains plausible — the mechanism
   and the safety evaluation fit. MICCAI may fit better if the conformal and
   KB work is emphasized. Recommendation: keep CHIL as the target and let the
   external evaluation decide.
2. **Who re-scopes the patent claims?** This needs someone who understands
   both the code and the claim language. The `patent/` directory has a
   complete filing package, and `patent/PATENT_AGENT_BRIEF.md` is written for
   a patent agent — the recommendation is to prepare a re-scoped brief and
   have the patent agent execute the change, since the claim set has legal
   consequences.
3. **Does the humanized draft need the same treatment?** `main_humanized.tex`
   is a parallel draft with the same numbers. Both must be corrected, or the
   wrong one will be submitted.
4. **Can the 53.7% entropy-reduction result be re-measured externally?** It
   is a mechanism property and may hold up on external vignettes, which would
   let the paper keep it as a headline. This is a `w1-external-eval` question
   worth asking early, because it changes what phase B has to produce.
