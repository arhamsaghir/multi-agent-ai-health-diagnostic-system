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

export interface VisionResult {
  predictions: AnalysisResult[];
  primary_finding: string;
  severity: "critical" | "high" | "moderate" | "low";
  recommendation: string;
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

function transformAPIResponse(data: any): DiagnosisResult[] {
  const diagnosis = Array.isArray(data.diagnosis) && data.diagnosis.length > 0
    ? data.diagnosis
    : Array.isArray(data.differential_diagnoses) && data.differential_diagnoses.length > 0
      ? data.differential_diagnoses.map((name: string) => ({ name, confidence: 0.7, severity: data.severity || "moderate" }))
      : [];

  const baseRecommendations = Array.isArray(data.recommendations) ? data.recommendations : [];
  const baseRedFlags = Array.isArray(data.red_flags) ? data.red_flags : [];
  const generalExplanation = data.patient_explanation || data.explanation || "";

  if (diagnosis.length === 0) {
    return [{
      condition: "Clinical Evaluation Recommended",
      confidence: 0.6,
      severity: (data.severity as any) || "moderate",
      description: generalExplanation || "The multi-agent system analyzed the provided symptoms. Clinical follow-up is recommended.",
      recommendations: baseRecommendations.length > 0 ? baseRecommendations : ["Consult a licensed physician for comprehensive evaluation"],
      redFlags: baseRedFlags,
    }];
  }

  return diagnosis.map((d: any, idx: number) => {
    const rawSeverity = (d.severity?.toLowerCase() || data.severity?.toLowerCase() || "moderate");
    const validSeverities: Array<"critical" | "high" | "moderate" | "low"> = ["critical", "high", "moderate", "low"];
    const severity = validSeverities.includes(rawSeverity) ? rawSeverity : "moderate";

    return {
      condition: d.name || d.condition || `Condition ${idx + 1}`,
      confidence: typeof d.confidence === "number" ? Math.round(d.confidence * 100) / 100 : 0.75,
      severity,
      description: d.description || generalExplanation || "Differential diagnosis derived from reported symptoms and risk models.",
      recommendations: d.recommendations && d.recommendations.length > 0 ? d.recommendations : baseRecommendations,
      redFlags: d.redFlags && d.redFlags.length > 0 ? d.redFlags : baseRedFlags,
    };
  });
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

    return sessions.map((s: any) => {
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