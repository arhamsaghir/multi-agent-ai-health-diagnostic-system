"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { SymptomInput, type PatientHistory } from "@/components/diagnosis/SymptomInput";
import { DiagnosisResults } from "@/components/diagnosis/DiagnosisResults";
import { FollowUpQuestions } from "@/components/diagnosis/FollowUpQuestions";
import { AgentExecutionStepper } from "@/components/diagnosis/AgentExecutionStepper";
import { ErrorState } from "@/components/diagnosis/ErrorState";
import {
  fetchFollowUpQuestions,
  getDemoResults,
  streamDiagnosis,
  streamRefineDiagnosis,
  toAegisMedApiError,
  type AegisMedApiError,
  type AgentProgressEvent,
  type FollowUpQuestion,
  type TriageInfo,
} from "@/lib/api";
import type { DiagnosisResult } from "@/components/diagnosis/DiagnosisResults";

type TriageStep = "input" | "follow_up" | "running" | "results" | "error";

/** Synthetic completed event so the stepper shows triage as done when the pipeline starts. */
function triageSeedEvent(triage?: TriageInfo): AgentProgressEvent {
  const top = triage?.top_candidates?.[0];
  return {
    type: "agent",
    node: "triage",
    agent: "DEMAT Active Triage",
    model: "Entropy Minimization",
    status: "completed",
    elapsed_ms: 0,
    summary: triage
      ? `entropy ${triage.entropy_bits} bits · top: ${top?.name ?? "—"} ${top ? `${Math.round(top.probability * 100)}%` : ""}`
      : "converged",
  };
}

export default function DiagnosisPage() {
  const [step, setStep] = useState<TriageStep>("input");
  const [results, setResults] = useState<DiagnosisResult[] | null>(null);
  const [resultSource, setResultSource] = useState<"live" | "demo">("live");
  const [isLoading, setIsLoading] = useState(false);
  const [isRefining, setIsRefining] = useState(false);
  const [error, setError] = useState<AegisMedApiError | null>(null);
  const [retryAction, setRetryAction] = useState<(() => void) | null>(null);

  // Active triage state
  const [activeText, setActiveText] = useState("");
  const [activeHistory, setActiveHistory] = useState<PatientHistory>({
    age: 30,
    bmi: 22,
    gender: "other",
    familyHistory: [],
  });
  const [sessionId, setSessionId] = useState<string>("");
  const [questions, setQuestions] = useState<FollowUpQuestion[]>([]);
  const [triageInfo, setTriageInfo] = useState<TriageInfo | undefined>(undefined);

  // Live pipeline execution state
  const [progressEvents, setProgressEvents] = useState<AgentProgressEvent[]>([]);

  const appendEvent = useCallback((event: AgentProgressEvent) => {
    setProgressEvents((prev) => [...prev, event]);
  }, []);

  /** Surface a failure as an error state with a retry affordance. No fallback content. */
  const failWith = useCallback((err: unknown, retry: () => void) => {
    setError(toAegisMedApiError(err));
    setRetryAction(() => retry);
    setStep("error");
  }, []);

  /** Run the streamed analysis pipeline (direct path — no follow-up questions). */
  const runStreamedAnalysis = useCallback(
    async (text: string, history: PatientHistory, triage?: TriageInfo) => {
      setProgressEvents([triageSeedEvent(triage)]);
      setStep("running");
      try {
        const streamed = await streamDiagnosis(text, history, appendEvent);
        setResults(streamed.results);
        setResultSource("live");
        if (streamed.triage) setTriageInfo(streamed.triage);
        setStep("results");
      } catch (streamErr) {
        failWith(streamErr, () => runStreamedAnalysis(text, history, triage));
      }
    },
    [appendEvent, failWith]
  );

  const handleInitialSubmit = useCallback(
    async (text: string, history: PatientHistory, demoMode: boolean) => {
      setIsLoading(true);
      setActiveText(text);
      setActiveHistory(history);
      setError(null);

      try {
        // Demo mode is explicit: synthetic example content, rendered with a
        // persistent marker, without touching the backend.
        if (demoMode) {
          setResults(getDemoResults(text));
          setResultSource("demo");
          setStep("results");
          return;
        }

        // 1. Query the DEMAT Active Triage engine for entropy-minimizing questions
        const followUp = await fetchFollowUpQuestions(text, history);

        if (followUp.questions && followUp.questions.length > 0) {
          setQuestions(followUp.questions);
          setTriageInfo(followUp.triage);
          setSessionId(followUp.session_id);
          setStep("follow_up");
          return;
        }
        // Entropy already low — run the streamed pipeline directly
        await runStreamedAnalysis(text, history, followUp.triage);
      } catch (err) {
        failWith(err, () => handleInitialSubmit(text, history, demoMode));
      } finally {
        setIsLoading(false);
      }
    },
    [runStreamedAnalysis, failWith]
  );

  const handleRefineSubmit = useCallback(
    async (answers: Array<{ id: string; question: string; answer: string }>) => {
      setIsRefining(true);
      setProgressEvents([triageSeedEvent(triageInfo)]);
      setStep("running");
      try {
        const refined = await streamRefineDiagnosis(activeText, activeHistory, answers, appendEvent, sessionId);
        setResults(refined.results);
        setResultSource("live");
        if (refined.triage) {
          setTriageInfo(refined.triage);
        }
        setStep("results");
      } catch (err) {
        failWith(err, () => handleRefineSubmit(answers));
      } finally {
        setIsRefining(false);
      }
    },
    [activeText, activeHistory, sessionId, triageInfo, appendEvent, failWith]
  );

  const handleSkipFollowUp = useCallback(async () => {
    setIsRefining(true);
    try {
      await runStreamedAnalysis(activeText, activeHistory, triageInfo);
    } finally {
      setIsRefining(false);
    }
  }, [activeText, activeHistory, triageInfo, runStreamedAnalysis]);

  const handleReset = useCallback(() => {
    setStep("input");
    setResults(null);
    setResultSource("live");
    setQuestions([]);
    setTriageInfo(undefined);
    setSessionId("");
    setProgressEvents([]);
    setError(null);
    setRetryAction(null);
  }, []);

  return (
    <div className="max-w-4xl mx-auto py-4">
      <AnimatePresence mode="wait">
        {step === "input" && (
          <motion.div
            key="input"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <SymptomInput onSubmit={handleInitialSubmit} isLoading={isLoading} />
          </motion.div>
        )}

        {step === "follow_up" && (
          <motion.div
            key="follow_up"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <FollowUpQuestions
              questions={questions}
              triage={triageInfo}
              onSubmit={handleRefineSubmit}
              onSkip={handleSkipFollowUp}
              isSubmitting={isRefining}
            />
          </motion.div>
        )}

        {step === "running" && (
          <motion.div
            key="running"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <AgentExecutionStepper events={progressEvents} running />
          </motion.div>
        )}

        {step === "error" && error && (
          <motion.div
            key="error"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <ErrorState
              error={error}
              onRetry={
                retryAction
                  ? () => {
                      setError(null);
                      setRetryAction(null);
                      retryAction();
                    }
                  : undefined
              }
            />
          </motion.div>
        )}

        {step === "results" && (
          <motion.div
            key="results"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Back Button */}
            <button
              onClick={handleReset}
              className="text-primary-600 dark:text-primary-400 hover:underline text-sm font-medium flex items-center gap-1.5"
            >
              ← Start New Diagnosis
            </button>

            {/* Compact trace of the completed run */}
            {progressEvents.length > 0 && (
              <AgentExecutionStepper events={progressEvents} running={false} />
            )}

            {/* Results Component */}
            {results && (
              <DiagnosisResults
                results={results}
                triage={triageInfo}
                sourceText={activeText}
                patientHistory={activeHistory}
                executionTrace={progressEvents}
                source={resultSource}
              />
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
