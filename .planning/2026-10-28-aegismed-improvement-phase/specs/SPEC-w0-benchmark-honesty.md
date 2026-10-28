# Spec: `w0-benchmark-honesty`

**Module id:** `w0-benchmark-honesty` · **Wave:** 0 · **Owner:** evaluation
**Closes gap:** 7 (partial) · **Depends on:** — · **Blocks:**
`publication-truth`, `w1-external-eval`
**Status:** not started

## Objective

**Stop calling a circular benchmark an accuracy result.**

AegisMed reports 98.0% top-1 accuracy on 200 cases. The research established
exactly how that number was produced, and the code confirms it: the benchmark
cases are generated from the same `DISEASE_DATABASE` likelihood tables the
system is scored against. The oracle is the system under test. A number
produced this way measures whether the code still does what it did when the
benchmark was generated — it cannot measure clinical accuracy at all.

This number is currently published in the paper's abstract, results table,
analysis, and conclusion. It is the project's most visible claim and its
least defensible.

This module's job is narrow and urgent: **retire the claim**, preserve the
harness as a regression test, and remove the circular number from every
document that repeats it. Building a proper external evaluation is
`w1-external-eval` and takes weeks; retracting the claim takes hours and
should not wait for it.

**User story:** *As a reader of this project's claims, every accuracy number
I see came from data the system did not generate.*

## In scope

- `scripts/benchmark/demat_benchmark.py` — reclassify as a regression
  harness; change the output so it cannot be read as an accuracy claim.
- `scripts/generate_benchmark_cases.py` — same.
- `scripts/run_benchmark.py` — same; note this script calls
  `_get_demo_result()`, a demo-matching function, which is a second circular
  path.
- `data/benchmarks/results/` — keep the historical results as a record of
  what was claimed; add a retraction notice. **Do not delete.**
- `data/benchmark_cases.json` — keep; add a provenance marker.
- Repository docs that repeat the 98% figure — `README.md`,
  `docs/test_report.md`, and any others found by grep.
- `tests/unit/test_demat_benchmark.py` — rename the tests so their intent is
  unambiguous.

## Out of scope

- Building the external evaluation harness — `w1-external-eval`.
- Editing the paper's claims — `publication-truth`.
- Deleting `data/benchmarks/results/` — it is the historical record.
- Changing the benchmark's numbers. The harness still computes what it
  computes; this module changes what it is *called*.

## Current state (verified)

**The circularity, in code.** `scripts/generate_benchmark_cases.py` builds
cases from `DISEASE_TEMPLATES` — hand-authored symptom templates per
category — and `scripts/benchmark/demat_benchmark.py` scores the system
against those cases. The research's finding is that
`simulate_patient_answer()` answers DEMAT's questions using the same
`DISEASE_DATABASE` likelihoods the system is scored against. The templates
and the likelihood tables are two views of one knowledge base.

**A second circular path.** `scripts/run_benchmark.py:113` calls
`_get_demo_result(case["symptom_text"], ...)` — a substring-matching demo
function — and scores *that* against the ground truth. This measures how well
a keyword rule matches a template, which is not a diagnosis benchmark at
all.

**The published numbers.** `paper/phase3-paper/main.tex` asserts 98.0% top-1
at `:41`, `:228`, `:250`, `:300`; +5.0% gain with p = 0.0339 at `:41`, `:69`,
`:250`; 100.0% top-3 coverage at `:41`, `:228`, `:250`, `:300`; ECE −55.7% at
`:41`, `:234`, `:253`; Brier −62.1% at `:41`, `:253`. ECE 0.2451 appears at
`:234`.

**The suite.** `tests/unit/test_demat_benchmark.py` — 127 lines, 7 tests,
currently named as accuracy tests.

**What the harness is genuinely good for.** It is a fast, deterministic
regression check on DEMAT's mechanics: that entropy decreases when it should,
that information gain ranks questions as expected, that the stopping rule
fires. Those are real properties. They are just not accuracy.

## Requirements

**R1 — The harness is renamed and re-documented as a regression harness.**
Its module docstring, its CLI output, and its generated summary must state
that it measures internal consistency on self-generated cases and is **not**
an accuracy evaluation.

**R2 — The output cannot be mistaken for an accuracy claim.** The benchmark
must print a banner, and write a banner into its summary file:

```
SELF-GENERATED REGRESSION HARNESS — NOT AN ACCURACY EVALUATION
Cases are generated from the same knowledge base the system is scored against.
These numbers describe internal consistency only. Do not cite them as
accuracy. For external evaluation see scripts/benchmark/external_eval.py.
```

**R3 — Historical results are preserved, not deleted.** `data/benchmarks/`
keeps every existing file. A `RETIREMENT.md` is added alongside explaining
what the numbers were, why they are not accuracy, and when they were
generated.

**R4 — The dataset carries its provenance.** `data/benchmark_cases.json`
gains a `provenance` block declaring it self-generated and unsuitable for
accuracy claims. Any consumer can read it.

**R5 — Test names state intent.** Tests are renamed from accuracy framing to
regression framing, e.g. `test_top1_accuracy` → `test_smoke_top1_recall_on
_self_generated_cases`, with a docstring saying why.

**R6 — Repository docs no longer present circular numbers as accuracy.** Any
document that states the 98% figure as an accuracy result is corrected. If a
document should keep the historical value for context, it must be labeled as
the retired self-referential measurement.

**R7 — The circular number is greppable.** A single search command finds
every remaining occurrence, and that command is recorded in this spec so it
can be re-run before every release.

**R8 — A guard prevents regression.** A test asserts that no file in the
repository contains the retired claim in an accuracy context — a check over
the paper's `.tex`, the README, and `docs/`. This is the test that keeps the
retraction from quietly un-retracting itself.

## The grep guard

```bash
grep -rnE "98(\.0)?\s*%|196/200|Top-1 diagnostic accuracy" \
  --include="*.md" --include="*.tex" --include="*.py" \
  . | grep -v node_modules | grep -v "RETIREMENT.md" \
  | grep -v "2026-10-28-aegismed-improvement-phase"
```

Run before every commit in this phase. Any hit must be either a labeled
historical reference or a violation.

## Acceptance criteria

- [ ] `scripts/benchmark/demat_benchmark.py` prints the regression banner on
      every run.
- [ ] The generated summary file contains the banner.
- [ ] `data/benchmarks/RETIREMENT.md` exists and explains the retraction.
- [ ] `data/benchmark_cases.json` carries a provenance block.
- [ ] Every test in `tests/unit/test_demat_benchmark.py` is renamed to
      regression framing with an explanatory docstring.
- [ ] The grep guard returns zero unlabeled hits outside this planning
      directory and the retirement notice.
- [ ] `README.md` and `docs/test_report.md` no longer state the 98% figure as
      an accuracy result.
- [ ] A test asserts the grep guard condition, so a future doc that
      reintroduces the claim fails the suite.
- [ ] `scripts/run_benchmark.py` is labeled as a demo-matching smoke script,
      not a benchmark.
- [ ] The full backend suite is green with no previously-passing test removed.

## Files in scope

| File | Change |
|---|---|
| `scripts/benchmark/demat_benchmark.py` | Banner; docstring; output labeling |
| `scripts/generate_benchmark_cases.py` | Provenance in generated cases |
| `scripts/run_benchmark.py` | Relabel as a demo-matching smoke script |
| `data/benchmark_cases.json` | Provenance block |
| `data/benchmarks/RETIREMENT.md` | **NEW** — what was claimed and why it is retired |
| `tests/unit/test_demat_benchmark.py` | Rename to regression framing |
| `tests/unit/test_retired_claims_guard.py` | **NEW** — the grep guard as a test |
| `README.md` | Correct any accuracy claim |
| `docs/test_report.md` | Correct any accuracy claim |

## Design notes

**Why keep the harness at all.** It is fast, deterministic, and catches
regressions in DEMAT's mechanics that no external benchmark would catch
quickly. Deleting it would remove a useful tool and a real regression fence.
The problem is not the harness; it is the label on it.

**Why not delete the historical results.** Deleting them would erase the
record of what the project claimed and when — which is exactly the evidence
needed to understand the retraction. The results stay; the framing changes.

**What the harness legitimately measures.** Entropy reduction, information-gain
ranking order, stopping-rule behavior, and determinism across runs. Those
should become the *named* assertions in the renamed tests. That makes the
harness's value explicit rather than implied.

**Where the replacement numbers come from.** `w1-external-eval` measures
against DxBench (1,148 real doctor–patient dialogue cases, 461 diseases) and
gretelai/symptom_to_diagnosis (Apache 2.0, 212 test cases) with bootstrap
confidence intervals. Until that lands, **the project has no defensible
accuracy number** — and that is a legitimate state to be in.

## Boundaries

- **Always:** preserve the historical results; keep the harness runnable;
  make the banner unmissable; label every self-generated measurement.
- **Ask first:** deleting any file under `data/benchmarks/`; changing the
  benchmark's computation; editing `README.md`'s headline positioning (which
  overlaps `publication-truth`).
- **Never:** present a self-generated number as an accuracy result; remove the
  banner to "clean up" output; silently delete a result file.

## Success criteria

No document, test name, script output, or result file in the repository
presents the 98% figure as an accuracy result. The harness still runs and
still catches regressions, and its output says plainly what it is.

## Open questions

1. **Should the retired numbers stay in the paper's history section?** The
   honest options are (a) remove them entirely and describe the methodology
   problem in a limitations note, or (b) keep them with an explicit
   "self-generated, not an accuracy estimate" label. Recommendation: (b) —
   it demonstrates the correction rather than hiding it, and CHIL reviewers
   reward that.
2. **Does the retirement notice belong in `data/benchmarks/` or in
   `docs/`?** Recommendation: `data/benchmarks/RETIREMENT.md`, adjacent to
   the files it describes, so anyone who finds the numbers finds the context.
3. **Should the old `frontend_old/` Streamlit prototype's numbers be
   corrected too?** It is legacy and not part of the release surface.
   Recommendation: correct the number where it appears, do not otherwise
   touch the directory.
