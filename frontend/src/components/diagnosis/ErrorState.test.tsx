import { cleanup, render, screen, fireEvent } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AegisMedApiError } from "@/lib/api";
import { ErrorState, EMERGENCY_NUMBER } from "./ErrorState";

afterEach(cleanup);

function makeError(kind: AegisMedApiError["kind"], status?: number): AegisMedApiError {
  return new AegisMedApiError(kind, `test ${kind}`, status);
}

describe("ErrorState", () => {
  it.each(["unreachable", "server", "rejected", "malformed"] as const)(
    "renders a kind-specific message for %s",
    (kind) => {
      render(<ErrorState error={makeError(kind)} />);
      expect(screen.getByTestId("error-state")).toBeInTheDocument();
      expect(screen.getByRole("alert")).toBeInTheDocument();
    }
  );

  it("always offers the emergency route as an action, not a disclaimer", () => {
    render(<ErrorState error={makeError("unreachable")} />);
    const call = screen.getByTestId("error-emergency-call");
    expect(call).toHaveAttribute("href", `tel:${EMERGENCY_NUMBER}`);
    expect(screen.getByText(new RegExp(`Call ${EMERGENCY_NUMBER}`))).toBeInTheDocument();
  });

  it("shows the retry affordance and invokes it", () => {
    const onRetry = vi.fn();
    render(<ErrorState error={makeError("server")} onRetry={onRetry} />);

    const retry = screen.getByTestId("error-retry");
    expect(retry).toBeInTheDocument();
    fireEvent.click(retry);
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("omits the retry button when no retry action is available", () => {
    render(<ErrorState error={makeError("malformed")} />);
    expect(screen.queryByTestId("error-retry")).not.toBeInTheDocument();
  });

  it("does not render symptom text or error internals", () => {
    render(
      <ErrorState error={new AegisMedApiError("server", "internal: patient said X")} />
    );
    expect(screen.queryByText(/patient said X/)).not.toBeInTheDocument();
  });
});
