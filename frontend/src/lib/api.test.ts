import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  AegisMedApiError,
  diagnose,
  getDemoResults,
  refineDiagnosis,
} from "./api";

const VALID_PAYLOAD = {
  diagnosis: [
    {
      name: "Upper Respiratory Infection",
      confidence: 0.7,
      severity: "low",
      description: "Viral upper respiratory infection.",
      recommendations: ["Rest", "Hydration"],
      redFlags: ["Fever above 102F", "Difficulty breathing"],
    },
  ],
  severity: "low",
  explanation: "Mild presentation.",
  patient_explanation: "You have a mild infection.",
  recommendations: ["Rest"],
  red_flags: ["Fever above 102F"],
  doctor_alert: false,
  confidence: { breakdown: { nlp: 0.8 } },
};

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

const HISTORY = { age: 30, bmi: 22, gender: "female", familyHistory: [] };

describe("diagnose() — no fabricated output", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });
  afterEach(() => {
    vi.useRealTimers();
  });

  it("rejects with kind=unreachable when the backend is unreachable (no demo content)", async () => {
    vi.useFakeTimers();
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.reject(new TypeError("fetch failed")))
    );

    const promise = diagnose("I have a cough", HISTORY);
    const assertion = expect(promise).rejects.toMatchObject({
      name: "AegisMedApiError",
      kind: "unreachable",
    });
    // Two attempts with a 2s backoff between them.
    await vi.advanceTimersByTimeAsync(2100);
    await assertion;
    expect(vi.mocked(globalThis.fetch)).toHaveBeenCalledTimes(2);
  });

  it("rejects with kind=server on a 500 response", async () => {
    vi.useFakeTimers();
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.resolve(jsonResponse({ detail: "boom" }, 500)))
    );

    const promise = diagnose("I have a cough", HISTORY);
    const assertion = expect(promise).rejects.toMatchObject({
      kind: "server",
      status: 500,
    });
    await vi.advanceTimersByTimeAsync(2100);
    await assertion;
  });

  it("does not retry a 4xx and rejects with kind=rejected", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.resolve(jsonResponse({ detail: "nope" }, 404)))
    );

    await expect(diagnose("I have a cough", HISTORY)).rejects.toMatchObject({
      kind: "rejected",
      status: 404,
    });
    expect(vi.mocked(globalThis.fetch)).toHaveBeenCalledTimes(1);
  });

  it("rejects with kind=malformed on a 200 body without severity (no moderate default)", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.resolve(jsonResponse({ diagnosis: [], explanation: "x" })))
    );

    await expect(diagnose("I have a cough", HISTORY)).rejects.toMatchObject({
      kind: "malformed",
    });
  });

  it("rejects with kind=malformed when an entry carries an unknown severity", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve(
          jsonResponse({
            ...VALID_PAYLOAD,
            severity: "sort of bad",
            diagnosis: [{ name: "X", severity: "sort of bad" }],
          })
        )
      )
    );

    await expect(diagnose("I have a cough", HISTORY)).rejects.toMatchObject({
      kind: "malformed",
    });
  });

  it("rejects with kind=malformed on a 200 non-JSON body", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.resolve(new Response("<html>oops</html>", { status: 200 })))
    );

    await expect(diagnose("I have a cough", HISTORY)).rejects.toMatchObject({
      kind: "malformed",
    });
  });

  it("resolves with transformed results after a transient network failure", async () => {
    vi.useFakeTimers();
    const fetchMock = vi
      .fn()
      .mockRejectedValueOnce(new TypeError("fetch failed"))
      .mockResolvedValueOnce(jsonResponse(VALID_PAYLOAD));
    vi.stubGlobal("fetch", fetchMock);

    const promise = diagnose("I have a cough", HISTORY);
    await vi.advanceTimersByTimeAsync(2100);
    const results = await promise;

    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(results[0].condition).toBe("Upper Respiratory Infection");
    expect(results[0].severity).toBe("low");
    expect(results[0].redFlags).toHaveLength(2);
  });

  it("returns real backend content on success", async () => {
    vi.stubGlobal("fetch", vi.fn(() => Promise.resolve(jsonResponse(VALID_PAYLOAD))));

    const results = await diagnose("I have a cough", HISTORY);
    expect(results).toHaveLength(1);
    expect(results[0].patientExplanation).toBe("You have a mild infection.");
  });

  it("demoMode returns synthetic content without calling the backend", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    const results = await diagnose("chest pain", HISTORY, true);
    expect(results[0].condition).toBe("Cardiovascular Disease");
    expect(fetchMock).not.toHaveBeenCalled();
  });
});

describe("refineDiagnosis()", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("rejects instead of fabricating when the backend fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.resolve(jsonResponse({ detail: "nope" }, 500)))
    );

    await expect(
      refineDiagnosis("cough", HISTORY, [{ id: "q1", question: "Fever?", answer: "Yes" }])
    ).rejects.toBeInstanceOf(AegisMedApiError);
  });

  it("returns backend results and triage on success", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve(jsonResponse({ ...VALID_PAYLOAD, triage: { session_id: "s1" } }))
      )
    );

    const { results, triage } = await refineDiagnosis(
      "cough",
      HISTORY,
      [{ id: "q1", question: "Fever?", answer: "Yes" }],
      "s1"
    );
    expect(results).toHaveLength(1);
    expect(triage).toEqual({ session_id: "s1" });
  });
});

describe("demo content isolation", () => {
  it("is only reachable through the explicit demoMode branch", () => {
    // The live error path must not fall back into getDemoResults: the only
    // permitted occurrences in api.ts are the function declaration and the
    // demoMode branch inside diagnose().
    const fs = require("node:fs");
    const source = fs.readFileSync(require.resolve("./api.ts"), "utf8");
    const occurrences = source.match(/getDemoResults\(/g) ?? [];
    expect(occurrences).toHaveLength(2); // declaration + the demoMode branch
    const callLines = source
      .split("\n")
      .filter((line: string) => line.includes("getDemoResults(") && !line.includes("export function"));
    expect(callLines).toHaveLength(1);
    // The sole call site must sit inside the explicit demoMode branch —
    // verify the guard on the preceding non-empty line.
    const callIndex = source.split("\n").findIndex((line: string) => line.includes("getDemoResults(") && !line.includes("export function"));
    const preceding = source.split("\n").slice(0, callIndex).filter((line: string) => line.trim()).pop() ?? "";
    expect(preceding).toContain("if (demoMode)");
  });
});
