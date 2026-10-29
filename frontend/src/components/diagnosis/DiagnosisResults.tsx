"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Cell 
} from "recharts";
import {
  AlertTriangle,
  CheckCircle,
  Info,
  AlertCircle,
  Activity,
  FileText,
  FlaskConical,
  Download,
  Loader2,
  Phone,
  MessageSquare
} from "lucide-react";
import { cn } from "@/lib/utils";
import { usePersona } from "@/lib/persona";
import { downloadReport, type AgentProgressEvent, type TriageInfo } from "@/lib/api";
import { EMERGENCY_NUMBER } from "@/components/diagnosis/ErrorState";

export interface DiagnosisResult {
  condition: string;
  confidence: number;
  severity: "critical" | "high" | "moderate" | "low";
  description: string;
  recommendations: string[];
  redFlags: string[];
  icd10?: string;
  rationale?: string;
  patientExplanation?: string;
  clinicalExplanation?: string;
  doctorAlert?: boolean;
  confidenceBreakdown?: Record<string, number>;
}

interface DiagnosisResultsProps {
  results: DiagnosisResult[];
  isLoading?: boolean;
  triage?: TriageInfo;
  sourceText?: string;
  patientHistory?: { age: number; bmi: number; gender: string };
  executionTrace?: AgentProgressEvent[];
  /** "demo" results are synthetic examples and must render unmistakably marked. */
  source?: "live" | "demo";
}

const TRIAGE_FROM_SEVERITY: Record<DiagnosisResult["severity"], string> = {
  critical: "ESI-1",
  high: "ESI-2",
  moderate: "ESI-3",
  low: "ESI-4",
};

const severityConfig = {
  critical: {
    color: "#DC2626",
    bg: "#FEF2F2",
    label: "Critical",
    icon: AlertTriangle,
  },
  high: {
    color: "#F59E0B",
    bg: "#FFFBEB",
    label: "High",
    icon: AlertCircle,
  },
  moderate: {
    color: "#F59E0B",
    bg: "#FFFBEB",
    label: "Moderate",
    icon: Info,
  },
  low: {
    color: "#10B981",
    bg: "#ECFDF5",
    label: "Low",
    icon: CheckCircle,
  },
};

export function SeverityBadge({ severity }: { severity: keyof typeof severityConfig }) {
  const config = severityConfig[severity];
  const Icon = config.icon;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold uppercase tracking-wide",
        "animate-pulse-severity"
      )}
      style={{ 
        backgroundColor: config.bg, 
        color: config.color 
      }}
    >
      <Icon size={12} />
      {config.label}
    </span>
  );
}

export function ConfidenceChart({ data }: { data: DiagnosisResult[] }) {
  const chartData = data.map((d) => ({
    name: d.condition,
    confidence: Math.round(d.confidence * 100),
    severity: d.severity,
  }));

  const colors = {
    critical: "#DC2626",
    high: "#F59E0B",
    moderate: "#F59E0B",
    low: "#10B981",
  };

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} layout="vertical" margin={{ left: 20, right: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis type="number" domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
          <YAxis 
            dataKey="name" 
            type="category" 
            width={120} 
            tick={{ fontSize: 12 }}
          />
          <Tooltip 
            contentStyle={{
              backgroundColor: "white",
              border: "1px solid #E5E7EB",
              borderRadius: "8px",
            }}
          />
          <Bar dataKey="confidence" radius={[0, 4, 4, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={colors[entry.severity as keyof typeof colors]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function DiagnosisResults({
  results,
  isLoading,
  triage,
  sourceText = "",
  patientHistory,
  executionTrace = [],
  source = "live",
}: DiagnosisResultsProps) {
  const { persona } = usePersona();
  const [reportLoading, setReportLoading] = useState(false);
  const [reportError, setReportError] = useState<string | null>(null);

  if (isLoading) {
    return <LoadingSkeleton />;
  }

  if (!results || results.length === 0) {
    return null;
  }

  const primaryResult = results[0];
  const severity = primaryResult.severity;
  const isDemo = source === "demo";
  // An escalation signal leads the page: the crisis card renders before any
  // narrative content, per the action-first escalation requirement.
  const escalate = Boolean(primaryResult.doctorAlert) || severity === "critical";
  const clinician = persona === "clinician";
  const narrative = clinician
    ? primaryResult.clinicalExplanation || primaryResult.description
    : primaryResult.patientExplanation || primaryResult.description;
  const breakdown = primaryResult.confidenceBreakdown || {};

  const handleDownloadReport = async () => {
    setReportLoading(true);
    setReportError(null);
    try {
      await downloadReport({
        symptom_input: sourceText,
        age: patientHistory?.age,
        bmi: patientHistory?.bmi,
        gender: patientHistory?.gender,
        diagnosis: results.map((item) => ({
          condition: item.condition,
          confidence: item.confidence,
          severity: item.severity,
          icd10_code: item.icd10,
          rationale: item.rationale,
        })),
        explanation: primaryResult.clinicalExplanation,
        patient_explanation: primaryResult.patientExplanation,
        recommendations: primaryResult.recommendations,
        severity,
        doctor_alert: primaryResult.doctorAlert,
        red_flags: primaryResult.redFlags,
        confidence: { breakdown },
        triage,
        execution_trace: executionTrace,
        disclaimer: "AegisMed is clinical decision support and does not replace independent clinical judgment.",
      });
    } catch (error) {
      setReportError(error instanceof Error ? error.message : "Unable to generate report");
    } finally {
      setReportLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
      data-persona-view={persona}
    >
      {/* Crisis card — action-first escalation, leads the page */}
      {escalate && (
        <div
          data-testid="crisis-card"
          className="p-6 rounded-2xl bg-red-600 text-white shadow-lg space-y-4"
        >
          <div className="flex items-center gap-3">
            <AlertTriangle size={24} />
            <h2 className="text-xl font-bold">Seek emergency care now</h2>
          </div>
          <p className="text-red-50 text-sm">
            This assessment includes signs that may need immediate medical
            attention. Do not wait for online advice — call emergency services
            or go to the nearest emergency room now.
          </p>
          <div className="flex flex-wrap gap-3">
            <a
              href={`tel:${EMERGENCY_NUMBER}`}
              data-testid="crisis-call"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-white text-red-700 font-bold text-sm hover:bg-red-50 transition-colors"
            >
              <Phone size={16} />
              Call {EMERGENCY_NUMBER}
            </a>
            <a
              href={`sms:${EMERGENCY_NUMBER}`}
              data-testid="crisis-sms"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl border border-white/70 text-white font-bold text-sm hover:bg-red-700 transition-colors"
            >
              <MessageSquare size={16} />
              Text {EMERGENCY_NUMBER}
            </a>
          </div>
        </div>
      )}

      {/* Demo-mode banner: a synthetic example must never look like a live analysis */}
      {isDemo && (
        <div
          data-testid="demo-banner"
          className="flex items-center gap-2 p-3 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800"
        >
          <FlaskConical size={16} className="text-amber-600 dark:text-amber-400" />
          <p className="text-sm font-medium text-amber-800 dark:text-amber-300">
            Demo Mode — the content below is a synthetic example, not an
            analysis of you.
          </p>
        </div>
      )}

      <div className="flex flex-wrap items-center justify-between gap-3">
        <span className="text-sm text-neutral-500 dark:text-neutral-400">
          {clinician ? "Clinician consultation report" : "Save your assessment"}
        </span>
        <button
          type="button"
          onClick={handleDownloadReport}
          disabled={reportLoading}
          className="inline-flex items-center gap-2 rounded-lg bg-primary-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-primary-700 disabled:cursor-wait disabled:opacity-60"
        >
          {reportLoading ? <Loader2 size={16} className="animate-spin" /> : <Download size={16} />}
          {reportLoading ? "Preparing PDF…" : "Download Report"}
        </button>
        {reportError && (
          <p role="alert" className="basis-full text-sm text-red-600 dark:text-red-400">{reportError}</p>
        )}
      </div>

      {/* Main Result Card */}
      <div className="p-6 rounded-2xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 shadow-lg">
        <div className="flex items-start justify-between gap-4 mb-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Activity className="text-primary-600 dark:text-primary-400" size={24} />
              <span className="text-sm text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
                {clinician ? "Leading differential" : "What this may be"}
              </span>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-2xl font-bold text-neutral-900 dark:text-white">
                {primaryResult.condition}
              </h2>
              {clinician && primaryResult.icd10 && (
                <span className="px-2 py-0.5 rounded-md text-xs font-mono bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-300">
                  {primaryResult.icd10}
                </span>
              )}
              {isDemo && (
                <span
                  data-testid="demo-marker"
                  className="px-2 py-0.5 rounded-md text-[11px] font-bold uppercase tracking-wide bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300"
                >
                  Demo · synthetic
                </span>
              )}
            </div>
          </div>
          <div className="flex flex-col items-end gap-2">
            <SeverityBadge severity={severity as keyof typeof severityConfig} />
            {clinician && (
              <span
                className="px-2 py-0.5 rounded-md text-[11px] font-semibold tracking-wide bg-primary-50 dark:bg-primary-950 text-primary-700 dark:text-primary-300"
                title="Mapped from the assessed severity, not a bedside ESI assignment"
              >
                {TRIAGE_FROM_SEVERITY[severity]} · mapped
              </span>
            )}
          </div>
        </div>

        <p className="text-neutral-600 dark:text-neutral-300">
          {narrative}
        </p>
        {clinician && primaryResult.doctorAlert && (
          <p className="mt-3 text-sm font-medium text-red-700 dark:text-red-300">
            Physician review flagged for this result.
          </p>
        )}

        {/* Confidence Score */}
        <div className="mt-6 p-4 rounded-xl bg-neutral-50 dark:bg-neutral-800">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
              Confidence
            </span>
            <span className="text-lg font-bold text-primary-600 dark:text-primary-400">
              {Math.round(primaryResult.confidence * 100)}%
            </span>
          </div>
          <div className="h-2 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${primaryResult.confidence * 100}%` }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="h-full bg-primary-500 rounded-full"
            />
          </div>
        </div>
      </div>

      {/* Confidence Chart */}
      <div className="p-6 rounded-2xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-4">
          {clinician ? "Differential confidence" : "Other possibilities"}
        </h3>
        <ConfidenceChart data={results} />
        {clinician && (
          <ul className="mt-4 divide-y divide-neutral-100 dark:divide-neutral-800">
            {results.map((item) => (
              <li key={item.condition} className="py-3">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-sm font-semibold text-neutral-900 dark:text-white">
                    {item.condition}
                  </span>
                  {item.icd10 && (
                    <span className="px-1.5 py-0.5 rounded text-[11px] font-mono bg-neutral-100 dark:bg-neutral-800 text-neutral-500">
                      {item.icd10}
                    </span>
                  )}
                  <span className="ml-auto text-sm tabular-nums text-neutral-500">
                    {Math.round(item.confidence * 100)}%
                  </span>
                </div>
                {item.rationale && (
                  <p className="mt-1 text-sm text-neutral-600 dark:text-neutral-400">
                    {item.rationale}
                  </p>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>

      {clinician && (Object.keys(breakdown).length > 0 || triage) && (
        <div className="p-6 rounded-2xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800">
          <div className="flex items-center gap-2 mb-4">
            <FlaskConical className="text-primary-600 dark:text-primary-400" size={20} />
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-white">
              Agent agreement
            </h3>
          </div>
          {triage && (
            <p className="mb-3 text-sm text-neutral-600 dark:text-neutral-300">
              DEMAT entropy {triage.entropy_bits.toFixed(2)} bits
              {triage.converged ? " · interrogation converged" : ""}
            </p>
          )}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {Object.entries(breakdown).map(([agent, score]) => (
              <div key={agent} className="rounded-xl bg-neutral-50 dark:bg-neutral-800 p-3">
                <p className="text-[11px] uppercase tracking-wide text-neutral-500">{agent}</p>
                <p className="text-lg font-semibold text-neutral-900 dark:text-white tabular-nums">
                  {Math.round(Number(score) * 100)}%
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      <div className="p-6 rounded-2xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800">
        <div className="flex items-center gap-2 mb-4">
          <FileText className="text-primary-600 dark:text-primary-400" size={20} />
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-white">
            {clinician ? "Recommended actions" : "What to do next"}
          </h3>
        </div>
        <ul className="space-y-3">
          {primaryResult.recommendations.map((rec, i) => (
            <motion.li
              key={i}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              className="flex items-start gap-3 text-neutral-600 dark:text-neutral-300"
            >
              <CheckCircle size={18} className="text-success-500 mt-0.5 flex-shrink-0" />
              {rec}
            </motion.li>
          ))}
        </ul>
      </div>

      {/* Red Flags */}
      {primaryResult.redFlags.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-6 rounded-2xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800"
        >
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="text-red-600 dark:text-red-400" size={20} />
            <h3 className="text-lg font-semibold text-red-900 dark:text-red-200">
              {clinician ? "Red flags" : "Get help right away if you notice"}
            </h3>
          </div>
          {clinician ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left text-red-900 dark:text-red-100">
                <thead>
                  <tr className="border-b border-red-200 dark:border-red-800">
                    <th className="py-2 pr-3 font-semibold">Finding</th>
                    <th className="py-2 font-semibold">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {primaryResult.redFlags.map((flag) => (
                    <tr key={flag} className="border-b border-red-100 dark:border-red-900/40">
                      <td className="py-2 pr-3">{flag}</td>
                      <td className="py-2">Urgent clinical review</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
          <ul className="space-y-3" data-testid="red-flag-list">
            {primaryResult.redFlags.map((flag, i) => (
              <li key={i} className="flex items-start gap-3 text-red-800 dark:text-red-200">
                <AlertCircle size={18} className="text-red-500 mt-0.5 flex-shrink-0" />
                {flag}
              </li>
            ))}
          </ul>
          )}
        </motion.div>
      )}

      {/* Disclaimer */}
      <div className="p-4 rounded-xl bg-neutral-50 dark:bg-neutral-800 text-center">
        <p className="text-sm text-neutral-500 dark:text-neutral-400">
          This AI-generated analysis is for informational purposes only. 
          Please consult a healthcare professional for proper diagnosis and treatment.
        </p>
      </div>
    </motion.div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="space-y-6">
      {/* Main Card Skeleton */}
      <div className="p-6 rounded-2xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800">
        <div className="flex items-start justify-between gap-4 mb-4">
          <div className="space-y-2">
            <div className="skeleton h-4 w-24 rounded" />
            <div className="skeleton h-8 w-48 rounded" />
          </div>
          <div className="skeleton h-8 w-20 rounded-full" />
        </div>
        <div className="space-y-2">
          <div className="skeleton h-4 w-full rounded" />
          <div className="skeleton h-4 w-3/4 rounded" />
        </div>
        <div className="mt-6 p-4 rounded-xl bg-neutral-50 dark:bg-neutral-800">
          <div className="skeleton h-6 w-32 rounded" />
        </div>
      </div>

      {/* Chart Skeleton */}
      <div className="p-6 rounded-2xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800">
        <div className="skeleton h-6 w-40 rounded mb-4" />
        <div className="skeleton h-64 w-full rounded" />
      </div>

      {/* Recommendations Skeleton */}
      <div className="p-6 rounded-2xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800">
        <div className="skeleton h-6 w-40 rounded mb-4" />
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="skeleton h-5 w-full rounded" />
          ))}
        </div>
      </div>
    </div>
  );
}