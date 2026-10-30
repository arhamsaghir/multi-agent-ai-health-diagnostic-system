# Spec: `ci-foundation`

**Module id:** `ci-foundation` · **Wave:** 0 · **Owner:** platform
**Closes gap:** 15 (partial — the CI portion of `w3-engineering`, pulled
forward per the capability map's Wave-0 deviation) · **Depends on:** — ·
**Blocks:** every other module's PR
**Status:** implemented — PR pending on `feat/ci-foundation`

## Objective

**Every PR is gated by a machine.** The repo has zero CI: a broken main
branch is one merge away at all times. The roadmap called CI "a regression
fence" and scheduled it for Wave 3; the capability map's recorded deviation
pulls it into Wave 0 because a fence built in Wave 3 protects none of Waves
0–2 — every module in this phase lands as a PR, and the fence must be up
before the later modules lean on it.

**User story:** *As a contributor, a red CI run tells me my change broke
something before a human has to.*

## In scope

- `.github/workflows/ci.yml` — GitHub Actions, greenfield (no `.github/`
  directory exists today).
- Two jobs mirroring the root `SPEC.md` canonical commands: backend
  (`/build` compile step + pytest) and frontend (tsc + next build + vitest).

## Out of scope

- The `diagnosis.py` split, the local-LLM fallback benchmark, and the rest
  of `w3-engineering` — those stay in Wave 3.
- Deployments, artifact publishing, matrix builds.
- Making ruff a blocking gate — it is **advisory** (67 pre-existing
  findings recorded in root `SPEC.md`; the cleanup is owned by later
  engineering work, not silently enforced here).

## Requirements

**R1 — Backend job.** Python 3.12 (the venv version), pip-cached, install
`requirements.txt`, then: (a) the `/build` compile gate —
`python -m compileall` over `src`/`tests` plus an import of `src.api.main`;
(b) `pytest -q` — the full suite; (c) `ruff check` runs **advisory** with
`continue-on-error: true`, findings visible in the log.

**R2 — Frontend job.** Node 22 (matches the dev machine), npm-cached,
`npm ci`, then: `npx tsc --noEmit`, `npm run build`, and
`npm run test --if-present` — the `--if-present` keeps the workflow correct
on branches that predate the Vitest runner (PR #8 introduces it).

**R3 — Triggers.** On every pull request and every push to `master`.

**R4 — No external services required.** The suite passes without the
OmniRoute tunnel (LLM clients fail fast on connection-refused and fall
back); CI sets `USE_OMNIROUTE=false` explicitly so no step ever waits on
`localhost:20128`. No dataset downloads, no secrets needed for the green
path.

## Acceptance criteria

- [ ] `.github/workflows/ci.yml` exists and parses as valid YAML.
- [ ] Backend job runs compile gate + pytest (+ advisory ruff).
- [ ] Frontend job runs tsc + next build + vitest-if-present.
- [ ] Triggers cover pull_request and push to master.
- [ ] No step requires a secret, tunnel, or network service to pass.
- [ ] Job timeout bounded (30 min) so a hang fails visibly.

## Boundaries

- **Always:** mirror the root SPEC.md's `/build` and `/test` gates — one
  source of truth for what "green" means; keep ruff visible but advisory.
- **Ask first:** adding new tooling (linters beyond ruff, coverage
  thresholds, security scanners).
- **Never:** gate on a check that isn't part of the canonical commands;
  silently swallow failures with `continue-on-error` outside the advisory
  ruff step.

## Success criteria

A PR that breaks the backend suite, the frontend types, or the frontend
build shows red before merge; a clean PR shows green from machine checks
alone.
