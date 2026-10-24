"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  Stethoscope,
  Scan,
  MessageSquare,
  History,
  Activity,
  Brain,
  Eye,
  Database,
  TrendingUp,
  Sparkles,
  ArrowRight,
  ShieldAlert,
  CheckCircle2,
  FileCheck
} from "lucide-react";

const agents = [
  {
    name: "NLP Agent",
    model: "BioBERT / Clinical NLP",
    role: "Extracts symptoms, duration, and clinical severity from natural language narratives.",
    icon: Brain,
    color: "from-blue-500 to-indigo-600",
    border: "border-blue-200 dark:border-blue-900/50",
    bg: "bg-blue-50/50 dark:bg-blue-950/20",
  },
  {
    name: "Vision Agent",
    model: "ResNet-50 (NIH ChestX-ray14)",
    role: "Deep learning scan classifier detecting 15 pulmonary and cardiac pathologies.",
    icon: Eye,
    color: "from-purple-500 to-pink-600",
    border: "border-purple-200 dark:border-purple-900/50",
    bg: "bg-purple-50/50 dark:bg-purple-950/20",
  },
  {
    name: "RAG Agent",
    model: "FAISS Vector Store",
    role: "Evidence-based clinical guideline retrieval for differential validation.",
    icon: Database,
    color: "from-emerald-500 to-teal-600",
    border: "border-emerald-200 dark:border-emerald-900/50",
    bg: "bg-emerald-50/50 dark:bg-emerald-950/20",
  },
  {
    name: "Prediction Agent",
    model: "GradientBoosting / XGBoost",
    role: "Calculates disease risk factors from demographics, vitals, and family history.",
    icon: TrendingUp,
    color: "from-amber-500 to-orange-600",
    border: "border-amber-200 dark:border-amber-900/50",
    bg: "bg-amber-50/50 dark:bg-amber-950/20",
  },
  {
    name: "Synthesis Agent",
    model: "LangGraph Orchestrator",
    role: "Aggregates multi-agent outputs, enforces emergency rules, and generates final differentials.",
    icon: Sparkles,
    color: "from-rose-500 to-red-600",
    border: "border-rose-200 dark:border-rose-900/50",
    bg: "bg-rose-50/50 dark:bg-rose-950/20",
  },
];

const capabilities = [
  {
    title: "Symptom Diagnosis",
    description: "Enter free-text complaints and patient history to run full multi-agent differential diagnosis.",
    href: "/diagnosis",
    icon: Stethoscope,
    badge: "Primary Pipeline",
    buttonText: "Check Symptoms",
  },
  {
    title: "Chest X-Ray Analysis",
    description: "Upload DICOM/PNG/JPEG thoracic radiographs to obtain ResNet-50 pathology heatmaps and probabilities.",
    href: "/vision",
    icon: Scan,
    badge: "Medical Imaging",
    buttonText: "Upload Scan",
  },
  {
    title: "Clinical Chatbot",
    description: "Ask medical questions with automatic safety guardrails, escalation triggers, and conversational context.",
    href: "/chat",
    icon: MessageSquare,
    badge: "Evidence-Based Q&A",
    buttonText: "Start Consultation",
  },
  {
    title: "Diagnostic History",
    description: "Review and audit past patient sessions, risk confidence scores, and logged diagnoses stored in SQLite.",
    href: "/history",
    icon: History,
    badge: "Session Store",
    buttonText: "View History",
  },
];

export default function Home() {
  return (
    <div className="max-w-6xl mx-auto space-y-8 sm:space-y-12 pb-12">
      {/* Hero Section */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden rounded-3xl p-6 sm:p-8 lg:p-12 bg-gradient-to-br from-primary-900 via-primary-800 to-slate-900 text-white shadow-xl"
      >
        <div className="relative z-10 max-w-3xl space-y-4 sm:space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-xs font-semibold tracking-wide uppercase">
            <Activity size={14} className="text-emerald-400 animate-pulse" />
            <span>Autonomous Multi-Agent AI System</span>
          </div>

          <h1 className="text-2xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight leading-tight">
            Comprehensive Clinical Intelligence & Diagnostics
          </h1>

          <p className="text-sm sm:text-base lg:text-lg text-primary-100/90 leading-relaxed">
            A cooperative multi-agent healthcare platform combining NLP symptom extraction,
            ResNet-50 medical imaging, FAISS vector search, and XGBoost clinical risk assessment.
          </p>

          <div className="flex flex-wrap items-center gap-3 sm:gap-4 pt-2">
            <Link
              href="/diagnosis"
              className="inline-flex items-center justify-center gap-2 px-5 sm:px-6 py-3 sm:py-3.5 bg-white text-primary-900 hover:bg-primary-50 rounded-xl font-bold shadow-lg transition-all transform hover:-translate-y-0.5 text-sm sm:text-base"
            >
              <Stethoscope size={18} />
              <span>Start Symptom Check</span>
              <ArrowRight size={16} />
            </Link>

            <Link
              href="/vision"
              className="inline-flex items-center justify-center gap-2 px-5 sm:px-6 py-3 sm:py-3.5 bg-primary-700/60 hover:bg-primary-700 border border-white/20 text-white rounded-xl font-semibold backdrop-blur-md transition-all text-sm sm:text-base"
            >
              <Scan size={18} />
              <span>Analyze X-Ray Scan</span>
            </Link>

            <Link
              href="/chat"
              className="inline-flex items-center justify-center gap-2 px-5 sm:px-6 py-3 sm:py-3.5 bg-slate-800/80 hover:bg-slate-800 border border-white/10 text-white rounded-xl font-semibold backdrop-blur-md transition-all text-sm sm:text-base"
            >
              <MessageSquare size={18} />
              <span>Clinical Assistant</span>
            </Link>
          </div>
        </div>

        {/* Decorative Grid Glow */}
        <div className="absolute -right-20 -bottom-20 w-96 h-96 bg-primary-500/20 rounded-full blur-3xl pointer-events-none" />
      </motion.section>

      {/* Main Capability Cards */}
      <section className="space-y-4">
        <div>
          <h2 className="text-xl lg:text-2xl font-bold text-neutral-900 dark:text-white">
            Clinical Diagnostic Modules
          </h2>
          <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
            Choose a specialist module to begin assessment or audit historical records
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
          {capabilities.map((cap, idx) => {
            const Icon = cap.icon;
            return (
              <motion.div
                key={cap.title}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.08 }}
                className="group p-5 sm:p-6 rounded-2xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 hover:border-primary-400 dark:hover:border-primary-600 shadow-sm hover:shadow-md transition-all flex flex-col justify-between"
              >
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="w-12 h-12 rounded-xl bg-primary-50 dark:bg-primary-950/60 text-primary-600 dark:text-primary-400 flex items-center justify-center font-bold">
                      <Icon size={24} />
                    </div>
                    <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-300">
                      {cap.badge}
                    </span>
                  </div>

                  <div>
                    <h3 className="text-lg font-bold text-neutral-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                      {cap.title}
                    </h3>
                    <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1.5 leading-relaxed">
                      {cap.description}
                    </p>
                  </div>
                </div>

                <div className="pt-6">
                  <Link
                    href={cap.href}
                    className="inline-flex items-center gap-2 text-sm font-semibold text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 group-hover:translate-x-1 transition-all"
                  >
                    <span>{cap.buttonText}</span>
                    <ArrowRight size={16} />
                  </Link>
                </div>
              </motion.div>
            );
          })}
        </div>
      </section>

      {/* Multi-Agent Architecture Overview */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl lg:text-2xl font-bold text-neutral-900 dark:text-white">
              Multi-Agent Architecture
            </h2>
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
              Five specialized agents coordinated via LangGraph state machine
            </p>
          </div>
          <span className="hidden sm:inline-flex items-center gap-1.5 text-xs font-medium text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/50 px-3 py-1.5 rounded-full border border-emerald-200 dark:border-emerald-800">
            <CheckCircle2 size={14} />
            All Subsystems Active
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {agents.map((agent, idx) => {
            const Icon = agent.icon;
            return (
              <motion.div
                key={agent.name}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.15 + idx * 0.05 }}
                className={`p-5 rounded-2xl ${agent.bg} border ${agent.border} flex flex-col justify-between space-y-3`}
              >
                <div className="space-y-2">
                  <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${agent.color} text-white flex items-center justify-center shadow-md`}>
                    <Icon size={20} />
                  </div>
                  <div>
                    <h4 className="font-bold text-sm text-neutral-900 dark:text-white">
                      {agent.name}
                    </h4>
                    <span className="text-[11px] font-mono text-neutral-500 dark:text-neutral-400 block mt-0.5">
                      {agent.model}
                    </span>
                  </div>
                </div>

                <p className="text-xs text-neutral-600 dark:text-neutral-300 leading-relaxed">
                  {agent.role}
                </p>
              </motion.div>
            );
          })}
        </div>
      </section>

      {/* Clinical Safety & Disclaimer Notice */}
      <section className="p-6 rounded-2xl bg-amber-50/70 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800/60 flex items-start gap-4">
        <ShieldAlert size={24} className="text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
        <div className="space-y-1 text-xs text-amber-800 dark:text-amber-200 leading-relaxed">
          <p className="font-bold text-sm text-amber-900 dark:text-amber-100">
            Clinical Safety Advisory & Disclaimer
          </p>
          <p>
            This system is an academic decision-support research prototype. It does not replace professional medical diagnosis, laboratory testing, or clinical judgment. For life-threatening emergencies, immediate physical hospitalization or contact with national emergency services (112 / 108) is required.
          </p>
        </div>
      </section>
    </div>
  );
}