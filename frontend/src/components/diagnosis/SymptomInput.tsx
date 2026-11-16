"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { 
  Send, 
  Mic, 
  MicOff, 
  Sparkles,
  AlertCircle,
  CheckCircle
} from "lucide-react";
import { cn } from "@/lib/utils";

interface SymptomInputProps {
  onSubmit: (text: string, history: PatientHistory, demoMode: boolean) => void;
  isLoading?: boolean;
}

export interface PatientHistory {
  age: number;
  bmi: number;
  gender: string;
  familyHistory: string[];
}

const demoHistory: PatientHistory = {
  age: 35,
  bmi: 24.5,
  gender: "female",
  familyHistory: [],
};

export function SymptomInput({ onSubmit, isLoading }: SymptomInputProps) {
  const [symptoms, setSymptoms] = useState("");
  const [showHistoryForm, setShowHistoryForm] = useState(false);
  const [history, setHistory] = useState<PatientHistory>(demoHistory);
  // Live analysis is the default; demo mode is an explicit opt-in whose
  // synthetic output is rendered with an unmistakable marker downstream.
  const [useDemoMode, setUseDemoMode] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (symptoms.trim()) {
      onSubmit(symptoms, history, useDemoMode);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Header */}
      <motion.div 
        className="flex items-center justify-between"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-neutral-900 dark:text-white">
            Health Assessment
          </h1>
          <p className="text-neutral-600 dark:text-neutral-400 mt-1">
            Describe your symptoms for AI-powered analysis
          </p>
        </div>
        
        {/* Demo Mode Toggle */}
        <button
          onClick={() => setUseDemoMode(!useDemoMode)}
          className={cn(
            "flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-colors",
            useDemoMode
              ? "bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300"
              : "bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400"
          )}
        >
          <Sparkles size={16} />
          Demo Mode
        </button>
      </motion.div>

      {/* Input Form */}
      <motion.form 
        onSubmit={handleSubmit} 
        className="space-y-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <div className="relative">
          <textarea
            value={symptoms}
            onChange={(e) => setSymptoms(e.target.value)}
            placeholder="Describe your symptoms in detail. For example: I've been having chest pain for the past 2 days, feeling short of breath when walking upstairs..."
            className="w-full h-40 p-4 rounded-xl border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white placeholder-neutral-400 resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
            disabled={isLoading}
          />
          
          {/* Character count */}
          <div className="absolute bottom-3 right-3 text-xs text-neutral-400">
            {symptoms.length} characters
          </div>
        </div>

        {/* Quick symptom buttons */}
        <div className="flex flex-wrap gap-2">
          {["Chest pain", "Fever", "Cough", "Headache", "Fatigue"].map((tag) => (
            <button
              key={tag}
              type="button"
              onClick={() => setSymptoms((prev) => prev ? `${prev}, ${tag.toLowerCase()}` : tag)}
              disabled={isLoading}
              className="px-3 py-1.5 text-sm rounded-full bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400 hover:bg-neutral-200 dark:hover:bg-neutral-700 transition-colors disabled:opacity-50"
            >
              + {tag}
            </button>
          ))}
        </div>

        {/* Patient History Toggle */}
        <button
          type="button"
          onClick={() => setShowHistoryForm(!showHistoryForm)}
          className="text-sm text-primary-600 dark:text-primary-400 hover:underline"
        >
          {showHistoryForm ? "Hide" : "Add"} patient history (optional)
        </button>

        {/* Patient History Form */}
        {showHistoryForm && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            className="grid grid-cols-2 lg:grid-cols-4 gap-4 p-4 rounded-xl bg-neutral-50 dark:bg-neutral-900"
          >
            <div>
              <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                Age
              </label>
              <input
                type="number"
                value={history.age}
                onChange={(e) => setHistory({ ...history, age: parseInt(e.target.value) || 0 })}
                className="w-full p-2 rounded-lg border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                BMI
              </label>
              <input
                type="number"
                step="0.1"
                value={history.bmi}
                onChange={(e) => setHistory({ ...history, bmi: parseFloat(e.target.value) || 0 })}
                className="w-full p-2 rounded-lg border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                Gender
              </label>
              <select
                value={history.gender}
                onChange={(e) => setHistory({ ...history, gender: e.target.value })}
                className="w-full p-2 rounded-lg border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white"
              >
                <option value="female">Female</option>
                <option value="male">Male</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                Family History
              </label>
              <select
                value={history.familyHistory[0] || ""}
                onChange={(e) => setHistory({ ...history, familyHistory: e.target.value ? [e.target.value] : [] })}
                className="w-full p-2 rounded-lg border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white"
              >
                <option value="">None</option>
                <option value="diabetes">Diabetes</option>
                <option value="heart_disease">Heart Disease</option>
                <option value="cancer">Cancer</option>
                <option value="hypertension">Hypertension</option>
              </select>
            </div>
          </motion.div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={!symptoms.trim() || isLoading}
          className={cn(
            "flex items-center justify-center gap-2 w-full py-3 px-6 rounded-xl font-semibold transition-all",
            symptoms.trim() && !isLoading
              ? "bg-primary-600 hover:bg-primary-700 text-white shadow-lg shadow-primary-500/25"
              : "bg-neutral-200 dark:bg-neutral-800 text-neutral-400 cursor-not-allowed"
          )}
        >
          {isLoading ? (
            <>
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <Send size={20} />
              Run Diagnosis
            </>
          )}
        </button>
      </motion.form>

      {/* Disclaimer */}
      <div className="flex items-start gap-3 p-4 rounded-xl bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800">
        <AlertCircle className="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-amber-800 dark:text-amber-200">
          <p className="font-medium">Important Disclaimer</p>
          <p className="mt-1 opacity-80">
            This system is for research and educational purposes only. 
            Always consult a healthcare professional for medical advice.
          </p>
        </div>
      </div>
    </motion.div>
  );
}