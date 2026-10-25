"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { SymptomInput, type PatientHistory } from "@/components/diagnosis/SymptomInput";
import { DiagnosisResults } from "@/components/diagnosis/DiagnosisResults";
import { FollowUpQuestions } from "@/components/diagnosis/FollowUpQuestions";
import { AgentExecutionStepper } from "@/components/diagnosis/AgentExecutionStepper";
import {
  diagnose,
  fetchFollowUpQuestions,
  streamDiagnosis,
  streamRefineDiagnosis,
  type AgentProgressEvent,
  type FollowUpQuestion,
  type TriageInfo,
} from "@/lib/api";
import type { DiagnosisResult } from "@/components/diagnosis/DiagnosisResults";

type TriageStep = "input" | "follow_up" | "running" | "results";

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
  const [isLoading, setIsLoading] = useState(false);
  const [isRefining, setIsRefining] = useState(false);

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

  /** Run the streamed analysis pipeline (direct path — no follow-up questions). */
  const runStreamedAnalysis = useCallback(
    async (text: string, history: PatientHistory, triage?: TriageInfo) => {
      setProgressEvents([triageSeedEvent(triage)]);
      setStep("running");
      try {
        const streamed = await streamDiagnosis(text, history, appendEvent);
        setResults(streamed.results);
        if (streamed.triage) setTriageInfo(streamed.triage);
        setStep("results");
      } catch (streamErr) {
        console.warn("Streaming analysis failed, falling back to standard call:", streamErr);
        try {
          const directResults = await diagnose(text, history, false);
          setResults(directResults);
          setStep("results");
        } catch (diagErr) {
          console.error("Diagnosis error:", diagErr);
          setStep("input");
        }
      }
    },
    [appendEvent]
  );

  const handleInitialSubmit = useCallback(async (text: string, history: PatientHistory) => {
    setIsLoading(true);
    setActiveText(text);
    setActiveHistory(history);

    try {
      // 1. Query the DEMAT Active Triage engine for entropy-minimizing questions
      const followUp = await fetchFollowUpQuestions(text, history);

      if (followUp.questions && followUp.questions.length > 0) {
        setQuestions(followUp.questions);
        setTriageInfo(followUp.triage);
        setSessionId(followUp.session_id);
        setIsLoading(false);
        setStep("follow_up");
        return;
      }
      // Entropy already low — run the streamed pipeline directly
      await runStreamedAnalysis(text, history, followUp.triage);
    } catch (err) {
      console.warn("Follow-up check failed, evaluating initial diagnosis directly:", err);
      await runStreamedAnalysis(text, history);
    } finally {
      setIsLoading(false);
    }
  }, [runStreamedAnalysis]);

  const handleRefineSubmit = useCallback(
    async (answers: Array<{ id: string; question: string; answer: string }>) => {
      setIsRefining(true);
      setProgressEvents([triageSeedEvent(triageInfo)]);
      setStep("running");
      try {
        const refined = await streamRefineDiagnosis(activeText, activeHistory, answers, appendEvent, sessionId);
        setResults(refined.results);
        if (refined.triage) {
          setTriageInfo(refined.triage);
        }
        setStep("results");
      } catch (err) {
        console.warn("Refinement failed, generating standard diagnosis:", err);
        try {
          const directResults = await diagnose(activeText, activeHistory, false);
          setResults(directResults);
          setStep("results");
        } catch (diagErr) {
          console.error("Diagnosis error:", diagErr);
          setStep("input");
        }
      } finally {
        setIsRefining(false);
      }
    },
    [activeText, activeHistory, sessionId, triageInfo, appendEvent]
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
    setQuestions([]);
    setTriageInfo(undefined);
    setSessionId("");
    setProgressEvents([]);
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
              />
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
