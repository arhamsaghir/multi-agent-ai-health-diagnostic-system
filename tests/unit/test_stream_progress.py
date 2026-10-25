"""Tests for the live execution streaming layer (SSE + progress bus)."""

import asyncio
import json
import re

import pytest
from fastapi.testclient import TestClient

from src.api.progress import (
    RunEventBus,
    event_bus,
    make_progress_cb,
    format_sse,
    stream_run_events,
)
from src.agents.orchestrator.agent import OrchestratorAgent


@pytest.fixture
def client():
    """FastAPI test client (mirrors tests/test_api_endpoints.py)."""
    from src.api.main import app
    return TestClient(app)


# ---------------------------------------------------------------------------
# RunEventBus
# ---------------------------------------------------------------------------

class TestRunEventBus:
    def test_publish_and_history(self):
        bus = RunEventBus()
        bus.create("r1")
        bus.publish("r1", {"type": "agent", "node": "symptoms", "status": "started"})
        bus.publish("r1", {"type": "agent", "node": "symptoms", "status": "completed"})
        hist = bus.history("r1")
        assert [e["status"] for e in hist] == ["started", "completed"]
        assert all("ts" in e for e in hist)

    def test_publish_unknown_run_is_ignored(self):
        bus = RunEventBus()
        bus.publish("nope", {"type": "agent"})  # must not raise

    def test_close_blocks_further_publishes(self):
        bus = RunEventBus()
        bus.create("r2")
        bus.close("r2")
        bus.publish("r2", {"type": "agent"})
        assert bus.history("r2") == []


class TestFormatSSE:
    def test_frame_shape(self):
        frame = format_sse({"type": "agent", "node": "knowledge", "status": "started"})
        assert frame.startswith("event: agent\n")
        assert frame.endswith("\n\n")
        data_line = [l for l in frame.split("\n") if l.startswith("data:")][0]
        payload = json.loads(data_line[5:].strip())
        assert payload["node"] == "knowledge"


# ---------------------------------------------------------------------------
# Orchestrator progress callbacks
# ---------------------------------------------------------------------------

class _StubAgent:
    """Async stub sub-agent — returns canned output, no model loading."""

    def __init__(self, output):
        self._output = output

    async def run(self, input_data):
        return dict(self._output)


def _stubbed_orchestrator() -> OrchestratorAgent:
    orch = OrchestratorAgent()
    orch.nlp_agent = _StubAgent({"symptoms": ["cough", "fever"], "entities": []})
    orch.rag_agent = _StubAgent({"relevant_docs": [{}], "knowledge": "k", "sources": 1})
    orch.prediction_agent = _StubAgent({"risk_scores": {"respiratory_infection": 0.4}, "severity": "low"})
    orch.synthesis_agent = _StubAgent({
        "diagnosis": [{"condition": "URI", "confidence": 0.7}],
        "explanation": "stub",
        "recommendations": [],
        "severity": "low",
        "doctor_alert": False,
        "confidence": {"overall_confidence": 0.7},
        "disclaimer": "stub",
    })
    return orch


class TestOrchestratorProgressEvents:
    def test_events_emitted_in_order(self):
        orch = _stubbed_orchestrator()
        events: list[dict] = []
        asyncio.run(orch.run(
            {"text": "cough and fever", "patient_history": {"age": 30}},
            progress_cb=events.append,
        ))

        types = [e["type"] for e in events]
        assert types[0] == "planned"

        agent_events = [e for e in events if e["type"] == "agent"]
        nodes_in_order = []
        for e in agent_events:
            if e["status"] == "started":
                nodes_in_order.append(e["node"])
            assert (not nodes_in_order) or e["node"] == nodes_in_order[-1]

        # Expected node sequence: symptoms, knowledge, risk, synthesis
        assert nodes_in_order == ["symptoms", "knowledge", "risk", "synthesis"]
        completed = [e for e in agent_events if e["status"] == "completed"]
        assert len(completed) == 4
        assert all("elapsed_ms" in e for e in completed)
        assert any("2 symptom(s)" in (e.get("summary") or "") for e in completed)

    def test_no_callback_no_events_but_same_result(self):
        orch = _stubbed_orchestrator()
        result = asyncio.run(orch.run({"text": "cough"}))
        assert "synthesis_result" in result

    def test_failed_node_emits_failed_status(self):
        orch = _stubbed_orchestrator()

        class _ExplodingAgent:
            async def run(self, input_data):
                raise RuntimeError("boom")

        orch.rag_agent = _ExplodingAgent()
        events: list[dict] = []
        asyncio.run(orch.run({"text": "cough"}, progress_cb=events.append))

        rag_events = [e for e in events if e.get("node") == "knowledge"]
        assert any(e["status"] == "failed" for e in rag_events)
        # Synthesis still runs after a failed node
        assert any(e.get("node") == "synthesis" and e["status"] == "completed" for e in events)


# ---------------------------------------------------------------------------
# SSE endpoint (streaming HTTP)
# ---------------------------------------------------------------------------

def _consume_stream(response) -> list[dict]:
    """Parse an httpx streaming response into a list of SSE event dicts."""
    raw = b"".join(response.iter_bytes()).decode()
    events = []
    for frame in raw.split("\n\n"):
        frame = frame.strip()
        if not frame or frame.startswith(":"):
            continue
        data_lines = [l[5:].strip() for l in frame.split("\n") if l.startswith("data:")]
        if data_lines:
            events.append(json.loads(data_lines[0]))
    return events


class TestAnalyzeStreamEndpoint:
    def test_stream_emits_progress_then_result(self, client, monkeypatch):
        import src.api.routes.diagnosis as diag_module

        class _StubOrchestrator:
            async def run(self, input_data, progress_cb=None):
                if progress_cb:
                    progress_cb({"type": "planned", "tasks": ["symptoms"]})
                    progress_cb({
                        "type": "agent", "node": "symptoms", "agent": "NLP Agent",
                        "model": "stub", "status": "started",
                    })
                    progress_cb({
                        "type": "agent", "node": "symptoms", "agent": "NLP Agent",
                        "model": "stub", "status": "completed",
                        "elapsed_ms": 5.0, "summary": "1 symptom(s) extracted",
                    })
                return {
                    "symptoms": ["cough"],
                    "synthesis_result": {
                        "diagnosis": [{"condition": "URI", "confidence": 0.7}],
                        "explanation": "stub",
                        "patient_explanation": "stub patient",
                        "recommendations": ["rest"],
                        "severity": "low",
                        "doctor_alert": False,
                        "differential_diagnoses": ["URI"],
                        "red_flags": [],
                        "confidence": {"overall_confidence": 0.7},
                        "disclaimer": "stub",
                    },
                }

        monkeypatch.setattr(diag_module, "_orchestrator", _StubOrchestrator())

        payload = {"text": "I have a cough", "patient_history": {"age": 30, "bmi": 22, "gender": "male", "family_history": []}}
        with client.stream("POST", "/api/diagnosis/analyze-stream", json=payload) as response:
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("text/event-stream")
            events = _consume_stream(response)

        types = [e["type"] for e in events]
        assert types[0] == "run_started"
        assert "planned" in types
        assert "result" in types
        assert types[-1] == "result"

        result_payload = events[-1]["data"]
        assert result_payload["diagnosis"][0]["condition"] == "URI"
        assert result_payload["severity"] == "low"

        started = [e for e in events if e.get("status") == "started"]
        completed = [e for e in events if e.get("status") == "completed"]
        assert started and completed
        assert types.index("planned") < types.index("agent")

    def test_stream_error_emits_error_frame(self, client, monkeypatch):
        import src.api.routes.diagnosis as diag_module

        class _BrokenOrchestrator:
            async def run(self, input_data, progress_cb=None):
                raise RuntimeError("pipeline exploded")

        monkeypatch.setattr(diag_module, "_orchestrator", _BrokenOrchestrator())

        payload = {"text": "anything"}
        with client.stream("POST", "/api/diagnosis/analyze-stream", json=payload) as response:
            assert response.status_code == 200
            raw = b"".join(response.iter_bytes()).decode()

        assert "event: error" in raw
        assert "pipeline exploded" in raw


class TestRefineStreamEndpoint:
    def test_refine_stream_emits_result(self, client, monkeypatch):
        import src.api.routes.diagnosis as diag_module

        class _StubOrchestrator:
            async def run(self, input_data, progress_cb=None):
                if progress_cb:
                    progress_cb({"type": "planned", "tasks": ["symptoms", "knowledge"]})
                return {
                    "symptoms": ["cough"],
                    "synthesis_result": {
                        "diagnosis": [{"condition": "Bronchitis", "confidence": 0.6}],
                        "explanation": "stub",
                        "patient_explanation": "stub patient",
                        "recommendations": [],
                        "severity": "moderate",
                        "doctor_alert": False,
                        "differential_diagnoses": ["Bronchitis"],
                        "red_flags": [],
                        "confidence": {"overall_confidence": 0.6},
                        "disclaimer": "stub",
                    },
                }

        monkeypatch.setattr(diag_module, "_orchestrator", _StubOrchestrator())

        payload = {
            "text": "cough",
            "follow_up_answers": [{"id": "q1", "question": "Fever?", "answer": "Yes"}],
            "session_id": "",
        }
        with client.stream("POST", "/api/diagnosis/refine-stream", json=payload) as response:
            assert response.status_code == 200
            events = _consume_stream(response)

        types = [e["type"] for e in events]
        assert "run_started" in types
        assert types[-1] == "result"
        assert events[-1]["data"]["diagnosis"][0]["condition"] == "Bronchitis"


# ---------------------------------------------------------------------------
# stream_run_events generator (unit-level)
# ---------------------------------------------------------------------------

class TestStreamRunEvents:
    def test_terminal_result_frame(self):
        async def _run():
            bus = event_bus
            bus.create("unit-run")
            cb = make_progress_cb("unit-run")

            async def work():
                cb({"type": "agent", "node": "symptoms", "status": "completed"})
                return {"ok": True}

            task = asyncio.create_task(work())
            frames = [f async for f in stream_run_events("unit-run", task, keepalive_seconds=0.2)]
            return frames

        frames = asyncio.run(_run())
        assert frames[-1].startswith("event: result")
        payload = json.loads(re.search(r"data: (.+)", frames[-1]).group(1))
        assert payload["data"] == {"ok": True}
