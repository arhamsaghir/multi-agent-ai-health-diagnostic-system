"""Confidence scoring module — combines confidences from multiple agents."""

from typing import Optional
from loguru import logger


class ConfidenceScorer:
    """Calculates overall diagnostic confidence by combining agent outputs.

    Weights each agent's contribution based on reliability and relevance,
    considers cross-agent agreement, symptom count, and severity indicators.
    """

    # Base weights for each agent type
    AGENT_WEIGHTS = {
        "nlp": 0.30,
        "vision": 0.25,
        "rag": 0.25,
        "prediction": 0.20,
    }

    def __init__(self, weights: Optional[dict] = None):
        if weights:
            self.AGENT_WEIGHTS = weights
            # Normalize weights to sum to 1.0
            total = sum(weights.values())
            self.AGENT_WEIGHTS = {k: v / total for k, v in weights.items()}

    def score(self, agent_outputs: dict, severity: str = "unknown") -> dict:
        """Calculate overall confidence from all agent outputs.

        Args:
            agent_outputs: Dict with outputs from each agent (nlp, vision, rag, prediction).
            severity: Overall severity assessment.

        Returns:
            Dict with overall_confidence, breakdown, and factors.
        """
        breakdown = {}
        factors = []

        # NLP confidence: based on symptom extraction quality
        nlp = agent_outputs.get("nlp", {})
        nlp_confidence = self._score_nlp(nlp)
        breakdown["nlp"] = round(nlp_confidence, 3)
        factors.append(f"NLP: {nlp_confidence:.0%} — {len(nlp.get('symptoms', []))} symptoms extracted")

        # Vision confidence: based on detection confidence
        vision = agent_outputs.get("vision", {})
        vision_confidence = self._score_vision(vision)
        breakdown["vision"] = round(vision_confidence, 3)
        factors.append(f"Vision: {vision_confidence:.0%} — {vision.get('total_detected', 0)} findings")

        # RAG confidence: based on knowledge retrieval quality
        rag = agent_outputs.get("rag", {})
        rag_confidence = self._score_rag(rag)
        breakdown["rag"] = round(rag_confidence, 3)
        factors.append(f"RAG: {rag_confidence:.0%} — {rag.get('num_sources', 0)} sources")

        # Prediction confidence: based on risk score clarity
        prediction = agent_outputs.get("prediction", {})
        pred_confidence = self._score_prediction(prediction)
        breakdown["prediction"] = round(pred_confidence, 3)
        factors.append(f"Prediction: {pred_confidence:.0%} — max risk: {prediction.get('max_risk', 0):.0%}")

        # Weighted combination
        overall = 0.0
        for agent, weight in self.AGENT_WEIGHTS.items():
            agent_conf = breakdown.get(agent, 0)
            # Only count agents that actually ran (non-zero confidence)
            if agent_conf > 0:
                overall += agent_conf * weight
            else:
                # Reduce overall if an agent didn't run
                overall += 0.1 * weight  # minimal confidence for missing agent

        # Adjust for severity
        severity_multiplier = {
            "critical": 0.85,
            "high": 0.90,
            "moderate": 0.95,
            "low": 1.0,
            "unknown": 0.70,
        }
        overall *= severity_multiplier.get(severity, 1.0)

        # Adjust for cross-agent agreement
        non_zero = [v for v in breakdown.values() if v > 0.1]
        if len(non_zero) >= 3:
            agreement_bonus = self._calculate_agreement(non_zero)
            overall *= (1.0 + agreement_bonus * 0.1)
            factors.append(f"Cross-agent agreement bonus: +{agreement_bonus * 10:.0f}%")
        elif len(non_zero) <= 1:
            factors.append("Low agent coverage — confidence reduced")
            overall *= 0.7

        overall = min(max(overall, 0.0), 1.0)

        logger.info(f"Confidence scoring: overall={overall:.0%}")
        for f in factors:
            logger.debug(f"  {f}")

        return {
            "overall_confidence": round(overall, 3),
            "breakdown": breakdown,
            "factors": factors,
            "agent_count": len(non_zero),
        }

    def _score_nlp(self, nlp_output: dict) -> float:
        """Score NLP agent output quality."""
        symptoms = nlp_output.get("symptoms", [])
        entities = nlp_output.get("entities", [])
        body_systems = nlp_output.get("body_systems", [])

        if not symptoms:
            return 0.0

        # More symptoms extracted = higher confidence (up to a point)
        symptom_score = min(len(symptoms) / 5.0, 1.0)

        # More entities = better understanding
        entity_score = min(len(entities) / 3.0, 1.0)

        # Body system identification helps
        system_score = min(len(body_systems) / 2.0, 1.0)

        return 0.5 * symptom_score + 0.3 * entity_score + 0.2 * system_score

    def _score_vision(self, vision_output: dict) -> float:
        """Score Vision agent output quality."""
        findings = vision_output.get("findings", [])

        if not findings:
            return 0.0

        # Use highest confidence finding
        max_conf = max(f.get("confidence", 0) for f in findings)
        num_findings = min(len(findings) / 3.0, 1.0)

        return 0.7 * max_conf + 0.3 * num_findings

    def _score_rag(self, rag_output: dict) -> float:
        """Score RAG agent output quality."""
        num_sources = rag_output.get("num_sources", 0)
        knowledge = rag_output.get("knowledge", "")

        if num_sources == 0 and not knowledge:
            return 0.0

        source_score = min(num_sources / 3.0, 1.0)
        knowledge_length_score = min(len(knowledge) / 500.0, 1.0)

        return 0.6 * source_score + 0.4 * knowledge_length_score

    def _score_prediction(self, pred_output: dict) -> float:
        """Score Prediction agent output quality."""
        risk_scores = pred_output.get("risk_scores", {})

        if not risk_scores:
            return 0.0

        # Higher max risk = clearer signal
        max_risk = pred_output.get("max_risk", 0)

        # More conditions assessed = better coverage
        n_conditions = len(risk_scores)
        coverage_score = min(n_conditions / 3.0, 1.0)

        return 0.6 * max_risk + 0.4 * coverage_score

    def _calculate_agreement(self, confidences: list[float]) -> float:
        """Calculate how much agents agree with each other.

        Returns 0.0-1.0 where 1.0 means perfect agreement.
        """
        if len(confidences) < 2:
            return 0.0

        mean_conf = sum(confidences) / len(confidences)
        variance = sum((c - mean_conf) ** 2 for c in confidences) / len(confidences)
        std_dev = variance ** 0.5

        # Lower std_dev = higher agreement
        agreement = max(0, 1.0 - std_dev)
        return agreement
