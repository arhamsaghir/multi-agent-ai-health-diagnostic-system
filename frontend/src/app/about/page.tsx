import { Thermometer, Brain, Eye, MessageSquare, Database, Shield } from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "NLP Agent",
    description: "Extracts symptoms from free-text patient descriptions using pattern matching and NLP.",
  },
  {
    icon: Eye,
    title: "Vision Agent",
    description: "Analyzes medical images (chest X-rays) for 15 disease categories using deep learning.",
  },
  {
    icon: Database,
    title: "RAG Agent",
    description: "Retrieves relevant medical knowledge from evidence-based clinical guidelines.",
  },
  {
    icon: MessageSquare,
    title: "Synthesis Agent",
    description: "Generates comprehensive diagnostic reports with confidence scores and recommendations.",
  },
  {
    icon: Shield,
    title: "Safety First",
    description: "Priority keyword matching ensures critical conditions are always identified.",
  },
];

export default function AboutPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-600 text-white mb-4">
          <Thermometer size={32} />
        </div>
        <h1 className="text-3xl font-bold text-neutral-900 dark:text-white">
          AI Health Diagnostic System
        </h1>
        <p className="mt-2 text-neutral-600 dark:text-neutral-400">
          Multi-Agent Architecture for Healthcare Diagnostics
        </p>
      </div>

      {/* Tech Stack */}
      <div className="p-6 rounded-2xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800">
        <h2 className="text-xl font-semibold text-neutral-900 dark:text-white mb-4">
          Technology Stack
        </h2>
        <div className="flex flex-wrap gap-2">
          {["Next.js 14", "TypeScript", "Tailwind CSS", "Framer Motion", "Recharts", "FastAPI"].map((tech) => (
            <span 
              key={tech} 
              className="px-3 py-1 text-sm rounded-full bg-primary-50 dark:bg-primary-950 text-primary-700 dark:text-primary-300"
            >
              {tech}
            </span>
          ))}
        </div>
      </div>

      {/* Features */}
      <div className="p-6 rounded-2xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800">
        <h2 className="text-xl font-semibold text-neutral-900 dark:text-white mb-6">
          System Architecture
        </h2>
        <div className="grid gap-6 md:grid-cols-2">
          {features.map((feature, i) => {
            const Icon = feature.icon;
            return (
              <div key={i} className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 rounded-lg bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
                    <Icon className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                  </div>
                </div>
                <div>
                  <h3 className="font-semibold text-neutral-900 dark:text-white">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400">
                    {feature.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Disclaimer */}
      <div className="p-4 rounded-xl bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800">
        <p className="text-sm text-amber-800 dark:text-amber-200">
          <strong>Disclaimer:</strong> This system is for research and educational purposes only. 
          It is not a medical device and should not be used for actual clinical diagnosis. 
          Always consult healthcare professionals for medical advice.
        </p>
      </div>
    </div>
  );
}