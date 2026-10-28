"""GenAI Synthesis Agent — LLM diagnostic report generation.

Takes outputs from all specialist agents (NLP, Vision, RAG, Prediction) and
produces a structured diagnostic report with diagnoses, explanations,
recommendations, severity assessment, and patient-friendly language. Uses the
configured LLM provider (Gemini, with an OpenRouter fallback) and degrades to
the rule-based report generator when no provider is reachable.
"""

from typing import Optional
from loguru import logger

from src.agents.base import BaseAgent
from src.llm.gemini_client import GeminiClient
from src.agents.confidence_scorer import ConfidenceScorer


class GenAIAgent(BaseAgent):
    """Generates final diagnostic report by synthesizing all agent outputs."""

    name = "genai_agent"
    description = "LLM synthesis (rule-based fallback) — Diagnostic report and patient communication"

    def __init__(self):
        super().__init__()
        self._gemini = None
        self._confidence_scorer = None
        self._load_attempted = False
        # Don't load Gemini at init — lazy load on first use

    @property
    def gemini(self):
        """Lazy-load Gemini client on first access."""
        if self._gemini is None:
            from src.llm.gemini_client import GeminiClient
            self._gemini = GeminiClient()
        return self._gemini

    @property
    def confidence_scorer(self):
        """Lazy-load confidence scorer on first access."""
        if self._confidence_scorer is None:
            from src.agents.confidence_scorer import ConfidenceScorer
            self._confidence_scorer = ConfidenceScorer()
        return self._confidence_scorer

    async def run(self, input_data: dict) -> dict:
        """Generate a diagnostic report from all agent outputs.

        Args:
            input_data: Dict with keys:
                - nlp: NLP agent output (symptoms, entities, body_systems)
                - vision: Vision agent output (findings, anomalies)
                - rag: RAG agent output (knowledge, relevant_docs)
                - prediction: Prediction agent output (risk_scores, severity)
                - patient_context: Optional patient history string
                - user_input: Original user text

        Returns:
            Dict with diagnosis, explanation, recommendations, severity,
            confidence_score, doctor_alert, and full report.
        """
        nlp = input_data.get("nlp", {})
        vision = input_data.get("vision", {})
        rag = input_data.get("rag", {})
        prediction = input_data.get("prediction", {})
        patient_context = input_data.get("patient_context", "")
        user_input = input_data.get("user_input", "")

        self.log("info", "Generating diagnostic report from agent outputs")

        # Build agent outputs dict for synthesis
        agent_outputs = {
            "nlp": nlp,
            "vision": vision,
            "rag": rag,
            "prediction": prediction,
        }

        # Generate structured report via Gemini
        report = self.gemini.generate_report(agent_outputs, patient_context)

        # Calculate confidence score
        confidence = self.confidence_scorer.score(agent_outputs, report.get("severity", "unknown"))

        # Determine severity and doctor alert from report
        severity = report.get("severity", "unknown")
        doctor_alert = report.get("doctor_alert", False)

        # Auto-escalate to doctor alert if severity is critical
        if severity == "critical":
            doctor_alert = True

        # Generate patient-friendly explanation
        patient_explanation = report.get("explanation", "No explanation available.")
        try:
            generated = self.gemini.explain_to_patient(
                report,
                language="simple"
            )
            # The LLM client reports a total failure as an error string
            # instead of raising, so an unreachable provider would otherwise
            # surface "Error generating response: ..." to the patient.
            if generated and not generated.startswith("Error generating response"):
                patient_explanation = generated
            else:
                self.log(
                    "warning",
                    "LLM patient explanation unavailable — using the rule-based explanation",
                )
        except Exception as e:
            self.log("warning", f"Failed to generate patient explanation: {e}")
            patient_explanation = report.get("explanation", "Please consult a healthcare professional for evaluation of your symptoms.")

        # Build final output
        result = {
            "diagnosis": report.get("diagnosis", []),
            "explanation": report.get("explanation", ""),
            "patient_explanation": patient_explanation,
            "recommendations": report.get("recommendations", []),
            "severity": severity,
            "doctor_alert": doctor_alert,
            "differential_diagnoses": report.get("differential_diagnoses", []),
            "red_flags": report.get("red_flags", []),
            "confidence": confidence,
            "disclaimer": report.get(
                "disclaimer",
                "This is an AI-generated assessment and not a substitute for professional medical advice. Always consult a qualified healthcare provider for diagnosis and treatment."
            ),
            "agent": self.name,
        }

        self.log("info", f"Report generated — severity: {severity}, confidence: {confidence['overall_confidence']:.0%}")
        return result

    def format_report_for_display(self, result: dict) -> str:
        """Format the diagnostic report for display in the UI.

        Args:
            result: The report dict from run().

        Returns:
            Formatted markdown string.
        """
        lines = []
        lines.append("# Diagnostic Report\n")

        # Severity banner
        severity = result.get("severity", "unknown").upper()
        if result.get("doctor_alert"):
            lines.append(f"## ⚠️ SEVERITY: {severity} — Medical Attention Recommended\n")
        else:
            lines.append(f"## Severity: {severity}\n")

        # Confidence
        confidence = result.get("confidence", {})
        overall_conf = confidence.get("overall_confidence", 0)
        lines.append(f"**Confidence:** {overall_conf:.0%}\n")

        # Diagnoses
        diagnoses = result.get("diagnosis", [])
        if diagnoses:
            lines.append("## Possible Conditions\n")
            for d in diagnoses:
                conf = d.get("confidence", 0)
                condition = d.get("condition", "Unknown")
                rationale = d.get("rationale", "")
                icd10 = d.get("icd10_code", "")
                icd_str = f" ({icd10})" if icd10 else ""
                lines.append(f"- **{condition}**{icd_str}: {conf:.0%} confidence")
                if rationale:
                    lines.append(f"  - {rationale}")
            lines.append("")

        # Differential diagnoses
        differentials = result.get("differential_diagnoses", [])
        if differentials:
            lines.append("## Differential Diagnoses\n")
            for d in differentials:
                lines.append(f"- {d}")
            lines.append("")

        # Red flags
        red_flags = result.get("red_flags", [])
        if red_flags:
            lines.append("## 🚨 Red Flags\n")
            for flag in red_flags:
                lines.append(f"- {flag}")
            lines.append("")

        # Recommendations
        recommendations = result.get("recommendations", [])
        if recommendations:
            lines.append("## Recommendations\n")
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")

        # Patient explanation
        patient_exp = result.get("patient_explanation", "")
        if patient_exp:
            lines.append("## What This Means for You\n")
            lines.append(patient_exp)
            lines.append("")

        # Disclaimer
        lines.append("---")
        lines.append(result.get("disclaimer", ""))

        return "\n".join(lines)
