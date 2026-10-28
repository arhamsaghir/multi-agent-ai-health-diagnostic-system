# Spec: `w0-truthful-frontend`

**Module id:** `w0-truthful-frontend` · **Wave:** 0 · **Owner:** frontend
**Closes gap:** 11 · **Depends on:** — · **Blocks:** `w3-regulatory`
**Status:** not started

## Objective

**No code path renders a diagnosis without a backend response.**

Today, `frontend/src/lib/api.ts` catches every failure of the live diagnosis
call and returns `getDemoResults(text)` — a rule-based function that invents
plausible clinical content from substring matching on the patient's symptom
text. The patient cannot tell the difference between a real analysis and a
fabricated one. The same function is reachable through `demoMode: true` on the
public `diagnose()` entry point.

This is the worst anti-pattern available in a safety context: a system that
fails open with confident-looking medical text. The research is unambiguous
that disclaimers are not a safety control (readership falls from 26% to under
1%), so the fix cannot be a warning banner. It has to be an error state.

**User story:** *As a patient, when the backend is unreachable I see a clear
error and a route to help — never a diagnosis that was never computed.*

## In scope

- `frontend/src/lib/api.ts` — remove `getDemoResults` from every live error
  path; restructure `diagnose()`, `refineDiagnosis()`, and the streaming
  variants to surface failures.
- `frontend/src/app/diagnosis/page.tsx` — render explicit error states;
  remove the fail-soft "moderate" severity default.
- `frontend/src/components/diagnosis/DiagnosisResults.tsx` — stop truncating
  red flags to `flags[:3]`; add the action-first escalation card.
- A new error-state component and a Vitest test suite for the API client.

## Out of scope

- Removing `getDemoResults` entirely. It is still needed for the explicit
  demo mode; it just must not be reachable as a *fallback*.
- Any backend change. The backend already returns errors properly.
- The `flags[:3]` truncation is fixed here because it hides red flags; the
  full escalation UI design belongs to `w2-ask-coverage`.
- Copy changes for product positioning ("diagnosis" → "assessment"). That is
  `w3-regulatory`.

## Current state (verified)

`frontend/src/lib/api.ts`:

- `:105-139` — `diagnose(text, history, demoMode = false)`. On `demoMode`,
  returns `getDemoResults(text)` directly. On any thrown error, logs
  `"Live API call failed, providing demo fallback:"` and returns
  `getDemoResults(text)`.
- `:502+` — `getDemoResults(text)` matches on `textLower.includes(...)` for
  chest pain/heart/breath, cough/fever/breathing, headache/dizz/light
  sensitivity, and thirst/urinate/fatigue, returning fixed conditions with
  hardcoded confidences (0.85, 0.78, 0.72, 0.68), severities, and
  recommendations.
- `:180+` — `refineDiagnosis()` — the same fallback pattern.
- `:284+` — `streamDiagnosis()` and `:311+` — `streamRefineDiagnosis()` —
  these throw on a missing result payload but do not fall back to fabricated
  content; they are the correct pattern to follow.

## Requirements

**R1 — The live diagnosis call never returns fabricated clinical content.**
`diagnose()`, `refineDiagnosis()`, `streamDiagnosis()`, and
`streamRefineDiagnosis()` must either return a response transformed from a
successful backend payload, or throw a typed error.

**R2 — Errors are typed and distinguishable.** The API client must expose an
error type the UI can branch on, distinguishing at minimum: backend
unreachable (network/DNS), backend error (5xx), backend rejected the request
(4xx), and malformed response (2xx with an unusable body). The UI shows a
different message and a different recovery action for each.

**R3 — No default severity.** The current fail-soft default of `"moderate"`
must not exist. If no severity is present in the response, that is an error,
not a default.

**R4 — Red flags are not truncated.** The `flags[:3]` truncation is removed.
All red flags returned by the backend are displayed.

**R5 — Escalation is action-first.** When a result carries an escalation
signal, the UI leads with a crisis card: one-tap call and one-tap SMS/text
actions, prominent severity, and a short "do this now" instruction. The
explanation follows; it does not lead.

**R6 — Demo mode is explicit and labeled.** `demoMode` remains available but
the UI must make the synthetic nature unmistakable — a persistent banner, and
results rendered with a synthetic-source marker. A demo result must never be
indistinguishable from a live result.

**R7 — No patient text in client logs.** The current
`console.warn("Live API call failed, providing demo fallback:", error)` path
is removed. If any error is logged, it must not include symptom text.

## Acceptance criteria

- [ ] A test asserts that when the backend is unreachable, `diagnose()`
      rejects rather than resolving with clinical content.
- [ ] A test asserts that a 500 response rejects.
- [ ] A test asserts that a 200 response with a malformed body rejects.
- [ ] Grep confirms no reachable call path from the live diagnosis flow to
      `getDemoResults` other than the explicit `demoMode` branch.
- [ ] A test asserts that a result with no `severity` is rejected rather than
      defaulted to `"moderate"`.
- [ ] A test asserts that 4 red flags in a result produce 4 rendered flags.
- [ ] A test asserts that demo-mode results render a visible synthetic-source
      marker.
- [ ] Grep confirms no `console.*` call in the frontend includes symptom text.
- [ ] `cd frontend && npm run build` succeeds.
- [ ] `cd frontend && npm test` passes.

## Files in scope

| File | Change |
|---|---|
| `frontend/src/lib/api.ts` | Remove fallbacks; add typed error; keep `getDemoResults` for explicit demo only |
| `frontend/src/app/diagnosis/page.tsx` | Error state rendering; remove fail-soft default |
| `frontend/src/components/diagnosis/DiagnosisResults.tsx` | Crisis card; remove `flags[:3]` |
| `frontend/src/components/diagnosis/ErrorState.tsx` | **NEW** — typed error presentation |
| `frontend/src/lib/api.test.ts` | **NEW** — API client contract tests |
| `frontend/src/components/diagnosis/ErrorState.test.tsx` | **NEW** |

## Interfaces

```typescript
export type ApiErrorKind =
  | "unreachable"   // network failure, DNS, CORS
  | "server"        // 5xx
  | "rejected"      // 4xx
  | "malformed";    // 2xx with unusable body

export class AegisMedApiError extends Error {
  readonly kind: ApiErrorKind;
  readonly status?: number;
  constructor(kind: ApiErrorKind, message: string, status?: number) { ... }
}
```

The UI branches on `error.kind`. The error message shown to a patient is
written in plain language with a recovery action; the technical detail is
logged without patient text.

## Testing strategy

- **API client tests** (Vitest + jsdom): mock `fetch` to reject, to return
  500, 404, and a malformed 200. Assert rejection with the right `kind`.
- **Component tests** (React Testing Library): render `<ErrorState>` for each
  `kind` and assert the recovery affordance; render results with 4 red flags
  and assert 4 are present; render an escalation result and assert the crisis
  card's call and SMS buttons are present.
- **No test may assert on demo content being returned from a failed live
  call.** That is the behavior being removed.

## Boundaries

- **Always:** keep `getDemoResults` available for the explicit demo path;
  preserve the P0 branch's `fetchSystemHealth` addition; keep patient text
  out of all client logs.
- **Ask first:** changing the `DiagnosisResult` interface shape (other modules
  consume it — `w1-conformal` adds fields); adding a new frontend dependency
  beyond the test runner.
- **Never:** reintroduce a catch-all fallback; return partial clinical content
  on error; default a missing severity; hide red flags behind truncation.

## Success criteria

A patient with the backend down sees a clear error with a route to help. A
patient with the backend up sees only real backend output. There is no code
path, reachable from the live flow, that produces clinical content that the
backend did not produce.

## Open questions

1. **Escalation contact numbers.** The crisis card needs real, jurisdiction-
   correct emergency numbers (India: 112 / 108). The backend should supply
   them rather than the frontend hardcoding them, but no such field exists
   today. **Recommend:** add an `escalation_contacts` field to the backend
   response in this module, sourced from configuration, so the frontend
   renders what the server says.
2. **Does the error state need a retry with backoff?** Recommend yes — a
   single retry after 2s, since most failures here are the OmniRoute 503
   pattern documented in project memory.
3. **Does the demo mode need to survive into the public release at all?**
   Recommend yes for the public site, with the explicit synthetic marker from
   R6, since it is a legitimate way to demonstrate the UI without a backend.
