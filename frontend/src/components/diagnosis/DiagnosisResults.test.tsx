import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { DiagnosisResults, type DiagnosisResult } from "./DiagnosisResults";

vi.mock("@/lib/persona", () => ({
  usePersona: () => ({ persona: "patient", setPersona: vi.fn() }),
}));

afterEach(cleanup);

function makeResult(overrides: Partial<DiagnosisResult> = {}): DiagnosisResult {
  return {
    condition: "Pneumonia",
    confidence: 0.7,
    severity: "high",
    description: "Consistent with pneumonia.",
    recommendations: ["See a doctor", "Rest", "Hydrate"],
    redFlags: [],
    patientExplanation: "You may have pneumonia.",
    clinicalExplanation: "Findings consistent with pneumonia.",
    doctorAlert: false,
    ...overrides,
  };
}

describe("DiagnosisResults — red flags are never truncated", () => {
  it("renders all red flags returned by the backend (4 in, 4 out)", () => {
    const results = [
      makeResult({
        redFlags: [
          "Flag one",
          "Flag two",
          "Flag three",
          "Flag four",
        ],
      }),
    ];
    render(<DiagnosisResults results={results} />);
    const list = screen.getByTestId("red-flag-list");
    expect(list.children).toHaveLength(4);
  });
});

describe("DiagnosisResults — action-first escalation", () => {
  it("leads with the crisis card when the result escalates", () => {
    render(
      <DiagnosisResults
        results={[makeResult({ doctorAlert: true, redFlags: ["Chest pain at rest"] })]}
      />
    );
    expect(screen.getByTestId("crisis-card")).toBeInTheDocument();
    expect(screen.getByTestId("crisis-call")).toHaveAttribute("href", "tel:112");
    expect(screen.getByTestId("crisis-sms")).toHaveAttribute("href", "sms:112");
  });

  it("escalates on critical severity even without doctorAlert", () => {
    render(<DiagnosisResults results={[makeResult({ severity: "critical" })]} />);
    expect(screen.getByTestId("crisis-card")).toBeInTheDocument();
  });

  it("does not render the crisis card for a routine result", () => {
    render(<DiagnosisResults results={[makeResult({ severity: "low" })]} />);
    expect(screen.queryByTestId("crisis-card")).not.toBeInTheDocument();
  });
});

describe("DiagnosisResults — demo results are unmistakable", () => {
  it("renders the demo banner and synthetic marker when source=demo", () => {
    render(<DiagnosisResults results={[makeResult()]} source="demo" />);
    expect(screen.getByTestId("demo-banner")).toBeInTheDocument();
    expect(screen.getByTestId("demo-marker")).toBeInTheDocument();
  });

  it("renders no demo marker for live results", () => {
    render(<DiagnosisResults results={[makeResult()]} source="live" />);
    expect(screen.queryByTestId("demo-banner")).not.toBeInTheDocument();
    expect(screen.queryByTestId("demo-marker")).not.toBeInTheDocument();
  });
});
