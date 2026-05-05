"""Rule-based diagnostic report generator.

Provides a fallback diagnostic report when LLM synthesis is unavailable
or times out. Uses pattern matching and rule-based logic to generate
structured reports from agent outputs.
"""

from typing import Dict, Any
from loguru import logger


class RuleBasedSynthesizer:
    """Generate diagnostic reports without LLM calls."""

    # Disease information database
    DISEASE_INFO = {
        "cardiovascular_disease": {
            "name": "Cardiovascular Disease",
            "icd10": "I25.9",
            "description": "Conditions affecting the heart and blood vessels",
            "red_flags": [
                "Chest pain or pressure",
                "Shortness of breath",
                "Pain radiating to arm or jaw",
                "Sudden dizziness or fainting",
            ],
            "recommendations": [
                "Seek immediate medical evaluation if experiencing chest pain",
                "Monitor blood pressure regularly",
                "Consult a cardiologist for comprehensive assessment",
                "Maintain heart-healthy diet and exercise routine",
            ],
        },
        "respiratory_infection": {
            "name": "Respiratory Infection",
            "icd10": "J22",
            "description": "Infections affecting the respiratory system",
            "red_flags": [
                "Difficulty breathing",
                "High fever persisting >3 days",
                "Coughing up blood",
                "Blue lips or face",
            ],
            "recommendations": [
                "Rest and stay hydrated",
                "Monitor oxygen saturation levels",
                "Seek medical attention if breathing becomes difficult",
                "Consider chest X-ray for further evaluation",
            ],
        },
        "diabetes": {
            "name": "Diabetes",
            "icd10": "E11.9",
            "description": "Condition affecting blood sugar regulation",
            "red_flags": [
                "Excessive thirst and urination",
                "Blurred vision",
                "Slow-healing wounds",
                "Confusion or drowsiness",
            ],
            "recommendations": [
                "Get fasting blood glucose test",
                "Monitor HbA1c levels",
                "Consult an endocrinologist",
                "Maintain balanced diet and regular exercise",
            ],
        },
        "neurological_disorder": {
            "name": "Neurological Disorder",
            "icd10": "G93.9",
            "description": "Conditions affecting the nervous system",
            "red_flags": [
                "Sudden severe headache",
                "Weakness on one side of body",
                "Difficulty speaking or understanding speech",
                "Loss of consciousness",
            ],
            "recommendations": [
                "Seek immediate medical attention for severe symptoms",
                "Consult a neurologist for comprehensive evaluation",
                "Consider MRI or CT scan for further assessment",
                "Monitor symptoms and document any changes",
            ],
        },
    }

    def generate_report(self, agent_outputs: Dict[str, Any], patient_context: str = "") -> Dict[str, Any]:
        """Generate a diagnostic report using rule-based logic.

        Args:
            agent_outputs: Dict with outputs from NLP, Vision, RAG, Prediction agents.
            patient_context: Patient demographics and history.

        Returns:
            Dict with diagnosis list, explanation, recommendations, severity, doctor_alert.
        """
        nlp = agent_outputs.get("nlp", {})
        vision = agent_outputs.get("vision", {})
        rag = agent_outputs.get("rag", {})
        prediction = agent_outputs.get("prediction", {})

        # Extract risk scores
        risk_scores = prediction.get("risk_scores", {})
        prediction_severity = prediction.get("severity", "unknown")

        # Extract symptoms
        symptoms = nlp.get("symptoms", [])
        symptom_texts = [s.get("symptom", s) if isinstance(s, dict) else s for s in symptoms]

        # Extract vision findings
        vision_findings = vision.get("findings", [])
        vision_anomalies = vision.get("anomalies", [])

        # Build diagnoses from prediction scores
        diagnoses = []
        for disease, score in risk_scores.items():
            if score > 0.3:  # Only include if risk > 30%
                info = self.DISEASE_INFO.get(disease, {})
                diagnoses.append({
                    "condition": info.get("name", disease),
                    "confidence": round(score, 2),
                    "rationale": self._build_rationale(disease, symptom_texts, risk_scores),
                    "icd10_code": info.get("icd10", ""),
                })

        # Sort by confidence
        diagnoses.sort(key=lambda x: x["confidence"], reverse=True)

        # Determine overall severity
        max_risk = max(risk_scores.values()) if risk_scores else 0
        if max_risk > 0.8 or prediction_severity == "critical":
            severity = "critical"
        elif max_risk > 0.6 or prediction_severity == "high":
            severity = "high"
        elif max_risk > 0.3 or prediction_severity == "moderate":
            severity = "moderate"
        else:
            severity = "low"

        # Build recommendations
        recommendations = self._build_recommendations(diagnoses, severity)

        # Add vision-based recommendations if applicable
        if vision_anomalies:
            recommendations.append("Follow up on imaging findings with appropriate specialist")

        # Build red flags
        red_flags = self._build_red_flags(diagnoses, symptom_texts)

        # Build explanation
        explanation = self._build_explanation(diagnoses, symptoms, patient_context, vision_findings)

        # Build differentials
        differentials = self._build_differentials(diagnoses)

        # Determine doctor alert
        doctor_alert = severity in ("critical", "high") or len(red_flags) > 0

        return {
            "diagnosis": diagnoses,
            "explanation": explanation,
            "recommendations": recommendations,
            "severity": severity,
            "doctor_alert": doctor_alert,
            "differential_diagnoses": differentials,
            "red_flags": red_flags,
            "disclaimer": "This is an AI-generated assessment and not a substitute for professional medical advice. Always consult a qualified healthcare provider for diagnosis and treatment.",
        }

    def _build_rationale(self, disease: str, symptoms: list, risk_scores: dict) -> str:
        """Build rationale for a diagnosis based on symptoms and risk factors."""
        info = self.DISEASE_INFO.get(disease, {})
        name = info.get("name", disease)

        # Check for matching symptoms
        matching_symptoms = []
        symptom_patterns = {
            "cardiovascular_disease": ["chest pain", "shortness of breath", "palpitation"],
            "respiratory_infection": ["cough", "fever", "breath", "wheeze"],
            "diabetes": ["thirst", "urination", "fatigue", "blurred"],
            "neurological_disorder": ["headache", "dizzy", "confusion", "numb"],
        }

        patterns = symptom_patterns.get(disease, [])
        for symptom in symptoms:
            if any(p in symptom.lower() for p in patterns):
                matching_symptoms.append(symptom)

        if matching_symptoms:
            return f"Patient presents with {', '.join(matching_symptoms)}, consistent with {name}."
        else:
            return f"Risk assessment indicates elevated probability of {name} based on patient profile."

    def _build_recommendations(self, diagnoses: list, severity: str) -> list:
        """Build recommendations based on diagnoses and severity."""
        recs = []

        if severity in ("critical", "high"):
            recs.append("Seek immediate medical attention")

        for diag in diagnoses:
            condition = diag["condition"].lower()
            for disease_key, info in self.DISEASE_INFO.items():
                if info["name"].lower() == condition:
                    recs.extend(info["recommendations"][:2])  # Top 2 recommendations
                    break

        if not recs:
            recs = ["Continue monitoring symptoms", "Maintain a healthy lifestyle", "Consult a healthcare professional if symptoms persist"]

        # Deduplicate while preserving order
        seen = set()
        unique_recs = []
        for rec in recs:
            if rec not in seen:
                seen.add(rec)
                unique_recs.append(rec)

        return unique_recs[:5]  # Limit to 5 recommendations

    def _build_red_flags(self, diagnoses: list, symptoms: list) -> list:
        """Build red flags based on diagnoses and symptoms."""
        flags = []

        for diag in diagnoses:
            condition = diag["condition"].lower()
            for disease_key, info in self.DISEASE_INFO.items():
                if info["name"].lower() == condition:
                    # Only include red flags that match patient symptoms
                    for flag in info["red_flags"]:
                        flag_lower = flag.lower()
                        if any(s.lower() in flag_lower or flag_lower in s.lower() for s in symptoms):
                            flags.append(flag)
                    break

        return flags[:3]  # Limit to 3 red flags

    def _build_explanation(self, diagnoses: list, symptoms: list, patient_context: str, vision_findings: list) -> str:
        """Build patient-friendly explanation."""
        if not diagnoses:
            return "Based on the information provided, no specific conditions were identified with high confidence. However, your symptoms should be evaluated by a healthcare professional for proper assessment."

        top_diag = diagnoses[0]
        condition_name = top_diag["condition"]
        confidence = top_diag["confidence"]

        symptom_list = ", ".join([s.get("symptom", s) if isinstance(s, dict) else s for s in symptoms[:3]]) if symptoms else "your reported symptoms"

        explanation = (
            f"Based on your symptoms ({symptom_list}) and patient profile, "
            f"our analysis suggests {condition_name} as a possible condition "
            f"with {confidence:.0%} confidence. "
        )

        if len(diagnoses) > 1:
            other_conditions = ", ".join([d["condition"] for d in diagnoses[1:3]])
            explanation += f"Other conditions to consider include {other_conditions}. "

        explanation += (
            "This assessment is based on AI analysis and should not replace "
            "professional medical advice. Please consult a healthcare provider "
            "for proper evaluation and diagnosis."
        )

        return explanation

    def _build_differentials(self, diagnoses: list) -> list:
        """Build differential diagnoses."""
        differentials = []

        all_conditions = {
            "cardiovascular_disease": ["Anxiety-related chest discomfort", "Gastroesophageal reflux disease (GERD)", "Musculoskeletal chest pain"],
            "respiratory_infection": ["Allergic rhinitis", "Seasonal allergies", "Environmental irritation"],
            "diabetes": ["Thyroid dysfunction", "Metabolic syndrome", "Prediabetes"],
            "neurological_disorder": ["Tension headache", "Migraine", "Stress-related symptoms"],
        }

        for diag in diagnoses[:2]:  # Only for top 2 diagnoses
            for disease_key, diffs in all_conditions.items():
                if disease_key in diag.get("condition", "").lower() or diag.get("condition", "").lower() in disease_key:
                    differentials.extend(diffs[:2])
                    break

        return differentials[:3]  # Limit to 3 differentials
