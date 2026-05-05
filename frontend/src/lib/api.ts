import { DiagnosisResult } from "@/components/diagnosis/DiagnosisResults";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface PatientHistory {
  age: number;
  bmi: number;
  gender: string;
  familyHistory: string[];
}

export async function diagnose(
  text: string, 
  history: PatientHistory,
  demoMode: boolean = true
): Promise<DiagnosisResult[]> {
  if (demoMode) {
    return getDemoResults(text);
  }

  try {
    const response = await fetch(`${API_BASE}/api/diagnosis/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, patient_history: history }),
    });

    if (!response.ok) {
      throw new Error("API request failed");
    }

    const data = await response.json();
    return transformAPIResponse(data);
  } catch (error) {
    console.error("API error, falling back to demo:", error);
    return getDemoResults(text);
  }
}

function transformAPIResponse(data: any): DiagnosisResult[] {
  const diagnosis = data.diagnosis || [];
  return diagnosis.map((d: any) => ({
    condition: d.name || d.condition,
    confidence: d.confidence || 0,
    severity: d.severity || "moderate",
    description: d.description || "",
    recommendations: d.recommendations || [],
    redFlags: d.redFlags || [],
  }));
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