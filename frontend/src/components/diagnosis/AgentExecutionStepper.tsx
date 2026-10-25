"use client";

import { motion, AnimatePresence } from "framer-motion";
import {
  Brain,
  Eye,
  Database,
  TrendingUp,
  Sparkles,
  Activity,
  Check,
  X,
  Loader2,
  Minus,
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { AgentProgressEvent } from "@/lib/api";

type StepStatus = "pending" | "running" | "done" | "failed" | "skipped";

interface StepState {
  node: string;
  agent: string;
  model: string;
  status: StepStatus;
  elapsedMs?: number;
  summary?: string;
}

const STEP_ORDER: Array<{ node: string; agent: string; model: string; icon: typeof Brain }> = [
  { node: "triage", agent: "DEMAT Active Triage", model: "Entropy Minimization", icon: Activity },
  { node: "symptoms", agent: "NLP Agent", model: "BioBERT / Clinical NLP", icon: Brain },
  { node: "image", agent: "Vision Agent", model: "ResNet / ChestX-ray14", icon: Eye },
  { node: "knowledge", agent: "RAG Agent", model: "FAISS Vector Store", icon: Database },
  { node: "risk", agent: "Prediction Agent", model: "GradientBoosting / XGBoost", icon: TrendingUp },
  { node: "synthesis", agent: "Synthesis Agent", model: "LLM Synthesis", icon: Sparkles },
];

const AGENT_BY_NODE: Record<string, (typeof STEP_ORDER)[number]> = Object.fromEntries(
  STEP_ORDER.map((s) => [s.node, s])
);

interface AgentExecutionStepperProps {
  events: AgentProgressEvent[];
  running: boolean;
}

function deriveSteps(events: AgentProgressEvent[]): StepState[] {
  const planned = events.find((e) => e.type === "planned");
  const plannedTasks = planned?.tasks ?? null;

  return STEP_ORDER.map((meta) => {
    const agentEvents = events.filter((e) => e.type === "agent" && e.node === meta.node);
    const last = agentEvents[agentEvents.length - 1];

    let status: StepStatus = "pending";
    if (meta.node === "triage") {
      // Triage runs before the orchestrator pipeline (or is emitted by refine-stream)
      status = last?.status === "completed" ? "done" : last?.status === "started" ? "running" : "pending";
    } else if (last) {
      status =
        last.status === "started" ? "running"
        : last.status === "completed" ? "done"
        : "failed";
    } else if (plannedTasks && !plannedTasks.includes(meta.node)) {
      status = "skipped";
    }

    return {
      node: meta.node,
      agent: meta.agent,
      model: meta.model,
      status,
      elapsedMs: last?.elapsed_ms,
      summary: last?.summary,
    };
  });
}

function StatusIcon({ status }: { status: StepStatus }) {
  switch (status) {
    case "running":
      return <Loader2 size={16} className="animate-spin text-primary-600 dark:text-primary-400" />;
    case "done":
      return <Check size={16} className="text-emerald-600 dark:text-emerald-400" />;
    case "failed":
      return <X size={16} className="text-red-500" />;
    case "skipped":
      return <Minus size={16} className="text-neutral-400" />;
    default:
      return null;
  }
}

export function AgentExecutionStepper({ events, running }: AgentExecutionStepperProps) {
  const steps = deriveSteps(events);
  const doneCount = steps.filter((s) => s.status === "done" || s.status === "failed").length;
  const activeCount = steps.filter((s) => s.status !== "skipped").length;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      className="p-6 rounded-2xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 shadow-sm space-y-5"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity size={18} className="text-primary-600 dark:text-primary-400 animate-pulse" />
          <h3 className="font-bold text-neutral-900 dark:text-white">
            Multi-Agent Execution
          </h3>
        </div>
        <span className="text-xs font-medium text-neutral-500 dark:text-neutral-400 tabular-nums">
          {doneCount}/{activeCount} agents
        </span>
      </div>

      {/* Progress bar */}
      <div className="h-1.5 rounded-full bg-neutral-100 dark:bg-neutral-800 overflow-hidden">
        <motion.div
          className="h-full rounded-full bg-gradient-to-r from-primary-500 to-emerald-500"
          animate={{ width: `${activeCount ? (doneCount / activeCount) * 100 : 0}%` }}
          transition={{ duration: 0.4, ease: "easeOut" }}
        />
      </div>

      <div className="space-y-1">
        <AnimatePresence>
          {steps.map((step) => {
            const Icon = AGENT_BY_NODE[step.node]?.icon ?? Brain;
            return (
              <motion.div
                key={step.node}
                layout
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-xl transition-colors",
                  step.status === "running" && "bg-primary-50 dark:bg-primary-950/40 border border-primary-200 dark:border-primary-800",
                  step.status === "done" && "bg-emerald-50/60 dark:bg-emerald-950/20",
                  step.status === "skipped" && "opacity-45"
                )}
              >
                <div
                  className={cn(
                    "w-8 h-8 rounded-lg flex items-center justify-center shrink-0 transition-colors",
                    step.status === "running" && "bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-300",
                    step.status === "done" && "bg-emerald-100 dark:bg-emerald-900/50 text-emerald-600 dark:text-emerald-400",
                    step.status === "failed" && "bg-red-100 dark:bg-red-900/50 text-red-500",
                    (step.status === "pending" || step.status === "skipped") &&
                      "bg-neutral-100 dark:bg-neutral-800 text-neutral-400"
                  )}
                >
                  <Icon size={16} />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-neutral-900 dark:text-white truncate">
                      {step.agent}
                    </span>
                    <span className="text-[10px] font-mono text-neutral-400 dark:text-neutral-500 truncate hidden sm:inline">
                      {step.model}
                    </span>
                  </div>
                  {step.summary && step.status === "done" && (
                    <p className="text-xs text-neutral-500 dark:text-neutral-400 truncate mt-0.5">
                      {step.summary}
                    </p>
                  )}
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  {step.elapsedMs !== undefined && step.status === "done" && (
                    <span className="text-[10px] font-mono text-neutral-400 tabular-nums">
                      {(step.elapsedMs / 1000).toFixed(1)}s
                    </span>
                  )}
                  <StatusIcon status={step.status} />
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      {running && (
        <p className="text-xs text-center text-neutral-400 dark:text-neutral-500">
          Agents are analyzing your case… results appear automatically.
        </p>
      )}
    </motion.div>
  );
}
