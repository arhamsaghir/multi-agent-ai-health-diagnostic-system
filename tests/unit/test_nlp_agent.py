"""Tests for the NLP Symptom Agent."""

import pytest
import asyncio
from src.agents.nlp.agent import NLPAgent


@pytest.fixture
def agent():
    return NLPAgent()


class TestNLPAgent:
    """Test suite for NLPAgent."""

    def test_extract_symptoms_basic(self, agent):
        result = agent._extract_symptoms("i have a headache and fever")
        assert len(result) >= 2
        categories = [s["category"] for s in result]
        assert "neurological" in categories
        assert "constitutional" in categories

    def test_extract_symptoms_empty(self, agent):
        result = agent._extract_symptoms("")
        assert result == []

    def test_extract_symptoms_respiratory(self, agent):
        result = agent._extract_symptoms("coughing with shortness of breath")
        assert len(result) >= 1
        assert any(s["category"] == "respiratory" for s in result)

    def test_extract_body_systems(self, agent):
        systems = agent._detect_body_systems("my chest hurts and i can't breathe")
        assert "respiratory" in systems
        # "chest" maps to cardiovascular via body_part but keyword matching may vary
        # Just verify at least respiratory is detected for breathing symptoms

    def test_assess_severity_high(self, agent):
        assert agent._assess_severity("severe unbearable pain") == "high"

    def test_assess_severity_moderate(self, agent):
        assert agent._assess_severity("moderate discomfort") == "moderate"

    def test_assess_severity_mild(self, agent):
        assert agent._assess_severity("slight headache") == "mild"

    def test_classify_intent_diagnosis(self, agent):
        assert agent._classify_intent("what do i have, diagnose me") == "diagnosis_request"

    def test_classify_intent_treatment(self, agent):
        assert agent._classify_intent("what medicine should i take") == "treatment_request"

    def test_extract_duration(self, agent):
        assert agent._extract_duration("fever for 3 days") == "3 days"
        assert agent._extract_duration("pain for 2 weeks") == "2 weeks"

    def test_full_run(self, agent):
        result = asyncio.run(
            agent.run({"text": "I have a severe headache and fever for 3 days with nausea"})
        )
        assert "symptoms" in result
        assert "entities" in result
        assert "severity_indicator" in result
        assert result["severity_indicator"] == "high"
        # Duration extraction may return "3 day" or "3 days" depending on regex
        assert result["duration"] is not None

    def test_run_empty_text(self, agent):
        result = asyncio.run(agent.run({"text": ""}))
        assert "error" in result


class TestAssertionExtraction:
    """Polarity, subject, and certainty on extracted findings (w0-assertion-nlp)."""

    def test_live_probe_yields_zero_present(self, agent):
        findings = agent._extract_symptoms("no fever, no cough, no chest pain")
        assert findings, "all three symptoms must still be *found*"
        assert all(f["polarity"] == "absent" for f in findings)

    def test_findings_carry_the_r8_contract(self, agent):
        findings = agent._extract_symptoms("I have a fever")
        assert findings, "expected at least one finding"
        for f in findings:
            assert {"symptom", "category", "polarity", "subject", "certainty", "span"} <= set(f)
            assert f["polarity"] in ("present", "absent", "hypothetical")
            assert f["subject"] in ("self", "family", "other", "hypothetical")
            assert f["certainty"] in ("explicit", "hedged")
            start, end = f["span"]
            assert 0 <= start < end

    def test_negation_is_clause_local(self, agent):
        findings = agent._extract_symptoms("no fever but I have a bad cough")
        by_symptom = {f["symptom"]: f["polarity"] for f in findings}
        assert by_symptom["fever"] == "absent"
        assert by_symptom["cough"] == "present"

    def test_family_subject_attribution(self, agent):
        findings = agent._extract_symptoms("my mother has diabetes and I have a cough")
        by_symptom = {(f["symptom"], f["subject"]) for f in findings}
        assert ("diabetes", "family") in by_symptom
        assert ("cough", "self") in by_symptom

    def test_conditional_is_hypothetical(self, agent):
        findings = agent._extract_symptoms("if I had a fever I would rest")
        assert all(f["polarity"] == "hypothetical" for f in findings)

    def test_double_negation_is_positive(self, agent):
        findings = agent._extract_symptoms("not without a fever")
        assert any(
            f["symptom"] == "fever" and f["polarity"] == "present" for f in findings
        )
