"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { SymptomInput, type PatientHistory } from "@/components/diagnosis/SymptomInput";
import { DiagnosisResults } from "@/components/diagnosis/DiagnosisResults";
import { diagnose } from "@/lib/api";
import type { DiagnosisResult } from "@/components/diagnosis/DiagnosisResults";

export default function DiagnosisPage() {
  const [results, setResults] = useState<DiagnosisResult[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleDiagnosis = useCallback(async (text: string, history: PatientHistory) => {
    setIsLoading(true);
    setResults(null);

    try {
      // Connect to live FastAPI multi-agent backend (/api/diagnosis/analyze)
      const diagnosisResults = await diagnose(text, history, false);
      setResults(diagnosisResults);
    } catch (error) {
      console.error("Diagnosis error:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return (
    <div className="max-w-4xl mx-auto">
      <AnimatePresence mode="wait">
        {!results ? (
          <motion.div
            key="input"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <SymptomInput onSubmit={handleDiagnosis} isLoading={isLoading} />
          </motion.div>
        ) : (
          <motion.div
            key="results"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Back Button */}
            <button
              onClick={() => setResults(null)}
              className="text-primary-600 dark:text-primary-400 hover:underline text-sm font-medium"
            >
              ← Start New Diagnosis
            </button>

            <DiagnosisResults results={results} isLoading={isLoading} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}