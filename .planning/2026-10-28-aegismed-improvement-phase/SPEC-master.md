# Spec: AegisMed Improvement Phase (Master)

**Module ids:** see [`CAPABILITY_MAP.md`](CAPABILITY_MAP.md) — this document
covers the initiative; each module has its own spec in `specs/`.
**Status:** proposed — awaiting review
**Date:** 2026-10-28

## Objective

AegisMed is a multi-agent symptom-assessment system whose published headline
number — 98% top-1 accuracy — is **circular**: the benchmark cases are
generated from the same `DISEASE_DATABASE` likelihoods the system is scored
against, so the oracle is the system under test. The system also cannot
comprehend negation ("no fever, no cough" extracts fever and cough as
present), fabricates demo diagnoses on API failure, and matches red flags
with 12 keyword strings.

This phase builds the system the research says the project should be:

1. **Nothing it says can be silently wrong.** Negation is handled, red flags
   are structured, fabricated output paths are gone, and the circular benchmark
   stops being cited as an accuracy claim.
2. **Every number it publishes is external.** Performance is measured against
   held-out real vignettes with bootstrap confidence intervals, and uncertainty
   is expressed as a calibrated conformal set rather than a percentage.
3. **Every claim it makes is traceable.** The paper, the patent, and the docs
   say what the code can defend.
4. **Every statement it makes is lawful.** DPDP consent, CDSCO-appropriate
   positioning, and ABDM-compatible data plumbing.

**User stories this serves:**

- *As a patient, I am never shown a diagnosis that the backend did not
  produce, because a fabricated one could send me to the wrong care.*
- *As a patient, I am escalated when my symptoms warrant it, even when I
  phrase them negatively ("no chest pain" must not hide chest pain risk).*
- *As a reader, every performance number I see came from data the system did
  not generate.*
- *As a regulator, the product's language and data handling match its claimed
  class and its jurisdiction's law.*
- *As the inventor, the patent claims describe something not already in the
  public literature.*

## Assumptions

These are stated up front because a spec's purpose is to surface
misunderstandings before code is written. **Correct them before proceeding if
any is wrong.**

1. **Scope is the existing stack.** FastAPI + Next.js 16 + SQLite + FHIR R4.
   Wave 3 migrates the data layer to Postgres, but nothing else is rewritten.
2. **The deterministic triage core stays authoritative.** DEMAT's entropy-driven
   question selection is the system's real asset and the claimed novelty. The
   LLM layer remains a conversation and language layer, never the decision
   authority.
3. **No real-patient evaluation in this phase.** All evaluation data in this
   phase is credential-free public data (DxBench, gretelai, HealthBench) plus
   locally authored golden and adversarial sets. IRB-gated prospective
   evaluation is explicitly deferred — see `FUTURE_IMPROVEMENTS.md`.
4. **The paper is a living artifact, not a frozen submission.** `main.tex` will
   be edited. The blinded submission copy is a separate, later artifact.
5. **Product language changes from "diagnosis" to "assessment/triage."** This
   is a positioning requirement, not optional. Telemedicine clause 2.8 and CDSCO
   classification both depend on it.
6. **No new heavyweight dependency without a written justification.** BM25 and
   conformal prediction are the two candidates; both have a standard-library or
   minimal-dependency path that should be preferred.
7. **The frontend gains a test runner.** Vitest + React Testing Library is the
   default assumption; see open question 3.
8. **CI is GitHub Actions.** The repo has no workflow directory today.
9. **The research evidence base is frozen.** Dossiers in
   `docs/research/public_release/` are the citation source for this phase. If a
   new claim needs a source, it gets added to the research set first, not
   asserted inline.
10. **The P0 branch merges first.** `fix/p0-truth-alignment-and-phi-hygiene`
    (`d32e61a`) carries the PHI-hygiene fix and truth-alignment work. It must
    merge to `master` before any module branch is cut, or every module branch
    inherits the conflict in `api.ts` and `nlp/agent.py`.

## Tech Stack

**Backend (unchanged):**

| Component | Version | Notes |
|---|---|---|
| Python | 3.12 (venv) | System `python3` is 3.13.9 — always use `venv/bin/python` |
| FastAPI | 0.115.6 | `src/api/main.py` app entry |
| Pydantic | 2.10.4 | Request/response models |
| pydantic-settings | 2.7.1 | `config/settings.py` |
| NumPy | 2.2.6 | Conformal quantiles, metrics |
| SciPy | 1.15.3 | Bootstrap confidence intervals |
| scikit-learn | 1.7.2 | ECE, Brier, calibration diagnostics |
| faiss-cpu | 1.9.0 | Dense retrieval leg |
| transformers | 4.47.1 | Optional BioBERT path (off by default) |
| sentence-transformers | 3.3.1 | Embeddings |
| LangGraph | — | Orchestration graph |
| loguru | — | Structured logging (PHI-redacted) |
| pytest | — | `asyncio_mode = auto`, `testpaths = tests` |

**Frontend (unchanged):**

| Component | Version |
|---|---|
| Next.js | 16 (App Router) |
| React | 19 |
| TypeScript | — |
| Tailwind CSS | v4 |
| framer-motion | — |
| lucide-react | — |
| recharts | — |

**New in this phase:** Vitest, React Testing Library, jsdom (frontend tests);
GitHub Actions (CI); `rank_bm25` or a hand-rolled BM25 (hybrid retrieval).

## Commands

All commands run from the repository root. Always use `venv/bin/python` — the
system `python3` is 3.13.9 and the venv is 3.12.13.

```bash
# Environment
python3 -m venv venv && venv/bin/pip install -r requirements.txt
cp .env.example .env

# Backend — run
venv/bin/python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
# health check
curl -fsS http://localhost:8000/health

# Backend — test
venv/bin/python -m pytest tests/ -v --tb=short          # full suite (~12 min)
venv/bin/python -m pytest tests/unit/test_nlp_agent.py -v  # single file
venv/bin/python -m pytest tests/ -q --tb=short -k "negation"  # by keyword

# Backend — lint and format (as configured in Makefile)
venv/bin/python -m ruff check src/ tests/ config/
venv/bin/python -m black src/ tests/ config/
venv/bin/python -m ruff check --fix src/ tests/ config/

# Frontend — run and build
cd frontend && npm run dev        # :3000
cd frontend && npm run build
cd frontend && npm run lint
cd frontend && npm test           # NEW — Vitest (see w3-engineering)

# Frontend — start (do NOT use `npx next start`; it hangs silently)
frontend/node_modules/.bin/next start

# Benchmark — existing (circular; regression use only after w0-benchmark-honesty)
venv/bin/python scripts/benchmark/demat_benchmark.py

# Benchmark — external (NEW; after w1-external-eval)
venv/bin/python scripts/benchmark/external_eval.py --dataset dxbench --bootstrap 2000
```

**Timing note:** the full backend suite takes ~12 minutes. Run single files
during development and the full suite before every commit.

## Project Structure

```
src/
├── agents/
│   ├── base.py               # BaseAgent ABC — run(input_data) -> dict
│   ├── nlp/agent.py          # w0-assertion-nlp scope
│   ├── rag/agent.py          # w2-hybrid-rag scope
│   ├── synthesis/agent.py    # w2-schema-synthesis scope
│   ├── orchestrator/agent.py # w2-orchestration scope
│   ├── prediction/agent.py
│   ├── vision/agent.py
│   └── voice/agent.py
├── core/
│   ├── demat.py              # entropy, info gain, question selection
│   ├── disease_kb.py         # w1-kb-v2 scope — DISEASE_DATABASE
│   └── question_bank.py      # w2-ask-coverage scope — CLINICAL_QUESTION_BANK
├── data/preprocessing/
│   └── text_preprocessor.py  # w0-assertion-nlp scope — polarity map
├── api/routes/
│   ├── diagnosis.py          # w3-engineering scope — split into routers
│   └── chat.py               # w0-red-flag-engine scope — SAFETY_KEYWORDS
├── core/red_flags.py         # NEW — w0-red-flag-engine
└── utils/redaction.py        # PHI redaction (P0 branch — do not regress)

frontend/src/
├── lib/api.ts                # w0-truthful-frontend scope — getDemoResults
├── app/diagnosis/page.tsx    # w0-truthful-frontend scope
└── components/diagnosis/     # SeverityBadge, ConfidenceChart, results

tests/
├── unit/                     # 18 files, 197 passing at baseline
├── integration/
└── safety/                   # NEW — w0-red-flag-engine adversarial suite

scripts/benchmark/
├── demat_benchmark.py        # circular — regression only
├── metrics.py                # top-k, Brier, ECE, McNemar
└── external_eval.py          # NEW — w1-external-eval

docs/research/public_release/ # frozen evidence base (citation source)
.planning/2026-10-28-aegismed-improvement-phase/  # this document set
```

## Code Style

Match the surrounding code. The codebase uses docstrings on every public
function, `Optional[...]`/`dict`/`list[...]` typing, loguru's `logger` in
backend modules, and `self.log(...)` inside `BaseAgent` subclasses.

Backend — a new agent-facing function:

```python
def _extract_symptoms(self, text: str) -> list[dict]:
    """Extract symptoms using pattern matching or BioBERT."""
    found = []
    for category, pattern in self.SYMPTOM_PATTERNS.items():
        matches = re.findall(pattern, text)
        for match in matches:
            found.append({"symptom": match, "category": category})

    seen = set()
    unique = []
    for s in found:
        if s["symptom"] not in seen:
            seen.add(s["symptom"])
            unique.append(s)

    return unique
```

Frontend — a component, matching the existing export style:

```tsx
export function SeverityBadge({ severity }: { severity: keyof typeof severityConfig }) {
  const config = severityConfig[severity];
  const Icon = config.icon;

  return (
    <span className={cn("inline-flex items-center gap-1.5 ...")}>
      <Icon size={12} />
      {config.label}
    </span>
  );
}
```

Conventions:

- Backend: `from __future__` is not used; type hints on public signatures;
  Google-style docstrings with `Args:`/`Returns:`; module-level constants in
  `UPPER_SNAKE_CASE`; no bare `print` in `src/` (use `logger`).
- Frontend: named exports (not default); `interface` for object shapes;
  `cn()` from `@/lib/utils` for conditional classes; Tailwind utility classes;
  no inline `style` objects except for computed chart colors.
- Tests: `pytest` classes named `Test<Unit>`, methods named `test_<behavior>`,
  fixtures via `@pytest.fixture`, assertions on public behavior rather than
  private state where possible.
- Comments explain *why*, never narrate *what*.

## Testing Strategy

| Level | Location | Scope | Runner |
|---|---|---|---|
| Unit | `tests/unit/` | Pure functions, agents in isolation | pytest |
| Golden | `tests/unit/test_assertion_golden.py` (NEW) | 200-case negation/lay-language set | pytest |
| Adversarial safety | `tests/safety/` (NEW) | Ambiguous emergency vignettes, out-of-scope refusal | pytest |
| Integration | `tests/integration/` | Agent chain, API routes | pytest |
| External evaluation | `scripts/benchmark/external_eval.py` (NEW) | Held-out public vignettes with bootstrap CIs | script |
| Frontend unit | `frontend/src/**/*.test.tsx` (NEW) | Components, API client error paths | Vitest |
| Contract | `tests/unit/test_api_contract.py` (NEW) | Response shape stability across refactors | pytest |

**Coverage expectations.** Every module must add tests that fail before the
change and pass after. Coverage percentage is not a gate — a module that adds
untestable branching is a module that needs a seam, not a coverage target.

**The golden harness is the release-blocking test for `w0-assertion-nlp`.**
It must reach ≥95% on a 200-case negation/lay-language set, and the live probe
case must flip:

```
Input:  "no fever, no cough, no chest pain"
Before: fever ✓, cough ✓, chest pain ✓  (all wrongly present)
After:  fever ✗, cough ✗, chest pain ✗  (all correctly absent)
```

**The adversarial suite is the release-blocking test for
`w0-red-flag-engine`:** 100% emergency-flagging on the gold set, plus working
refusal on out-of-KB input.

**No test may assert on a number that came from the circular benchmark.**
Such a test is a regression guard, not an accuracy claim, and must be named
to make that clear (e.g. `test_demat_smoke_regression_*`).

Full detail in [`TEST_PLAN.md`](TEST_PLAN.md).

## Boundaries

**Always:**

- Run `venv/bin/python -m pytest tests/ -v --tb=short` before every commit.
- Keep patient text out of logs. Use the redaction helpers in
  `src/utils/redaction.py`.
- Cite the research dossier for every performance or regulatory claim.
- Update `PROGRESS_TRACKER.md` and `progress.md` in the same commit as the
  code it describes.
- Add a test that fails before your change.
- Leave the existing `frontend_old/` Streamlit prototype alone unless a task
  explicitly names it.

**Ask first:**

- Changing the `DISEASE_DATABASE` condition keys or the question bank's
  likelihood tables — these change downstream numbers.
- Adding any dependency to `requirements.txt`.
- Editing the paper (`paper/phase3-paper/main.tex`) or the patent
  specification — these have legal consequences.
- Any change to `config/settings.py` defaults, especially `enforce_api_key`.
- Changing the `doctor_alert` boolean contract to anything else.
- Deleting or rewriting `data/benchmarks/results/` — the historical results
  are the record of what was claimed.

**Never:**

- Never fabricate, estimate, or infer a citation. If a source was not
  fetched, it is `UNKNOWN — how to find out: …`.
- Never let an LLM output widen the triage band, the severity, or the red-flag
  set.
- Never reintroduce a fallback that returns plausible-looking clinical content
  when the backend fails.
- Never log patient symptom text, even at debug level.
- Never report a self-generated benchmark number as an accuracy result.
- Never publish, present, or upload the CHIL manuscript before the provisional
  filing date `D0` exists.
- Never remove a failing test without replacing it with one that asserts the
  correct behavior.

## Success Criteria

The phase is complete when every wave gate in `CAPABILITY_MAP.md` is
satisfied with linked evidence, and:

- [ ] No code path in the frontend or backend renders a diagnosis without a
      backend response. Verified by an automated test, not by inspection.
- [ ] The live negation probe case flips; the golden harness is ≥95%.
- [ ] 100% emergency-flagging on the adversarial gold set; out-of-scope
      refusal works.
- [ ] No self-referential number appears in the paper, the patent
      specification, the README, or `docs/`.
- [ ] External top-1/top-3 with bootstrap CIs are published in-repo, with the
      open-ended setting as the headline.
- [ ] Empirical conformal coverage is within ±2pp of nominal on external data.
- [ ] Every KB condition carries an ICD-11 code and ≥1 PD-source citation.
- [ ] Every recommendation carries a source ID; citation coverage is enforced
      in code, not by convention.
- [ ] The LLM provably cannot widen the triage band — enforced by a test, not
      by a prompt instruction.
- [ ] Ask-coverage is measured and above the 36.9% field benchmark.
- [ ] DPDP consent flows, verifiable parental consent, encryption at rest,
      audit trail, retention, and export/delete are implemented.
- [ ] Counsel sign-off on CDSCO classification and product positioning is
      recorded.
- [ ] Patent claims are re-scoped and a professional prior-art search is filed.
- [ ] CI runs on every PR and is green: pytest, `tsc --noEmit`, `next build`,
      Vitest.
- [ ] The backend suite is green with no previously-passing test removed.

## Open Questions

Each of these blocks a specific module. They are listed here rather than
buried in specs so that one review can resolve them all.

1. **Paper thesis.** Does `publication-truth` phase A restate the paper's
   contribution as the *triage mechanism* (recommended — stronger, and matches
   the research's strategy paragraph), or remove the accuracy contribution and
   publish a mechanism paper? **Blocks `publication-truth`.**
2. **KB v2 authoring.** Who reviews 150 conditions and their red-flag
   criteria? In-house, a clinical advisor, or recruited reviewers? **Blocks
   `w1-kb-v2` scheduling; the engineering work can start without it.**
3. **Frontend test runner.** Vitest + React Testing Library + jsdom
   (recommended) vs. Jest. **Blocks `w3-engineering` task 3.**
4. **External eval headline setting.** Open-ended (recommended, 44.2% best
   model) or 3-candidate (62.5%)? The recommendation is to report both with
   open-ended as the headline. **Blocks `w1-external-eval` reporting.**
5. **Patent claim re-scope.** Should the re-scoping happen before the
   provisional filing (recommended — priority is preserved by date, but new
   matter generally cannot benefit from the original date) or as a PCT-stage
   amendment? **Blocks `w3-patent` and `publication-truth` phase B.**
6. **Local LLM choice.** BioMistral-7B vs MedGemma-4B for the offline
   fallback, and whether the CPU container has the RAM for either. **Blocks
   `w3-engineering` task 4.**
7. **IRB status.** Has the IRB protocol been submitted? This phase does not
   depend on it, but the paper's "future work" and any prospective claim do.
   **Does not block this phase.**
8. **CDSCO counsel.** Which counsel firm, and has the engagement letter been
   sent? **Blocks `w3-regulatory`; the product-language audit can start
   immediately.**
