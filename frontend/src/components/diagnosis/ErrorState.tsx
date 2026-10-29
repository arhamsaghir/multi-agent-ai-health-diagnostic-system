"use client";

import { AlertTriangle, Phone, RefreshCw } from "lucide-react";
import type { AegisMedApiError } from "@/lib/api";

/**
 * Typed error presentation for the diagnosis flow. The message and the
 * recovery affordance branch on the error kind; the emergency route is
 * always present, because a patient whose tool just failed may still be
 * experiencing an emergency. Disclaimers are not a safety control — the
 * emergency route is an action (tel: link), not a paragraph.
 */
const ERROR_COPY: Record<
  AegisMedApiError["kind"],
  { title: string; body: string; retryLabel: string }
> = {
  unreachable: {
    title: "Can't reach the analysis service",
    body: "Your information was not analyzed. Check your internet connection and try again.",
    retryLabel: "Try again",
  },
  server: {
    title: "The analysis service is temporarily unavailable",
    body: "This is usually temporary. Nothing about your case was recorded from this attempt — try again in a moment.",
    retryLabel: "Try again",
  },
  rejected: {
    title: "The request could not be processed",
    body: "The service refused this request. If it keeps happening, the service configuration may need attention.",
    retryLabel: "Try again",
  },
  malformed: {
    title: "The service returned an unreadable response",
    body: "The analysis service responded, but not with a usable result. Try again; if it repeats, this is a defect worth reporting.",
    retryLabel: "Try again",
  },
};

/** India universal emergency number; w3-regulatory moves this to backend-supplied config. */
export const EMERGENCY_NUMBER = "112";

export function ErrorState({
  error,
  onRetry,
}: {
  error: AegisMedApiError;
  onRetry?: () => void;
}) {
  const copy = ERROR_COPY[error.kind];

  return (
    <div
      role="alert"
      data-testid="error-state"
      className="p-6 rounded-2xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 shadow-sm space-y-4"
    >
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-xl bg-amber-100 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 flex items-center justify-center shrink-0">
          <AlertTriangle size={20} />
        </div>
        <div className="space-y-1">
          <h3 className="font-bold text-neutral-900 dark:text-white">{copy.title}</h3>
          <p className="text-sm text-neutral-600 dark:text-neutral-300">{copy.body}</p>
        </div>
      </div>

      <div
        data-testid="error-emergency"
        className="flex flex-wrap items-center justify-between gap-3 p-4 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800"
      >
        <p className="text-sm font-medium text-red-800 dark:text-red-200">
          If you are experiencing a medical emergency, do not wait for this
          service — call or go to the nearest emergency room now.
        </p>
        <a
          href={`tel:${EMERGENCY_NUMBER}`}
          data-testid="error-emergency-call"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700 text-white text-sm font-bold transition-colors"
        >
          <Phone size={16} />
          Call {EMERGENCY_NUMBER}
        </a>
      </div>

      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          data-testid="error-retry"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-neutral-200 dark:border-neutral-700 text-sm font-semibold text-neutral-700 dark:text-neutral-200 hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors"
        >
          <RefreshCw size={16} />
          {copy.retryLabel}
        </button>
      )}
    </div>
  );
}
