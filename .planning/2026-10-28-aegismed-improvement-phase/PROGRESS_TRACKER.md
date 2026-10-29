# Progress Tracker — AegisMed Improvement Phase

The single status board. Every wave gate is satisfied by **linked evidence**,
not by checked boxes.

## Waves

| Wave | Goal | Gate | Status |
|---|---|---|---|
| 0 | Stop the bleeding | see [`CAPABILITY_MAP.md`](CAPABILITY_MAP.md) §Waves | 🟡 in progress — 1 of 4 blockers implemented |
| 1 | Measure honestly | — | ⚪ not started |
| 2 | Become advanced | — | ⚪ not started |
| 3 | Lawful & durable | — | ⚪ not started |

## Modules

| Module id | Status | Evidence |
|---|---|---|
| `w0-truthful-frontend` | 🟡 implemented — PR open | 26/26 Vitest green (`npm test`); `tsc --noEmit` clean; `next build` green; grep guards pass (no live path reaches `getDemoResults`; no console symptom text). Note: R4's `flags[:3]` truncation was located in `src/agents/rule_based_synthesis.py` (backend), fixed in the same PR. |
| `w0-assertion-nlp` | ⚪ not started | — |
| `w0-red-flag-engine` | ⚪ not started | — |
| `w0-benchmark-honesty` | ⚪ not started | — |
| `ci-foundation` | ⚪ not started | — |
| `publication-truth` | ⚪ not started | — |
| all `w1`–`w3` modules | ⚪ not started | — |

## Baseline

- Backend suite: **234 passed / 17 skipped** at `master` @ `23694c2` (post-PR #5).
- Frontend: no test runner existed before `w0-truthful-frontend`; Vitest 3 +
  RTL 16 + jsdom 24 added by that module (26 tests).
- No CI pipeline yet (`ci-foundation` pending).
