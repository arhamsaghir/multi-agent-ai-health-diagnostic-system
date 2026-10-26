"""Regression tests for PHI log hygiene and truth-aligned agent metadata.

Two guarantees are locked in here:

1. Patient-supplied free text never reaches the log stream. Logs may show
   that input arrived and how long it was, never the content itself.
2. The agent metadata shown to users describes the pipeline that actually
   runs, not a model the code only claims to use.
"""

import asyncio

import pytest
from loguru import logger

from src.utils.redaction import redact, safe_error, text_fingerprint


@pytest.fixture
def captured_logs():
    """Collect loguru messages emitted during the test."""
    messages: list[str] = []
    handler_id = logger.add(
        lambda message: messages.append(message.record["message"]),
        level="DEBUG",
    )
    yield messages
    logger.remove(handler_id)


class TestTextFingerprint:
    def test_does_not_disclose_the_input(self):
        secret = "Patient reports severe chest pain radiating to the left arm"
        fingerprint = text_fingerprint(secret)
        assert secret not in fingerprint
        assert "chest pain" not in fingerprint

    def test_is_stable_and_distinguishes_inputs(self):
        assert text_fingerprint("cough") == text_fingerprint("cough")
        assert text_fingerprint("cough") != text_fingerprint("fever")

    def test_reports_length_for_truncation_checks(self):
        assert "len=5" in text_fingerprint("cough")

    def test_handles_empty_input(self):
        assert text_fingerprint("") == "empty"
        assert text_fingerprint(None) == "empty"


class TestRedact:
    def test_removes_the_secret(self):
        text = "Model rejected prompt: patient has chest pain"
        assert "chest pain" not in redact(text, "chest pain")

    def test_keeps_surrounding_diagnostics(self):
        text = "Model rejected prompt: patient has chest pain"
        cleaned = redact(text, "chest pain")
        assert "Model rejected prompt" in cleaned
        assert "<redacted>" in cleaned

    def test_ignores_short_secrets_that_would_match_everything(self):
        assert redact("abc def", "a") == "abc def"

    def test_handles_empty_text(self):
        assert redact(None, "secret") == ""


class TestSafeError:
    def test_keeps_the_exception_type(self):
        rendered = safe_error(ValueError("boom"))
        assert "ValueError" in rendered

    def test_scrubs_patient_text(self):
        error = RuntimeError("upstream rejected: chest pain radiating to left arm")
        rendered = safe_error(error, "chest pain radiating to left arm")
        assert "chest pain radiating to left arm" not in rendered
        assert "RuntimeError" in rendered


class TestOrchestratorDoesNotLogPatientText:
    def _orchestrator_with_failing_agents(self):
        from src.agents.orchestrator.agent import OrchestratorAgent

        orch = OrchestratorAgent()

        class _LeakyAgent:
            async def run(self, input_data):
                raise RuntimeError(
                    f"upstream rejected request body: {input_data.get('text', '')}"
                )

        orch.nlp_agent = _LeakyAgent()
        orch.rag_agent = _LeakyAgent()
        orch.prediction_agent = _LeakyAgent()
        orch.synthesis_agent = _LeakyAgent()
        return orch

    def test_symptom_text_is_not_logged(self, captured_logs):
        orch = self._orchestrator_with_failing_agents()
        secret = "PATIENT-DETAIL-9821 severe chest pain"

        asyncio.run(orch.run({"text": secret}))

        joined = "\n".join(captured_logs)
        assert secret not in joined
        assert "PATIENT-DETAIL-9821" not in joined
        # The run is still visible in the logs, just without the content.
        assert "NLP agent" in joined

    def test_voice_transcript_is_not_logged(self, captured_logs):
        orch = self._orchestrator_with_failing_agents()
        secret = "VOICE-DETAIL-4417 wheezing since last night"

        asyncio.run(orch.run({"text": "", "voice_transcript": secret}))

        assert secret not in "\n".join(captured_logs)


class TestRagAgentDoesNotLogTheQuery:
    def test_query_is_logged_as_a_fingerprint(self, captured_logs, monkeypatch):
        from src.agents.rag.agent import RAGAgent

        agent = RAGAgent()
        # Skip the embedding model and the LLM client so the test stays
        # offline and fast; neither affects the log line under test.
        agent.faiss_index = None
        agent.documents = []
        monkeypatch.setattr(agent, "_init_rag_client", lambda: None)
        agent.rag_client = None

        secret = "PATIENT-DETAIL-7734 persistent productive cough"
        asyncio.run(agent.run({"query": secret}))

        joined = "\n".join(captured_logs)
        assert secret not in joined
        assert "RAG retrieval query" in joined
        assert text_fingerprint(secret) in joined


class TestDisplayMetadataMatchesTheRunningPipeline:
    def test_node_display_has_no_stale_model_claims(self):
        from src.agents.display import NODE_DISPLAY

        claims = " ".join(
            f"{meta['agent']} {meta['model']}" for meta in NODE_DISPLAY.values()
        ).lower()
        for stale in ["chestx-ray14", "xgboost", "lstm", "biobert / clinical"]:
            assert stale not in claims, f"Stale claim still advertised: {stale}"

    def test_node_display_is_shared_by_progress_and_orchestrator(self):
        from src.agents.display import NODE_DISPLAY
        from src.agents.orchestrator.agent import NODE_DISPLAY as ORCHESTRATOR_DISPLAY
        from src.api.progress import AGENT_META

        assert ORCHESTRATOR_DISPLAY is NODE_DISPLAY
        assert AGENT_META is NODE_DISPLAY

    def test_progress_events_carry_the_display_metadata(self):
        from src.agents.orchestrator.agent import OrchestratorAgent

        class _StubAgent:
            async def run(self, input_data):
                return {"symptoms": ["cough"], "entities": []}

        orch = OrchestratorAgent()
        # Stub every specialist so the test loads no models and makes no
        # network calls.
        orch.nlp_agent = _StubAgent()
        orch.rag_agent = _StubAgent()
        orch.prediction_agent = _StubAgent()
        orch.synthesis_agent = _StubAgent()

        events: list[dict] = []
        asyncio.run(orch.run({"text": "cough"}, progress_cb=events.append))

        agent_events = [e for e in events if e["type"] == "agent"]
        assert agent_events
        assert all(e.get("agent") and e.get("model") for e in agent_events)


class TestAgentDescriptionsMatchTheImplementation:
    def test_no_agent_claims_a_model_it_does_not_use(self):
        from src.agents.nlp.agent import NLPAgent
        from src.agents.prediction.agent import PredictionAgent
        from src.agents.rag.agent import RAGAgent
        from src.agents.synthesis.agent import GenAIAgent
        from src.agents.vision.agent import VisionAgent

        descriptions = " ".join(
            agent.description
            for agent in (
                NLPAgent, VisionAgent, RAGAgent, PredictionAgent, GenAIAgent,
            )
        ).lower()

        for stale in ["lstm", "gemini 1.5", "tumor", "nemotron 3 super"]:
            assert stale not in descriptions, f"Stale agent description: {stale}"


class TestClinicalPatternExtraction:
    def test_keyword_does_not_match_inside_another_word(self):
        """'ear' inside 'heart' must not raise ENT."""
        from src.agents.nlp.agent import NLPAgent

        systems = NLPAgent()._detect_body_systems("heart palpitations and chest pain")
        assert "cardiovascular" in systems
        assert "ENT" not in systems

    def test_inflected_form_is_still_detected(self):
        from src.agents.nlp.agent import NLPAgent

        systems = NLPAgent()._detect_body_systems("i can't breathe")
        assert "respiratory" in systems

    def test_headache_is_detected_as_neurological(self):
        from src.agents.nlp.agent import NLPAgent

        systems = NLPAgent()._detect_body_systems("severe headache with nausea")
        assert "neurological" in systems

    def test_wheezing_symptom_pattern_matches(self):
        import re

        from src.agents.nlp.agent import NLPAgent

        assert re.search(NLPAgent.SYMPTOM_PATTERNS["respiratory"], "wheezing at night")

    def test_dizziness_symptom_pattern_matches(self):
        import re

        from src.agents.nlp.agent import NLPAgent

        assert re.search(NLPAgent.SYMPTOM_PATTERNS["neurological"], "dizziness")
