"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { HelpCircle, Sparkles, ArrowRight, SkipForward, Activity, CheckCircle2 } from "lucide-react";
import type { FollowUpQuestion, TriageInfo } from "@/lib/api";

interface FollowUpQuestionsProps {
  questions: FollowUpQuestion[];
  triage?: TriageInfo;
  onSubmit: (answers: Array<{ id: string; question: string; answer: string }>) => void;
  onSkip: () => void;
  isSubmitting?: boolean;
}

export function FollowUpQuestions({
  questions,
  triage,
  onSubmit,
  onSkip,
  isSubmitting = false,
}: FollowUpQuestionsProps) {
  const [answers, setAnswers] = useState<Record<string, string>>({});

  const handleSelectOption = (questionId: string, option: string) => {
    setAnswers((prev) => ({ ...prev, [questionId]: option }));
  };

  const handleTextChange = (questionId: string, text: string) => {
    setAnswers((prev) => ({ ...prev, [questionId]: text }));
  };

  const allAnswered = questions.every((q) => Boolean(answers[q.id]?.trim()));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const formatted = questions.map((q) => ({
      id: q.id,
      question: q.question,
      answer: answers[q.id] || "No answer provided",
    }));
    onSubmit(formatted);
  };

  // Compute certainty percentage from entropy (max ~3.32 bits for 10 diseases)
  const entropy = triage?.entropy_bits ?? 2.8;
  const certaintyPercent = Math.max(10, Math.min(95, Math.round((1.0 - entropy / 3.32) * 100)));

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      className="space-y-6"
    >
      {/* DEMAT Algorithmic Header Banner */}
      <div className="p-5 rounded-2xl bg-gradient-to-r from-teal-500/10 via-primary-500/10 to-indigo-500/10 border border-teal-500/20 dark:border-teal-500/30">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-teal-600 dark:text-teal-400" />
              <h2 className="text-lg font-bold text-neutral-900 dark:text-white">
                Dynamic Active Triage Engine (DEMAT)
              </h2>
            </div>
            <p className="text-xs text-neutral-600 dark:text-neutral-300">
              The multi-agent system calculated diagnostic entropy of{" "}
              <span className="font-semibold text-teal-600 dark:text-teal-400">
                {entropy.toFixed(2)} bits
              </span>
              . Answering these targeted questions maximizes mutual information gain to refine your diagnosis.
            </p>
          </div>

          <div className="shrink-0 text-right">
            <span className="text-xs font-semibold text-neutral-500 dark:text-neutral-400 uppercase tracking-wider block">
              Diagnostic Confidence
            </span>
            <span className="text-2xl font-bold text-teal-600 dark:text-teal-400">
              {certaintyPercent}%
            </span>
          </div>
        </div>

        {/* Confidence Progress Bar */}
        <div className="mt-4 w-full bg-neutral-200 dark:bg-neutral-800 rounded-full h-2 overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${certaintyPercent}%` }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="bg-gradient-to-r from-teal-500 to-primary-600 h-full rounded-full"
          />
        </div>

        {/* Current Top Differentials */}
        {triage?.top_candidates && triage.top_candidates.length > 0 && (
          <div className="mt-4 pt-3 border-t border-teal-500/15 flex flex-wrap items-center gap-2">
            <span className="text-xs font-semibold text-neutral-500 dark:text-neutral-400 flex items-center gap-1">
              <Activity size={13} className="text-teal-500" /> Leading Differentials:
            </span>
            {triage.top_candidates.slice(0, 3).map((cand) => (
              <span
                key={cand.disease}
                className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-white/80 dark:bg-neutral-900/80 text-neutral-800 dark:text-neutral-200 border border-neutral-200 dark:border-neutral-700"
              >
                <span>{cand.name}</span>
                <span className="text-teal-600 dark:text-teal-400 font-semibold">
                  {Math.round(cand.probability * 100)}%
                </span>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Questions Form */}
      <form onSubmit={handleSubmit} className="space-y-5">
        {questions.map((q, idx) => (
          <div
            key={q.id}
            className="p-6 rounded-2xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 shadow-sm space-y-4"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-start gap-3">
                <span className="flex items-center justify-center w-7 h-7 rounded-full bg-primary-100 dark:bg-primary-950 text-primary-700 dark:text-primary-300 text-xs font-bold shrink-0 mt-0.5">
                  Q{idx + 1}
                </span>
                <div>
                  <h3 className="text-base font-semibold text-neutral-900 dark:text-white leading-snug">
                    {q.question}
                  </h3>
                  {q.rationale && (
                    <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1 italic">
                      Clinical focus: {q.rationale}
                    </p>
                  )}
                </div>
              </div>
              {answers[q.id] && (
                <CheckCircle2 size={18} className="text-emerald-500 shrink-0 mt-1" />
              )}
            </div>

            {/* Multiple Choice / Yes-No Options */}
            {(q.type === "choice" || q.type === "yes_no") && q.options && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-1">
                {q.options.map((opt) => {
                  const isSelected = answers[q.id] === opt;
                  return (
                    <button
                      key={opt}
                      type="button"
                      onClick={() => handleSelectOption(q.id, opt)}
                      className={`text-left px-4 py-3 rounded-xl border text-sm font-medium transition-all ${
                        isSelected
                          ? "bg-primary-600 text-white border-primary-600 shadow-sm shadow-primary-600/20"
                          : "bg-neutral-50 dark:bg-neutral-800/60 text-neutral-800 dark:text-neutral-200 border-neutral-200 dark:border-neutral-700/80 hover:border-primary-400 hover:bg-neutral-100 dark:hover:bg-neutral-800"
                      }`}
                    >
                      {opt}
                    </button>
                  );
                })}
              </div>
            )}

            {/* Free Text Input */}
            {q.type === "text" && (
              <div className="pt-1">
                <input
                  type="text"
                  placeholder="Type your response here..."
                  value={answers[q.id] || ""}
                  onChange={(e) => handleTextChange(q.id, e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border border-neutral-300 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-800 text-neutral-900 dark:text-white placeholder:text-neutral-400 focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
                />
              </div>
            )}
          </div>
        ))}

        {/* Action Controls */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
          <button
            type="button"
            onClick={onSkip}
            className="w-full sm:w-auto flex items-center justify-center gap-2 px-5 py-3 text-sm font-medium text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white transition-colors"
          >
            <SkipForward size={16} />
            Skip & View Initial Diagnosis
          </button>

          <button
            type="submit"
            disabled={!allAnswered || isSubmitting}
            className={`w-full sm:w-auto flex items-center justify-center gap-2 px-8 py-3.5 rounded-xl text-sm font-semibold shadow-md transition-all ${
              allAnswered && !isSubmitting
                ? "bg-primary-600 hover:bg-primary-700 text-white shadow-primary-600/25"
                : "bg-neutral-200 dark:bg-neutral-800 text-neutral-400 cursor-not-allowed shadow-none"
            }`}
          >
            {isSubmitting ? (
              <span>Refining Differential...</span>
            ) : (
              <>
                <span>Refine & Finalize Diagnosis</span>
                <ArrowRight size={16} />
              </>
            )}
          </button>
        </div>
      </form>
    </motion.div>
  );
}
