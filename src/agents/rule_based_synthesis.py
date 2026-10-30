"""Rule-based diagnostic report generator.

Provides a fallback diagnostic report when LLM synthesis is unavailable
or times out. Uses pattern matching and rule-based logic to generate
structured reports from agent outputs.
"""

from typing import Dict, Any
from loguru import logger

from src.core.red_flags import RedFlagEngine


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

        # Extract symptoms — triage input is only present, self-reported
        # findings (w0-assertion-nlp R9). Absent/hypothetical/family/other
        # findings stay in the NLP output for context but never reach here.
        symptoms = nlp.get("symptoms", [])
        symptom_texts = []
        for s in symptoms:
            if isinstance(s, dict):
                if (
                    s.get("polarity", "present") == "present"
                    and s.get("subject", "self") == "self"
                ):
                    symptom_texts.append(s.get("symptom", ""))
            else:
                symptom_texts.append(s)
        symptom_texts = [t for t in symptom_texts if t]

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

        # If no prediction risk score exceeded 0.3 (or prediction didn't run because no clinical history was provided),
        # infer potential conditions from symptoms and RAG
        if not diagnoses and (symptom_texts or symptoms):
            combined_symptoms_str = " ".join([str(s).lower() for s in symptom_texts]).lower()

            for disease_key, info in self.DISEASE_INFO.items():
                disease_name = info.get("name", disease_key)
                matches = 0
                for rf in info.get("red_flags", []):
                    rf_words = [w for w in rf.lower().split() if len(w) > 3]
                    if any(w in combined_symptoms_str for w in rf_words):
                        matches += 1

                keywords = {
                    "cardiovascular_disease": ["chest", "heart", "cardio", "arm", "palpitation", "angina"],
                    "respiratory_infection": ["cough", "breath", "lung", "respiratory", "fever", "throat", "phlegm", "dyspnea"],
                    "diabetes": ["thirst", "urination", "glucose", "sugar", "diabetic"],
                    "neurological_disorder": ["headache", "migraine", "dizziness", "seizure", "numbness", "vision", "neuro"],
                }.get(disease_key, [])

                keyword_matches = sum(1 for kw in keywords if kw in combined_symptoms_str)
                if matches > 0 or keyword_matches > 0:
                    conf = min(0.85, 0.45 + (matches * 0.15) + (keyword_matches * 0.10))
                    diagnoses.append({
                        "condition": disease_name,
                        "confidence": round(conf, 2),
                        "rationale": f"Reported symptoms ({', '.join(symptom_texts[:3])}) align with clinical indicators for {disease_name}.",
                        "icd10_code": info.get("icd10", ""),
                    })

            if not diagnoses and symptom_texts:
                primary = symptom_texts[0].title()
                diagnoses.append({
                    "condition": f"{primary} (Clinical Evaluation Recommended)",
                    "confidence": 0.50,
                    "rationale": f"Patient reported {', '.join(symptom_texts)}. Rule-based evaluation recommends clinical assessment.",
                    "icd10_code": "R68.89",
                })

        # Sort by confidence
        diagnoses.sort(key=lambda x: x["confidence"], reverse=True)

        # Determine overall severity
        nlp_severity = nlp.get("severity", "unknown")
        max_risk = max(risk_scores.values()) if risk_scores else 0
        if max_risk > 0.8 or prediction_severity == "critical" or nlp_severity == "critical":
            severity = "critical"
        elif max_risk > 0.6 or prediction_severity == "high" or nlp_severity == "high":
            severity = "high"
        elif max_risk > 0.3 or prediction_severity == "moderate" or nlp_severity == "moderate":
            severity = "moderate"
        elif any("severe" in str(s).lower() or "chest pain" in str(s).lower() for s in symptom_texts):
            severity = "high"
        else:
            severity = "low"

        # Red flags + escalation from the structured engine (w0-red-flag-engine):
        # tiered, negation-aware, sourced — never word overlap. The engine
        # runs on the patient's own words; when none were passed in, use the
        # original text the NLP preprocessor preserved.
        engine_text = patient_context or (nlp.get("preprocessed") or {}).get("original", "")
        assessment = RedFlagEngine().assess(engine_text)
        escalation = assessment.escalation
        red_flags = [
            f"[{f.tier}] {f.reason} (evidence: '{f.evidence}'; source: {f.source})"
            for f in escalation.findings
            if f.tier != "informational"
        ]

        # Build recommendations
        recommendations = self._build_recommendations(diagnoses, severity)

        # Add vision-based recommendations if applicable
        if vision_anomalies:
            recommendations.append("Follow up on imaging findings with appropriate specialist")

        # The escalation object is authoritative; doctor_alert is now a
        # derived view of it (kept for backward compatibility with the
        # frontend/report consumers until they move onto the object).
        doctor_alert = severity in ("critical", "high") or escalation.level in ("urgent", "emergency")

        # Build explanation — the patient-facing text also consumes only the
        # filtered present/self symptom set (w0-assertion-nlp R9).
        explanation = self._build_explanation(diagnoses, symptom_texts, patient_context, vision_findings)

        # Build differentials
        differentials = self._build_differentials(diagnoses)

        return {
            "diagnosis": diagnoses,
            "explanation": explanation,
            "recommendations": recommendations,
            "severity": severity,
            "doctor_alert": doctor_alert,
            "escalation": escalation.model_dump(),
            "refusal": assessment.refusal.model_dump() if assessment.refusal else None,
            "differential_diagnoses": differentials,
            "red_flags": red_flags,
            "disclaimer": "This is an AI-generated assessment and not a substitute for professional medical advice. Always consult a qualified healthcare provider for diagnosis and treatment.",
        }

    def compose_explanations(self, synthesis: Dict[str, Any]) -> Dict[str, Any]:
        """Guarantee both explanation flavors exist in a synthesis payload.

        LLM synthesis can omit one of the two explanation fields (clinical
        ``explanation`` vs plain-language ``patient_explanation``). The
        dual-mode UI renders both, so each missing flavor is composed from
        the structured diagnosis entries rather than left empty.

        Args:
            synthesis: Synthesis result dict, mutated in place.

        Returns:
            The same dict with both explanation flavors populated.
        """
        diagnoses = synthesis.get("diagnosis") or []
        normalized = []
        for d in diagnoses:
            if isinstance(d, dict):
                normalized.append({
                    "condition": d.get("condition") or d.get("name") or "Undetermined",
                    "confidence": float(d.get("confidence") or 0.0),
                })

        if not synthesis.get("patient_explanation"):
            synthesis["patient_explanation"] = self._build_explanation(normalized, [], "", [])

        if not synthesis.get("explanation"):
            synthesis["explanation"] = self._build_clinical_explanation(normalized, synthesis)

        return synthesis

    def _build_clinical_explanation(self, diagnoses: list, synthesis: dict) -> str:
        """Compose the clinician-facing explanation from structured differentials."""
        if not diagnoses:
            return (
                "Clinical correlation recommended: multi-agent analysis did not "
                "produce a ranked differential; structured evaluation is advised."
            )

        top = diagnoses[0]
        lines = [f"Primary differential: {top['condition']} (confidence {top['confidence']:.0%})."]

        if len(diagnoses) > 1:
            others = ", ".join(f"{d['condition']} ({d['confidence']:.0%})" for d in diagnoses[1:4])
            lines.append(f"Alternative differentials to exclude: {others}.")

        severity = synthesis.get("severity")
        if severity and severity != "unknown":
            lines.append(f"Overall triage severity: {severity}.")

        red_flags = synthesis.get("red_flags") or []
        if red_flags:
            lines.append(
                "Red-flag findings require exclusion of acute pathology: " + "; ".join(red_flags[:3]) + "."
            )

        lines.append(
            "Recommend confirmatory workup and physician sign-off; this "
            "assessment is decision support, not a diagnosis."
        )
        return " ".join(lines)

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

    # _build_red_flags was removed with w0-red-flag-engine: red flags now
    # come from the structured engine (tiered, negation-aware, sourced) in
    # generate_report — the old word-overlap matcher is retired.

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
