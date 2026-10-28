# AegisMed Improvement Phase — Document Set

**Created:** 2026-10-28 · **Status:** PLANNING COMPLETE — awaiting execution
**Branch:** `docs/improvement-phase-plan` (stacked on `docs/public-release-research`)
**Research basis:** `docs/research/public_release/` (commit `9be85dd`, 11 dossiers)

This directory is the single source of truth for what the improvement phase
builds, in what order, and how progress is tracked. It is written **before**
implementation so that every change has a spec, an acceptance criterion, and a
traceable origin in the research evidence.

## What this phase is

The research program (2026-10-27) produced an evidence base and a sequenced
roadmap. This phase **executes** that roadmap: it turns a system that
overstates its own performance into one whose every number can be defended,
whose every output is traceable, and whose failure modes are handled
explicitly rather than papered over.

The headline fact driving everything below: the system's 98% top-1 accuracy is
**circular** — the benchmark cases are generated from the same
`DISEASE_DATABASE` likelihoods the system is scored against. No other number
in the repository is as load-bearing, and it is currently published in the
paper's abstract.

## Documents

| Document | Purpose | Read it when |
|---|---|---|
| [`CAPABILITY_MAP.md`](CAPABILITY_MAP.md) | Module ids, dependency direction, build order | Before picking up any work |
| [`SPEC-master.md`](SPEC-master.md) | Initiative-wide objective, commands, style, testing, boundaries | Once, then refer to |
| [`TRACEABILITY.md`](TRACEABILITY.md) | Every research gap → module → task → test → status | To check nothing was dropped |
| [`tasks/plan.md`](tasks/plan.md) | Technical implementation plan, sequencing, parallel tracks | Before scheduling work |
| [`tasks/todo.md`](tasks/todo.md) | Discrete tasks with acceptance criteria and verification | While executing |
| [`TEST_PLAN.md`](TEST_PLAN.md) | Golden harness, adversarial suite, external protocol, CI gates | Before writing a test |
| [`RISK_REGISTER.md`](RISK_REGISTER.md) | Live risks, triggers, mitigations, owners | Weekly review |
| [`PROGRESS_TRACKER.md`](PROGRESS_TRACKER.md) | The single status board | Every session |
| [`FUTURE_IMPROVEMENTS.md`](FUTURE_IMPROVEMENTS.md) | What this phase deliberately defers, and why it matters | When planning what follows |
| [`findings.md`](findings.md) | Code-verified baseline facts this plan rests on | To check a claim in a spec |
| [`progress.md`](progress.md) | Session-by-session execution log | After each work session |
| [`decisions/`](decisions/) | Architecture decision records | Before changing a locked decision |

### Module specs

| Spec | Module | Wave |
|---|---|---|
| [`specs/SPEC-w0-truthful-frontend.md`](specs/SPEC-w0-truthful-frontend.md) | `w0-truthful-frontend` | 0 |
| [`specs/SPEC-w0-assertion-nlp.md`](specs/SPEC-w0-assertion-nlp.md) | `w0-assertion-nlp` | 0 |
| [`specs/SPEC-w0-red-flag-engine.md`](specs/SPEC-w0-red-flag-engine.md) | `w0-red-flag-engine` | 0 |
| [`specs/SPEC-w0-benchmark-honesty.md`](specs/SPEC-w0-benchmark-honesty.md) | `w0-benchmark-honesty` | 0 |
| [`specs/SPEC-publication-truth.md`](specs/SPEC-publication-truth.md) | `publication-truth` | 0–1 |
| [`specs/SPEC-w1-external-eval.md`](specs/SPEC-w1-external-eval.md) | `w1-external-eval` | 1 |
| [`specs/SPEC-w1-conformal.md`](specs/SPEC-w1-conformal.md) | `w1-conformal` | 1 |
| [`specs/SPEC-w1-kb-v2.md`](specs/SPEC-w1-kb-v2.md) | `w1-kb-v2` | 1 |
| [`specs/SPEC-w2-hybrid-rag.md`](specs/SPEC-w2-hybrid-rag.md) | `w2-hybrid-rag` | 2 |
| [`specs/SPEC-w2-schema-synthesis.md`](specs/SPEC-w2-schema-synthesis.md) | `w2-schema-synthesis` | 2 |
| [`specs/SPEC-w2-orchestration.md`](specs/SPEC-w2-orchestration.md) | `w2-orchestration` | 2 |
| [`specs/SPEC-w2-ask-coverage.md`](specs/SPEC-w2-ask-coverage.md) | `w2-ask-coverage` | 2 |
| [`specs/SPEC-w3-dpdp.md`](specs/SPEC-w3-dpdp.md) | `w3-dpdp` | 3 |
| [`specs/SPEC-w3-regulatory.md`](specs/SPEC-w3-regulatory.md) | `w3-regulatory` | 3 |
| [`specs/SPEC-w3-abdm.md`](specs/SPEC-w3-abdm.md) | `w3-abdm` | 3 |
| [`specs/SPEC-w3-patent.md`](specs/SPEC-w3-patent.md) | `w3-patent` | 3 |
| [`specs/SPEC-w3-engineering.md`](specs/SPEC-w3-engineering.md) | `w3-engineering` | 3 |

## How to work in this directory

1. **Pick a module id** from `CAPABILITY_MAP.md`. Never start work whose module
   id is absent from that map — the map is the index of what exists.
2. **Read that module's spec.** It carries the objective, boundaries,
   acceptance criteria, and the specific files in scope.
3. **Claim a task** in `tasks/todo.md` and update `PROGRESS_TRACKER.md`.
4. **Verify with the command named in the task.** A task without a verification
   command is not done.
5. **Log what happened** in `progress.md`, including failures and reversals.
6. **Update `TRACEABILITY.md`** if a task changes a gap's status.

## Rules that bind this phase

- **No number enters a document without a source and a baseline.** If the
  source is not in `docs/research/public_release/`, it does not go in.
- **No self-referential measurement counts as evidence.** A benchmark whose
  oracle is the system under test is a regression test, not an evaluation.
- **No fabricated output path survives.** Not in the frontend, not in the
  backend, not in a fallback.
- **Patient text never reaches a log.** The P0 branch already fixed this;
  every module must preserve the fix.
- **The deterministic triage core owns the safety band.** An LLM may tighten
  language, never widen the band.

## Branch and merge sequence

```
master
  └── docs/public-release-research   (9be85dd — research; PR first)
        └── docs/improvement-phase-plan   (this branch — plan + execution)
              └── feature branches cut per module
```

This branch is **stacked** on `docs/public-release-research` so that every
relative path in these documents resolves while reading. After the research PR
merges to `master`, rebase this branch before opening its PR:

```bash
git rebase master
```

Feature branches for implementation are cut from this branch, one per module
id, and merged back into it.

## Baseline at time of writing

- Backend suite: **197 passed, 17 skipped** (724s), on `master` @ `76c079c`.
- Branch under test: `master` plus the research commit.
- No CI pipeline exists. No frontend test runner exists. See
  `specs/SPEC-w0-benchmark-honesty.md` and `specs/SPEC-w3-engineering.md`.
