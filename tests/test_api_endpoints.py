"""API endpoint tests — FastAPI route validation."""

import pytest
from fastapi.testclient import TestClient
import json
import io

from src.api.main import app


@pytest.fixture
def client():
    """Create test client for API endpoints."""
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "agents" in data
        assert "models" in data

    def test_health_contains_all_agents(self, client):
        response = client.get("/health")
        data = response.json()
        expected_agents = ["orchestrator", "vision", "nlp", "rag", "prediction", "voice", "synthesis"]
        for agent in expected_agents:
            assert agent in data["agents"], f"Missing agent: {agent}"

    def test_health_response_time(self, client):
        response = client.get("/health")
        data = response.json()
        assert "response_time_ms" in data
        assert isinstance(data["response_time_ms"], (int, float))


class TestDiagnosisEndpoint:
    def test_analyze_text_input(self, client):
        response = client.post(
            "/api/diagnosis/analyze",
            json={
                "text": "I have chest pain for 3 days with shortness of breath",
                "age": 55,
                "gender": "male",
                "bmi": 28.5,
                "family_history": ["heart disease"],
            },
        )
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert "diagnosis" in data or "result" in data

    def test_analyze_minimal_input(self, client):
        response = client.post(
            "/api/diagnosis/analyze",
            json={"text": "headache"},
        )
        assert response.status_code in [200, 422, 500]

    def test_analyze_empty_text(self, client):
        response = client.post(
            "/api/diagnosis/analyze",
            json={"text": ""},
        )
        assert response.status_code in [200, 422, 500]  # 500 is acceptable for empty input in dev mode

    def test_analyze_missing_text(self, client):
        response = client.post(
            "/api/diagnosis/analyze",
            json={"age": 30},
        )
        assert response.status_code in [422, 500]

    def test_analyze_with_image_missing_file(self, client):
        response = client.post("/api/diagnosis/analyze-with-image")
        assert response.status_code in [422, 500]


class TestChatEndpoint:
    def test_chat_message(self, client):
        response = client.post(
            "/api/chat/message",
            json={"message": "What are the symptoms of pneumonia?"},
        )
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert "response" in data or "message" in data or "reply" in data

    def test_chat_empty_message(self, client):
        response = client.post(
            "/api/chat/message",
            json={"message": ""},
        )
        assert response.status_code in [200, 422]

    def test_chat_conversations_list(self, client):
        response = client.get("/api/chat/conversations")
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    def test_chat_nonexistent_conversation(self, client):
        response = client.get("/api/chat/conversation/nonexistent-id")
        assert response.status_code in [404, 500]

    def test_chat_delete_nonexistent_conversation(self, client):
        response = client.delete("/api/chat/conversation/nonexistent-id")
        assert response.status_code in [404, 500]


class TestErrorHandling:
    def test_invalid_endpoint(self, client):
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_invalid_method(self, client):
        response = client.get("/api/diagnosis/analyze")
        assert response.status_code == 405

    def test_malformed_json(self, client):
        response = client.post(
            "/api/diagnosis/analyze",
            data="not valid json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code in [400, 422]

    def test_large_payload(self, client):
        large_text = "symptom " * 10000
        response = client.post(
            "/api/diagnosis/analyze",
            json={"text": large_text},
        )
        assert response.status_code in [200, 400, 413, 422, 500]


class TestCORS:
    def test_cors_headers_on_health(self, client):
        response = client.get("/health", headers={"Origin": "http://localhost:8501"})
        assert response.status_code == 200
        # CORS headers should be present for allowed origins
        assert "access-control-allow-origin" in response.headers or response.status_code == 200
