# Spec: AegisMed Improvement Phase

**Status:** active · **Module ids:** [`CAPABILITY_MAP.md`](.planning/2026-10-28-aegismed-improvement-phase/CAPABILITY_MAP.md) · **Module specs:** [`.planning/2026-10-28-aegismed-improvement-phase/specs/`](.planning/2026-10-28-aegismed-improvement-phase/specs/)

This is the **root entry point** for spec-driven development on this project.
The module-level source of truth lives in
`.planning/2026-10-28-aegismed-improvement-phase/` (capability map, 17 module
specs, traceability). This document consolidates the initiative-wide contract —
objective, commands, structure, style, testing, boundaries — and defines
`/build` and `/test` as the canonical verification commands. When this file and
a module spec disagree, the module spec wins for module-scoped concerns; this
file wins for initiative-wide concerns.

Evidence base (frozen, citation source for every claim):
[`docs/research/public_release/`](docs/research/public_release/).

---

## 1. Objective

AegisMed is a multi-agent symptom-assessment system whose published headline
number (98% top-1) is circular — benchmark cases are generated from the same
`DISEASE_DATABASE` likelihoods the system is scored against. It cannot
comprehend negation, fabricates demo diagnoses on API failure, and matches red
flags with 12 keyword strings. This phase builds the system the research says
it should be:

1. **Nothing it says can be silently wrong** — negation handled, red flags
   structured, fabricated output paths gone, the circular benchmark retired as
   an accuracy claim.
2. **Every published number is external** — held-out real vignettes with
   bootstrap CIs; uncertainty as calibrated conformal sets, not percentages.
3. **Every claim is traceable** — paper, patent, and docs say what the code
   can defend.
4. **Every statement is lawful** — DPDP consent, CDSCO-appropriate positioning,
   ABDM-compatible data plumbing.

The deterministic triage core (DEMAT) stays the decision authority; the LLM
layer is conversation and language only, and may tighten language but never
widen a triage band.

## 2. Commands

All commands run from the repository root. Always use `venv/bin/python`
(3.12) — system `python3` is 3.13. Do not use `npx next start` (hangs silently).

### `/build` — full verification build (canonical)

Runs everything that must pass before any PR can merge. Fails fast, in order:

```bash
# 1. Backend compiles and imports cleanly
venv/bin/python -m compileall -q src config scripts \
  && venv/bin/python -c "import src.api.main"

# 2. Frontend typecheck
cd frontend && ./node_modules/.bin/tsc --noEmit -p tsconfig.json

# 3. Frontend production build
NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-/api/backend} ./node_modules/.bin/next build
```

Lint is a separate command, not a `/build` gate: `venv/bin/python -m ruff
check src/ tests/ config/` currently reports 67 pre-existing findings
(55 auto-fixable). Clearing that debt is a `ci-foundation` deliverable — until
then ruff is advisory and `/build` does not gate on it. New code must not add
findings.

### `/test` — full test suite (canonical)

```bash
# 1. Backend suite (~12 min full; use -k during development)
venv/bin/python -m pytest tests/ -q --tb=short

# 2. Frontend suite (Vitest — lands with w0-truthful-frontend)
cd frontend && npm test
```

Raw commands for everything else:

```bash
venv/bin/python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000   # backend run
curl -fsS http://localhost:8000/health                                    # health check
cd frontend && ./node_modules/.bin/next start                             # frontend serve
venv/bin/python -m black src/ tests/ config/                              # format
venv/bin/python -m pytest tests/ -q -k "negation"                         # tests by keyword
venv/bin/python scripts/benchmark/external_eval.py --dataset dxbench      # external eval (w1)
```

## 3. Project Structure

```
src/
├── agents/                     # BaseAgent ABC; nlp/, rag/, synthesis/, orchestrator/ are module scopes
├── core/                       # demat.py, disease_kb.py (w1-kb-v2), question_bank.py, red_flags.py (NEW w0)
├── data/preprocessing/         # text_preprocessor.py (w0-assertion-nlp)
├── api/                        # main.py, routes/ (diagnosis.py split deferred to w3-engineering)
├── llm/                        # openrouter_client.py, gemini_client.py
└── utils/redaction.py          # PHI redaction — do not regress

frontend/src/
├── lib/api.ts                  # API client (w0-truthful-frontend scope)
├── app/                        # Next.js App Router pages
└── components/diagnosis/       # results, stepper, error states

tests/                          # unit/, integration/, safety/ (NEW — adversarial)
frontend/src/**/*.test.ts(x)    # Vitest co-located tests (NEW)
scripts/benchmark/              # demat_benchmark.py (circular — regression only), external_eval.py (w1)
docs/research/public_release/   # frozen research evidence base
.planning/2026-10-28-aegismed-improvement-phase/   # capability map + 17 module specs
```

## 4. Code Style

Match the surrounding code: docstrings on public functions, type hints on
public signatures, loguru `logger` (never `print`) in backend modules,
`self.log(...)` inside `BaseAgent` subclasses.

```python
def _extract_symptoms(self, text: str) -> list[dict]:
    """Extract symptoms using pattern matching or BioBERT."""
    found = []
    for category, pattern in self.SYMPTOM_PATTERNS.items():
        for match in re.findall(pattern, text):
            found.append({"symptom": match, "category": category})
    ...
```

```tsx
export function SeverityBadge({ severity }: { severity: keyof typeof severityConfig }) {
  const config = severityConfig[severity];
  return (
    <span className={cn("inline-flex items-center gap-1.5 ...")}>
      <config.icon size={12} />
      {config.label}
    </span>
  );
}
```

Conventions: module constants `UPPER_SNAKE_CASE`; Google-style docstrings
(`Args:`/`Returns:`); frontend uses named exports, `interface` for shapes,
`cn()` from `@/lib/utils`, Tailwind utilities, no inline `style` except
computed chart colors; comments explain *why*, never narrate *what*.

## 5. Testing Strategy

| Level | Location | Runner |
|---|---|---|
| Unit | `tests/unit/` | pytest |
| Golden (negation/lay-language, 200 cases) | `tests/unit/test_assertion_golden.py` | pytest |
| Adversarial safety | `tests/safety/` | pytest |
| Integration | `tests/integration/` | pytest |
| External evaluation (bootstrap CIs) | `scripts/benchmark/external_eval.py` | script |
| Frontend unit | `frontend/src/**/*.test.ts(x)` | Vitest |
| Contract | `tests/unit/test_api_contract.py` | pytest |

Rules that override convenience:

- Every module adds a test that **fails before** the change and passes after.
- The golden harness (≥95% on 200 negation/lay-language cases, live probe case
  flips) is release-blocking for `w0-assertion-nlp`; the adversarial suite
  (100% emergency-flagging, out-of-scope refusal) for `w0-red-flag-engine`.
- **No test may assert on a number from the circular benchmark** as an accuracy
  result; such regression guards must be named `test_demat_smoke_regression_*`.
- Full detail: [`TEST_PLAN.md`](.planning/2026-10-28-aegismed-improvement-phase/TEST_PLAN.md).

## 6. Boundaries

**Always**

- Run `/test` (or the module's named subset) before every commit.
- Keep patient text out of logs — use `src/utils/redaction.py`.
- Cite a research dossier for every performance or regulatory claim.
- Add a test that fails before your change; update
  `PROGRESS_TRACKER.md`/`progress.md` in the same commit.

**Ask first**

- Changing `DISEASE_DATABASE` condition keys or question-bank likelihoods.
- Adding any dependency (Python or npm).
- Editing `paper/` or `patent/` — legal consequences.
- Changing `config/settings.py` defaults (especially `enforce_api_key`) or the
  `doctor_alert` contract.
- Deleting/rewriting `data/benchmarks/results/` (historical record).

**Never**

- Never fabricate, estimate, or infer a citation.
- Never let an LLM output widen the triage band, severity, or red-flag set.
- Never reintroduce a fallback that returns plausible-looking clinical content
  on backend failure.
- Never log patient symptom text, even at debug level.
- Never report a self-generated benchmark number as an accuracy result.
- Never publish the CHIL manuscript before the provisional filing date `D0`.
- Never remove a failing test without replacing it with one asserting the
  correct behavior.

## 7. Module index

Full table with dependencies, waves, gaps, and build order:
[`CAPABILITY_MAP.md`](.planning/2026-10-28-aegismed-improvement-phase/CAPABILITY_MAP.md).

| Wave | Modules |
|---|---|
| 0 — stop the bleeding | `w0-truthful-frontend`, `w0-assertion-nlp`, `w0-red-flag-engine`, `w0-benchmark-honesty`, `ci-foundation` (pulled forward from `w3-engineering`), `publication-truth` phase A |
| 1 — measure honestly | `w1-external-eval`, `w1-conformal`, `w1-kb-v2`, `publication-truth` phase B |
| 2 — become advanced | `w2-hybrid-rag`, `w2-schema-synthesis`, `w2-orchestration`, `w2-ask-coverage` |
| 3 — lawful & durable | `w3-engineering`, `w3-dpdp`, `w3-regulatory`, `w3-abdm`, `w3-patent` |

## 8. Success criteria & open questions

Initiative-wide gates and the 17 open questions live in
[`SPEC-master.md`](.planning/2026-10-28-aegismed-improvement-phase/SPEC-master.md)
(§Success Criteria, §Open Questions). Wave gates are satisfied by **linked
evidence** in `PROGRESS_TRACKER.md`, not by checked boxes.
