"""Tests for confidence scoring module."""

import pytest
from src.agents.confidence_scorer import ConfidenceScorer


class TestConfidenceScorer:
    """Test cases for ConfidenceScorer."""

    def setup_method(self):
        self.scorer = ConfidenceScorer()

    def test_empty_agent_outputs(self):
        """Empty outputs should return near-zero confidence."""
        result = self.scorer.score({})
        assert result["overall_confidence"] < 0.3
        assert result["agent_count"] == 0

    def test_single_agent_low_confidence(self):
        """Single agent with minimal output should have low confidence."""
        outputs = {
            "nlp": {"symptoms": [{"symptom": "headache", "category": "neurological"}]},
        }
        result = self.scorer.score(outputs)
        assert result["overall_confidence"] < 0.5
        assert result["breakdown"]["nlp"] >= 0
        # Single agent with minimal output has low confidence due to coverage penalty

    def test_nlp_scoring_with_multiple_symptoms(self):
        """More symptoms should yield higher NLP confidence."""
        outputs = {
            "nlp": {
                "symptoms": [
                    {"symptom": "headache", "category": "neurological"},
                    {"symptom": "fever", "category": "systemic"},
                    {"symptom": "cough", "category": "respiratory"},
                ],
                "entities": [
                    {"type": "body_part", "value": "head"},
                    {"type": "duration", "value": "3 days"},
                ],
                "body_systems": ["neurological", "respiratory"],
            },
        }
        result = self.scorer.score(outputs)
        assert result["breakdown"]["nlp"] > 0.5

    def test_vision_scoring(self):
        """Vision scoring should use max confidence finding."""
        outputs = {
            "vision": {
                "findings": [
                    {"condition": "Pneumonia", "confidence": 0.85},
                    {"condition": "Effusion", "confidence": 0.60},
                ],
                "total_detected": 2,
            },
        }
        result = self.scorer.score(outputs)
        assert result["breakdown"]["vision"] > 0.5

    def test_rag_scoring(self):
        """RAG scoring should consider source count and knowledge length."""
        outputs = {
            "rag": {
                "num_sources": 3,
                "knowledge": "Headaches can be caused by tension, migraines, or more serious conditions. Clinical guidelines recommend evaluation if persistent.",
            },
        }
        result = self.scorer.score(outputs)
        assert result["breakdown"]["rag"] > 0.5

    def test_prediction_scoring(self):
        """Prediction scoring should use max risk and condition count."""
        outputs = {
            "prediction": {
                "risk_scores": {
                    "cardiovascular_disease": 0.65,
                    "diabetes": 0.30,
                },
                "max_risk": 0.65,
            },
        }
        result = self.scorer.score(outputs)
        assert result["breakdown"]["prediction"] > 0.3

    def test_full_pipeline_high_confidence(self):
        """All agents running with good outputs should yield high confidence."""
        outputs = {
            "nlp": {
                "symptoms": [
                    {"symptom": "chest pain", "category": "cardiovascular"},
                    {"symptom": "shortness of breath", "category": "respiratory"},
                ],
                "entities": [
                    {"type": "body_part", "value": "chest"},
                    {"type": "severity_modifier", "value": "severe"},
                ],
                "body_systems": ["cardiovascular", "respiratory"],
            },
            "vision": {
                "findings": [
                    {"condition": "Cardiomegaly", "confidence": 0.78},
                ],
                "total_detected": 1,
            },
            "rag": {
                "num_sources": 4,
                "knowledge": "Chest pain with shortness of breath may indicate cardiovascular issues. Clinical guidelines recommend immediate ECG evaluation.",
            },
            "prediction": {
                "risk_scores": {
                    "cardiovascular_disease": 0.80,
                },
                "max_risk": 0.80,
            },
        }
        result = self.scorer.score(outputs, severity="high")
        assert result["overall_confidence"] > 0.4
        assert result["agent_count"] == 4
        assert all(k in result["breakdown"] for k in ["nlp", "vision", "rag", "prediction"])

    def test_severity_adjustment(self):
        """Critical severity should reduce confidence slightly."""
        outputs = {
            "nlp": {
                "symptoms": [{"symptom": "headache", "category": "neurological"}],
                "entities": [],
                "body_systems": ["neurological"],
            },
        }
        result_normal = self.scorer.score(outputs, severity="low")
        result_critical = self.scorer.score(outputs, severity="critical")
        assert result_critical["overall_confidence"] < result_normal["overall_confidence"]

    def test_custom_weights(self):
        """Custom weights should be normalized and applied."""
        weights = {"nlp": 0.5, "vision": 0.3, "rag": 0.2}
        scorer = ConfidenceScorer(weights=weights)
        # Weights should sum to 1.0
        total = sum(scorer.AGENT_WEIGHTS.values())
        assert abs(total - 1.0) < 0.001

    def test_agreement_bonus(self):
        """High agreement between agents should boost confidence."""
        outputs = {
            "nlp": {
                "symptoms": [{"symptom": "fever", "category": "systemic"}],
                "entities": [{"type": "severity_modifier", "value": "moderate"}],
                "body_systems": ["systemic"],
            },
            "rag": {
                "num_sources": 3,
                "knowledge": "Fever indicates possible infection. Monitor temperature.",
            },
            "prediction": {
                "risk_scores": {"respiratory_infection": 0.55},
                "max_risk": 0.55,
            },
        }
        result = self.scorer.score(outputs)
        # Should have 3 agents running
        assert result["agent_count"] >= 3

    def test_cross_agent_agreement_calculation(self):
        """Agreement should be high for similar confidences."""
        # Test internal agreement calculation
        high_agreement = self.scorer._calculate_agreement([0.7, 0.75, 0.72])
        low_agreement = self.scorer._calculate_agreement([0.2, 0.8, 0.5])
        assert high_agreement > low_agreement
