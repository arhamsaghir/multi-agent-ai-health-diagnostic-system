"use client";

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
  FlaskConical
} from "lucide-react";
import { cn } from "@/lib/utils";

export interface DiagnosisResult {
  condition: string;
  confidence: number;
  severity: "critical" | "high" | "moderate" | "low";
  description: string;
  recommendations: string[];
  redFlags: string[];
}

interface DiagnosisResultsProps {
  results: DiagnosisResult[];
  isLoading?: boolean;
}

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

export function DiagnosisResults({ results, isLoading }: DiagnosisResultsProps) {
  if (isLoading) {
    return <LoadingSkeleton />;
  }

  if (!results || results.length === 0) {
    return null;
  }

  const primaryResult = results[0];
  const severity = primaryResult?.severity || "low";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Main Result Card */}
      <div className="p-6 rounded-2xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 shadow-lg">
        <div className="flex items-start justify-between gap-4 mb-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Activity className="text-primary-600 dark:text-primary-400" size={24} />
              <span className="text-sm text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
                Primary Diagnosis
              </span>
            </div>
            <h2 className="text-2xl font-bold text-neutral-900 dark:text-white">
              {primaryResult.condition}
            </h2>
          </div>
          <SeverityBadge severity={severity as keyof typeof severityConfig} />
        </div>

        <p className="text-neutral-600 dark:text-neutral-300">
          {primaryResult.description}
        </p>

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
          Differential Diagnoses
        </h3>
        <ConfidenceChart data={results} />
      </div>

      {/* Recommendations */}
      <div className="p-6 rounded-2xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800">
        <div className="flex items-center gap-2 mb-4">
          <FileText className="text-primary-600 dark:text-primary-400" size={20} />
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-white">
            Recommendations
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
              Red Flags -Seek Immediate Care
            </h3>
          </div>
          <ul className="space-y-3">
            {primaryResult.redFlags.map((flag, i) => (
              <li key={i} className="flex items-start gap-3 text-red-800 dark:text-red-200">
                <AlertCircle size={18} className="text-red-500 mt-0.5 flex-shrink-0" />
                {flag}
              </li>
            ))}
          </ul>
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