"""Prediction Agent — ML-based disease risk scoring.

Uses GradientBoosting classifiers (scikit-learn, loaded from joblib) for
tabular patient data risk prediction, with a rule-based fallback when no
trained model is available.
"""

from typing import Any, Optional
import os
import json
import numpy as np

from src.agents.base import BaseAgent
from src.data.preprocessing.tabular_preprocessor import TabularPreprocessor
from config import settings


class PredictionAgent(BaseAgent):
    """Machine learning prediction agent for disease risk assessment."""

    name = "prediction_agent"
    description = "GradientBoosting — Risk scoring from patient history and vitals"

    def __init__(self):
        super().__init__()
        self.preprocessor = TabularPreprocessor()
        self.model = None
        self.model_dict = {}
        self.feature_names = []
        self._load_model()

    def _load_model(self):
        """Load pre-trained GradientBoosting models from joblib files."""
        model_path = settings.prediction_model_path
        model_dir = os.path.dirname(model_path)
        model_basename = os.path.splitext(os.path.basename(model_path))[0]

        # Try joblib format (recommended)
        meta_path = os.path.join(model_dir, f"{model_basename}_metadata.json")
        if os.path.exists(meta_path):
            try:
                import joblib
                with open(meta_path, "r") as f:
                    metadata = json.load(f)

                self.feature_names = metadata.get("feature_names", [])
                diseases = metadata.get("diseases", [])

                for disease in diseases:
                    # Support both .joblib and .pkl extensions
                    for ext in [".joblib", ".pkl"]:
                        disease_model_path = os.path.join(model_dir, f"{model_basename}_{disease}{ext}")
                        if os.path.exists(disease_model_path):
                            model = joblib.load(disease_model_path)
                            self.model_dict[disease] = model
                            break

                if self.model_dict:
                    self.model = self.model_dict
                    self.log("info", f"Loaded {len(self.model_dict)} GradientBoosting models via joblib")
                return
            except Exception as e:
                self.log("warning", f"Failed to load joblib models ({e}), using rule-based scoring")

        self.log("warning", "No trained model found — using rule-based scoring")

    async def run(self, input_data: dict) -> dict:
        """Assess disease risk from patient data.

        Args:
            input_data: Dict with patient_history containing age, vitals,
                       conditions, lifestyle factors.

        Returns:
            Dict with risk scores per condition, severity, and recommendations.
        """
        history = input_data.get("patient_history", {})
        symptoms = input_data.get("symptoms", [])

        if not history and not symptoms:
            return {"error": "No patient data provided", "risk_scores": {}}

        if self.model:
            try:
                risk_scores = self._ml_prediction(history, symptoms)
            except Exception as e:
                self.log("warning", f"Prediction failed ({e}), using rule-based scoring")
                risk_scores = self._rule_based_scoring(history, symptoms)
        else:
            risk_scores = self._rule_based_scoring(history, symptoms)

        # Determine overall severity
        max_score = max(risk_scores.values()) if risk_scores else 0
        severity = "critical" if max_score > 0.8 else "high" if max_score > 0.6 else "moderate" if max_score > 0.3 else "low"

        doctor_alert = max_score > 0.7 or severity in ("critical", "high")

        recommendations = self._generate_recommendations(risk_scores, severity)

        return {
            "risk_scores": risk_scores,
            "max_risk": round(max_score, 3),
            "severity": severity,
            "doctor_alert": doctor_alert,
            "recommendations": recommendations,
            "model_used": "gradient_boosting" if self.model else "rule-based",
            "agent": self.name,
        }

    def _ml_prediction(self, history: dict, symptoms: list) -> dict:
        """Use trained ML models for prediction (one model per disease)."""
        try:
            feature_vector = self.preprocessor.build_feature_vector(history)
            fv = feature_vector.reshape(1, -1)

            risk_scores = {}
            for disease_name, disease_model in self.model_dict.items():
                try:
                    probs = disease_model.predict_proba(fv)[0]
                    # predict_proba returns [prob_negative, prob_positive] for binary
                    risk_scores[disease_name] = round(float(probs[1]), 3)
                except Exception:
                    risk_scores[disease_name] = 0.0

            return risk_scores
        except Exception as e:
            self.log("warning", f"ML prediction failed ({e}), falling back to rule-based")
            return self._rule_based_scoring(history, symptoms)

    def _rule_based_scoring(self, history: dict, symptoms: list) -> dict:
        """Fallback rule-based risk scoring when no trained model exists."""
        risks = {}

        age = history.get("age", 30)
        if age > 60:
            risks["cardiovascular_disease"] = 0.6
            risks["diabetes"] = 0.4
        elif age > 40:
            risks["cardiovascular_disease"] = 0.35
            risks["diabetes"] = 0.25
        else:
            risks["cardiovascular_disease"] = 0.15
            risks["diabetes"] = 0.1

        # Symptom-based adjustments
        symptom_lower = [s.lower() if isinstance(s, str) else s for s in symptoms]
        symptom_text = " ".join(str(s) for s in symptoms).lower()

        if any(w in symptom_text for w in ["chest pain", "shortness of breath", "palpitation"]):
            risks["cardiovascular_disease"] = min(risks.get("cardiovascular_disease", 0) + 0.4, 1.0)

        if any(w in symptom_text for w in ["cough", "fever", "breath", "wheeze"]):
            risks["respiratory_infection"] = 0.55

        if any(w in symptom_text for w in ["headache", "dizzy", "confusion", "numb"]):
            risks["neurological_disorder"] = 0.45

        # BMI-based adjustments
        bmi = history.get("bmi", 25)
        if bmi > 30:
            risks["diabetes"] = min(risks.get("diabetes", 0) + 0.3, 1.0)
            risks["cardiovascular_disease"] = min(risks.get("cardiovascular_disease", 0) + 0.2, 1.0)

        # Family history
        family_history = history.get("family_history", [])
        if "diabetes" in family_history:
            risks["diabetes"] = min(risks.get("diabetes", 0) + 0.2, 1.0)
        if "heart disease" in family_history:
            risks["cardiovascular_disease"] = min(risks.get("cardiovascular_disease", 0) + 0.2, 1.0)

        # Round scores
        return {k: round(v, 3) for k, v in risks.items()}

    def _generate_recommendations(self, risks: dict, severity: str) -> list[str]:
        """Generate actionable recommendations based on risk scores."""
        recs = []

        if severity in ("critical", "high"):
            recs.append("Seek immediate medical attention")
            recs.append("Consult a specialist for further evaluation")

        for condition, score in risks.items():
            if score > 0.5:
                condition_names = {
                    "cardiovascular_disease": "cardiovascular health",
                    "respiratory_infection": "respiratory evaluation",
                    "diabetes": "blood sugar testing",
                    "neurological_disorder": "neurological assessment",
                }
                recs.append(f"Schedule evaluation for {condition_names.get(condition, condition)}")

        if not recs:
            recs.append("Continue monitoring symptoms")
            recs.append("Maintain a healthy lifestyle")

        return recs
