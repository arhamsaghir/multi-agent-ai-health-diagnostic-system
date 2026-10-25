import { DiagnosisResult } from "@/components/diagnosis/DiagnosisResults";

export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface PatientHistory {
  age: number;
  bmi: number;
  gender: string;
  familyHistory: string[];
}

export interface AnalysisResult {
  disease: string;
  confidence: number;
}

export interface FollowUpQuestion {
  id: string;
  question: string;
  type: "choice" | "yes_no" | "text";
  options?: string[];
  category?: string;
  rationale?: string;
  expected_information_gain?: number;
}

export interface TriageCandidate {
  disease: string;
  name: string;
  icd10: string;
  probability: number;
}

export interface TriageInfo {
  session_id: string;
  entropy_bits: number;
  entropy_reduction: number;
  round_count: number;
  converged: boolean;
  top_candidates: TriageCandidate[];
  asked_questions: string[];
}

export interface FollowUpResult {
  questions: FollowUpQuestion[];
  has_more: boolean;
  session_id: string;
  triage?: TriageInfo;
}

export interface VisionResult {
  predictions: AnalysisResult[];
  primary_finding: string;
  severity: "critical" | "high" | "moderate" | "low";
  recommendation: string;
  heatmap?: string;
  heatmap_class?: string;
  heatmap_confidence?: number;
}

export async function analyzeImage(file: File): Promise<VisionResult> {
  const formData = new FormData();
  formData.append("image", file);

  const response = await fetch(`${API_BASE}/api/vision/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Vision analysis failed with status ${response.status}`);
  }

  const data = await response.json();
  const findings: Array<{ condition?: string; disease?: string; confidence?: number; severity?: string }> =
    data.findings || [];

  const predictions: AnalysisResult[] = findings.map((f) => ({
    disease: f.condition || f.disease || "Unknown Finding",
    confidence: f.confidence ?? 0,
  }));

  const primaryFinding = predictions.length > 0 ? predictions[0].disease : "No Abnormality Detected";
  const rawSeverity = (findings[0]?.severity?.toLowerCase() || "low") as "critical" | "high" | "moderate" | "low";
  const validSeverities: Array<"critical" | "high" | "moderate" | "low"> = ["critical", "high", "moderate", "low"];
  const severity = validSeverities.includes(rawSeverity) ? rawSeverity : "moderate";

  let recommendation = "Image analysis shows no high-confidence abnormalities. Correlate with clinical examination.";
  if (predictions.length > 0 && predictions[0].confidence > 0.4) {
    recommendation = `Findings indicate potential ${primaryFinding} (${Math.round(predictions[0].confidence * 100)}% confidence). Clinical correlation and follow-up radiological confirmation are recommended.`;
  }

  return {
    predictions,
    primary_finding: primaryFinding,
    severity,
    recommendation,
    heatmap: data.heatmap,
    heatmap_class: data.heatmap_class,
    heatmap_confidence: data.heatmap_confidence,
  };
}

export async function diagnose(
  text: string,
  history: PatientHistory,
  demoMode: boolean = false
): Promise<DiagnosisResult[]> {
  if (demoMode) {
    return getDemoResults(text);
  }

  try {
    const response = await fetch(`${API_BASE}/api/diagnosis/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text,
        patient_history: {
          age: history.age,
          bmi: history.bmi,
          gender: history.gender,
          family_history: history.familyHistory,
        },
      }),
    });

    if (!response.ok) {
      throw new Error(`API returned status ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    return transformAPIResponse(data);
  } catch (error) {
    console.warn("Live API call failed, providing demo fallback:", error);
    return getDemoResults(text);
  }
}

export async function fetchFollowUpQuestions(
  text: string,
  history?: PatientHistory,
  previous?: Array<{ id: string; question: string; answer: string }>,
  sessionId?: string
): Promise<FollowUpResult> {
  const payload = {
    text,
    patient_history: history
      ? {
          age: history.age,
          bmi: history.bmi,
          gender: history.gender,
          family_history: history.familyHistory,
        }
      : undefined,
    previous_questions: previous,
    session_id: sessionId,
  };

  const response = await fetch(`${API_BASE}/api/diagnosis/follow-up`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Follow-up API error: ${response.statusText}`);
  }

  const data = await response.json();
  return {
    questions: data.questions || [],
    has_more: data.has_more ?? false,
    session_id: data.session_id || "",
    triage: data.triage,
  };
}

export async function refineDiagnosis(
  text: string,
  history: PatientHistory,
  answers: Array<{ id: string; question: string; answer: string }>,
  sessionId?: string
): Promise<{ results: DiagnosisResult[]; triage?: TriageInfo }> {
  const response = await fetch(`${API_BASE}/api/diagnosis/refine`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text,
      patient_history: {
        age: history.age,
        bmi: history.bmi,
        gender: history.gender,
        family_history: history.familyHistory,
      },
      follow_up_answers: answers,
      session_id: sessionId,
    }),
  });

  if (!response.ok) {
    throw new Error(`Refine API error: ${response.statusText}`);
  }

  const data = await response.json();
  return {
    results: transformAPIResponse(data),
    triage: data.triage,
  };
}

/* ------------------------------------------------------------------ */
/* Live execution streaming (SSE)                                      */
/* ------------------------------------------------------------------ */

export interface AgentProgressEvent {
  type: "run_started" | "planned" | "agent" | "result" | "error";
  run_id?: string;
  tasks?: string[];
  node?: string;
  agent?: string;
  model?: string;
  status?: "started" | "completed" | "failed";
  elapsed_ms?: number;
  summary?: string;
  ts?: number;
  data?: unknown;
  message?: string;
}

/** Parse an SSE byte stream, dispatching parsed event objects to onEvent. */
async function consumeSSE(
  response: Response,
  onEvent: (event: AgentProgressEvent) => void
): Promise<AgentProgressEvent | null> {
  if (!response.ok) {
    throw new Error(`Stream request failed with status ${response.status}`);
  }
  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("Stream not supported by this browser");
  }

  const decoder = new TextDecoder();
  let buffer = "";
  let resultEvent: AgentProgressEvent | null = null;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const frames = buffer.split("\n\n");
    buffer = frames.pop() ?? "";

    for (const frame of frames) {
      if (!frame.trim() || frame.startsWith(":")) continue;
      const dataLine = frame
        .split("\n")
        .map((l) => l.trim())
        .find((l) => l.startsWith("data:"));
      if (!dataLine) continue;
      try {
        const event = JSON.parse(dataLine.slice(5).trim()) as AgentProgressEvent;
        if (event.type === "error") {
          throw new Error(event.message || "Pipeline error");
        }
        if (event.type === "result") {
          resultEvent = event;
        } else {
          onEvent(event);
        }
      } catch (e) {
        if (e instanceof SyntaxError) continue;
        throw e;
      }
    }
  }
  return resultEvent;
}

/** Streamed variant of diagnose(): emits per-agent progress events, resolves with results. */
export async function streamDiagnosis(
  text: string,
  history: PatientHistory,
  onEvent: (event: AgentProgressEvent) => void
): Promise<{ results: DiagnosisResult[]; triage?: TriageInfo }> {
  const response = await fetch(`${API_BASE}/api/diagnosis/analyze-stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text,
      patient_history: {
        age: history.age,
        bmi: history.bmi,
        gender: history.gender,
        family_history: history.familyHistory,
      },
    }),
  });

  const resultEvent = await consumeSSE(response, onEvent);
  if (!resultEvent?.data) {
    throw new Error("Stream ended without a result payload");
  }
  const data = resultEvent.data as Record<string, unknown>;
  return { results: transformAPIResponse(data), triage: data.triage as TriageInfo | undefined };
}

/** Streamed variant of refineDiagnosis(): DEMAT arbitration event + agent progress. */
export async function streamRefineDiagnosis(
  text: string,
  history: PatientHistory,
  answers: Array<{ id: string; question: string; answer: string }>,
  onEvent: (event: AgentProgressEvent) => void,
  sessionId?: string
): Promise<{ results: DiagnosisResult[]; triage?: TriageInfo }> {
  const response = await fetch(`${API_BASE}/api/diagnosis/refine-stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text,
      patient_history: {
        age: history.age,
        bmi: history.bmi,
        gender: history.gender,
        family_history: history.familyHistory,
      },
      follow_up_answers: answers,
      session_id: sessionId,
    }),
  });

  const resultEvent = await consumeSSE(response, onEvent);
  if (!resultEvent?.data) {
    throw new Error("Stream ended without a result payload");
  }
  const data = resultEvent.data as Record<string, unknown>;
  return { results: transformAPIResponse(data), triage: data.triage as TriageInfo | undefined };
}

interface ApiDiagnosisEntry {
  severity?: string;
  confidence?: number;
  name?: string;
  condition?: string;
  description?: string;
  recommendations?: string[];
  redFlags?: string[];
  icd10_code?: string;
  icd10?: string;
  rationale?: string;
}

interface ApiDiagnosisPayload {
  diagnosis?: ApiDiagnosisEntry[];
  differential_diagnoses?: string[];
  recommendations?: string[];
  red_flags?: string[];
  severity?: string;
  patient_explanation?: string;
  explanation?: string;
  doctor_alert?: boolean;
  confidence?: { breakdown?: Record<string, number> };
}

type Severity = "critical" | "high" | "moderate" | "low";

function normalizeSeverity(value: unknown): Severity {
  const severities: Severity[] = ["critical", "high", "moderate", "low"];
  const lowered = typeof value === "string" ? value.toLowerCase() : "";
  return (severities as string[]).includes(lowered) ? (lowered as Severity) : "moderate";
}

function transformAPIResponse(data: ApiDiagnosisPayload): DiagnosisResult[] {
  const diagnosis = Array.isArray(data.diagnosis) && data.diagnosis.length > 0
    ? data.diagnosis
    : Array.isArray(data.differential_diagnoses) && data.differential_diagnoses.length > 0
      ? data.differential_diagnoses.map((name: string) => ({ name, confidence: 0.7, severity: data.severity || "moderate" }))
      : [];

  const baseRecommendations = Array.isArray(data.recommendations) ? data.recommendations : [];
  const baseRedFlags = Array.isArray(data.red_flags) ? data.red_flags : [];
  const patientExplanation = data.patient_explanation || data.explanation || "";
  const clinicalExplanation = data.explanation || data.patient_explanation || "";
  const generalExplanation = patientExplanation || clinicalExplanation;
  const breakdown =
    data.confidence && typeof data.confidence === "object" ? data.confidence.breakdown : undefined;
  const shared = {
    patientExplanation: patientExplanation || undefined,
    clinicalExplanation: clinicalExplanation || undefined,
    doctorAlert: Boolean(data.doctor_alert),
    confidenceBreakdown: breakdown,
  };

  if (diagnosis.length === 0) {
    return [{
      condition: "Clinical Evaluation Recommended",
      confidence: 0.6,
      severity: normalizeSeverity(data.severity),
      description: generalExplanation || "The multi-agent system analyzed the provided symptoms. Clinical follow-up is recommended.",
      recommendations: baseRecommendations.length > 0 ? baseRecommendations : ["Consult a licensed physician for comprehensive evaluation"],
      redFlags: baseRedFlags,
      ...shared,
    }];
  }

  return diagnosis.map((d: ApiDiagnosisEntry, idx: number) => {
    const rawSeverity = (d.severity?.toLowerCase() || data.severity?.toLowerCase() || "moderate");
    const validSeverities: Array<"critical" | "high" | "moderate" | "low"> = ["critical", "high", "moderate", "low"];
    const severity = validSeverities.includes(rawSeverity as Severity) ? (rawSeverity as Severity) : "moderate";

    return {
      condition: d.name || d.condition || `Condition ${idx + 1}`,
      confidence: typeof d.confidence === "number" ? Math.round(d.confidence * 100) / 100 : 0.75,
      severity,
      description: d.description || generalExplanation || "Differential diagnosis derived from reported symptoms and risk models.",
      recommendations: d.recommendations && d.recommendations.length > 0 ? d.recommendations : baseRecommendations,
      redFlags: d.redFlags && d.redFlags.length > 0 ? d.redFlags : baseRedFlags,
      icd10: d.icd10_code || d.icd10 || undefined,
      rationale: d.rationale || undefined,
      ...shared,
    };
  });
}

export interface ReportPayload {
  symptom_input?: string;
  age?: number;
  gender?: string;
  bmi?: number;
  diagnosis: Array<Record<string, unknown>>;
  explanation?: string;
  patient_explanation?: string;
  recommendations?: string[];
  severity?: string;
  doctor_alert?: boolean;
  differential_diagnoses?: string[];
  red_flags?: string[];
  confidence?: Record<string, unknown>;
  disclaimer?: string;
  triage?: TriageInfo;
  execution_trace?: AgentProgressEvent[];
}

export async function downloadReport(payload: ReportPayload): Promise<void> {
  const response = await fetch(`${API_BASE}/api/report/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `Report generation failed (${response.status})`);
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "aegismed-clinical-report.pdf";
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

export interface ChatMessageResult {
  reply: string;
  conversationId: string;
  safetyAlert: boolean;
  timestamp: Date;
}

export async function sendChatMessage(
  message: string,
  conversationId?: string
): Promise<ChatMessageResult> {
  const response = await fetch(`${API_BASE}/api/chat/message`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      conversation_id: conversationId || undefined,
    }),
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || `Chat request failed with status ${response.status}`);
  }

  const data = await response.json();
  return {
    reply: data.response || "No response received from clinical assistant.",
    conversationId: data.conversation_id,
    safetyAlert: Boolean(data.safety_alert),
    timestamp: data.timestamp ? new Date(data.timestamp * 1000) : new Date(),
  };
}

export function getDemoResults(text: string): DiagnosisResult[] {
  const textLower = text.toLowerCase();
  
  // Rule-based diagnosis logic for demo
  if (textLower.includes("chest pain") || textLower.includes("heart") || textLower.includes("short of breath")) {
    return [{
      condition: "Cardiovascular Disease",
      confidence: 0.85,
      severity: "high",
      description: "Your symptoms suggest potential cardiovascular involvement. Chest pain with shortness of breath should be evaluated by a cardiologist.",
      recommendations: [
        "Schedule an ECG test",
        "Monitor blood pressure regularly",
        "Avoid strenuous physical activity",
        "Consult a cardiologist within 24-48 hours",
      ],
      redFlags: [
        "Chest pain radiating to arm/jaw",
        "Shortness of breath at rest",
        "Dizziness or fainting",
      ],
    }];
  }
  
  if (textLower.includes("cough") || textLower.includes("fever") || textLower.includes("breathing")) {
    return [{
      condition: "Respiratory Infection",
      confidence: 0.78,
      severity: "moderate",
      description: "Your symptoms are consistent with a respiratory infection. Further evaluation may be needed.",
      recommendations: [
        "Rest and stay hydrated",
        "Monitor temperature",
        "Avoid cold environments",
        "Consult doctor if symptoms worsen",
      ],
      redFlags: [
        "High fever (>102°F)",
        "Difficulty breathing",
        "Chest pain",
      ],
    }];
  }
  
  if (textLower.includes("headache") || textLower.includes("dizz") || textLower.includes("light sensitivity")) {
    return [{
      condition: "Neurological Disorder",
      confidence: 0.72,
      severity: "low",
      description: "Your symptoms may indicate a neurological condition. Most headaches are benign but should be monitored.",
      recommendations: [
        "Rest in a quiet, dark room",
        "Stay hydrated",
        "Avoid screen time",
        "Consult doctor if persistent",
      ],
      redFlags: [
        "Sudden severe headache",
        "Confusion",
        "Speech difficulty",
      ],
    }];
  }
  
  if (textLower.includes("thirst") || textLower.includes("urinate") || textLower.includes("fatigue")) {
    return [{
      condition: "Type 2 Diabetes",
      confidence: 0.68,
      severity: "moderate",
      description: "Your symptoms suggest possible diabetes. Screening is recommended.",
      recommendations: [
        "Get fasting blood glucose test",
        "HbA1c test",
        "Follow up with primary care physician",
      ],
      redFlags: [],
    }];
  }
  
  // Default response
  return [{
    condition: "General Symptoms",
    confidence: 0.45,
    severity: "low",
    description: "Your symptoms require more information for accurate diagnosis. Please consult a healthcare provider.",
    recommendations: [
      "Rest and monitor symptoms",
      "Keep a symptom diary",
      "Consult a healthcare professional",
    ],
    redFlags: [],
  }];
}

export interface DiagnosisRecord {
  id: string;
  date: string;
  condition: string;
  severity: "critical" | "high" | "moderate" | "low";
  confidence: number;
  symptoms: string;
}

export const mockHistoryRecords: DiagnosisRecord[] = [
  {
    id: "1",
    date: "2024-01-15",
    condition: "Cardiovascular Disease",
    severity: "high",
    confidence: 0.85,
    symptoms: "Chest pain, shortness of breath",
  },
  {
    id: "2",
    date: "2024-01-14",
    condition: "Respiratory Infection",
    severity: "moderate",
    confidence: 0.78,
    symptoms: "Cough, fever, chills",
  },
  {
    id: "3",
    date: "2024-01-12",
    condition: "Type 2 Diabetes Risk",
    severity: "moderate",
    confidence: 0.65,
    symptoms: "Fatigue, increased thirst",
  },
  {
    id: "4",
    date: "2024-01-10",
    condition: "Migraine",
    severity: "low",
    confidence: 0.72,
    symptoms: "Headache, light sensitivity",
  },
  {
    id: "5",
    date: "2024-01-08",
    condition: "Common Cold",
    severity: "low",
    confidence: 0.92,
    symptoms: "Runny nose, sore throat",
  },
];

interface HistorySessionRecord {
  id: string | number;
  severity?: string;
  symptoms?: string[];
  user_input?: string;
  created_at?: string;
  primary_condition?: string;
  confidence?: number;
}

export async function fetchHistory(): Promise<DiagnosisRecord[]> {
  try {
    const res = await fetch(`${API_BASE}/api/history?limit=50`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });

    if (!res.ok) {
      throw new Error(`Failed to fetch history: ${res.statusText}`);
    }

    const data = await res.json();
    const sessions = data.sessions || [];
    if (sessions.length === 0) {
      return mockHistoryRecords;
    }

    return sessions.map((s: HistorySessionRecord) => {
      const rawSeverity = (s.severity?.toLowerCase() || "low") as "critical" | "high" | "moderate" | "low";
      const validSeverities: Array<"critical" | "high" | "moderate" | "low"> = ["critical", "high", "moderate", "low"];
      const severity = validSeverities.includes(rawSeverity) ? rawSeverity : "moderate";
      const symptomsList = Array.isArray(s.symptoms) && s.symptoms.length > 0
        ? s.symptoms.join(", ")
        : s.user_input || "Symptom check";
      const dateStr = s.created_at ? s.created_at.split("T")[0] : new Date().toISOString().split("T")[0];

      return {
        id: String(s.id),
        date: dateStr,
        condition: s.primary_condition || "General Assessment",
        severity,
        confidence: typeof s.confidence === "number" ? Math.round(s.confidence * 100) / 100 : 0.8,
        symptoms: symptomsList,
      };
    });
  } catch (err) {
    console.error("fetchHistory error, falling back to mock records:", err);
    return mockHistoryRecords;
  }
}