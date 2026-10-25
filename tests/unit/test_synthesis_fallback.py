"""Tests for the synthesis agent's patient-explanation fallback.

When the LLM provider is unreachable the client returns an error string
rather than raising. That string must never reach the patient.
"""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from src.agents.synthesis.agent import GenAIAgent


@pytest.fixture
def agent() -> GenAIAgent:
    """A synthesis agent with a stubbed confidence scorer and LLM client."""
    instance = GenAIAgent()
    instance._confidence_scorer = SimpleNamespace(
        score=lambda outputs, severity: {"overall_confidence": 0.5, "agent_count": 2}
    )
    return instance


def _stub_gemini(monkeypatch, agent: GenAIAgent, report: dict, explanation) -> None:
    """Point the agent at a stubbed LLM client."""

    def generate_report(agent_outputs, patient_context=""):
        return report

    monkeypatch.setattr(
        type(agent),
        "gemini",
        property(lambda self: SimpleNamespace(
            generate_report=generate_report,
            explain_to_patient=explanation,
        )),
    )


def _run(agent: GenAIAgent) -> dict:
    """Run the synthesis agent with stubbed agent outputs."""
    return asyncio.run(
        agent.run(
            {
                "nlp": {"symptoms": ["chest pain"]},
                "vision": {"findings": []},
                "rag": {"knowledge": ""},
                "prediction": {"risk_scores": {}},
            }
        )
    )


def test_error_string_from_llm_is_not_shown_to_the_patient(agent, monkeypatch) -> None:
    """An LLM error string must be replaced by the rule-based explanation."""
    report = {
        "diagnosis": [{"condition": "Cardiovascular Disease", "confidence": 0.6}],
        "explanation": "Your symptoms suggest a cardiac issue and warrant evaluation.",
        "severity": "high",
        "doctor_alert": True,
        "recommendations": ["Seek evaluation"],
    }

    _stub_gemini(
        monkeypatch,
        agent,
        report,
        lambda report, language="simple": (
            "Error generating response: Model returned an empty completion"
        ),
    )

    result = _run(agent)
    assert not result["patient_explanation"].startswith("Error generating response")
    assert result["patient_explanation"] == report["explanation"]


def test_successful_llm_explanation_is_used(agent, monkeypatch) -> None:
    """A normal LLM answer is passed through unchanged."""
    report = {
        "diagnosis": [{"condition": "Cardiovascular Disease", "confidence": 0.6}],
        "explanation": "rule-based text",
        "severity": "moderate",
    }

    _stub_gemini(
        monkeypatch,
        agent,
        report,
        lambda report, language="simple": "friendly patient text",
    )

    result = _run(agent)
    assert result["patient_explanation"] == "friendly patient text"


def test_llm_exception_falls_back_to_rule_based(agent, monkeypatch) -> None:
    """An exception from the provider also falls back cleanly."""
    report = {
        "diagnosis": [{"condition": "Cardiovascular Disease", "confidence": 0.6}],
        "explanation": "rule-based text",
        "severity": "moderate",
    }

    def explode(report, language="simple"):
        raise RuntimeError("provider down")

    _stub_gemini(monkeypatch, agent, report, explode)

    result = _run(agent)
    assert result["patient_explanation"] == "rule-based text"
