"""Phase 2 clinical PDF report endpoint tests."""

from fastapi.testclient import TestClient


def test_report_endpoint_returns_pdf():
    from src.api.main import app

    client = TestClient(app)
    response = client.post(
        "/api/report/generate",
        json={
            "symptom_input": "Cough and fever",
            "age": 35,
            "gender": "female",
            "diagnosis": [{
                "condition": "Pneumonia",
                "confidence": 0.82,
                "icd10_code": "J18.9",
                "rationale": "Fever and productive cough",
            }],
            "severity": "moderate",
            "recommendations": ["Clinical assessment", "Chest X-ray"],
            "red_flags": ["Difficulty breathing"],
            "confidence": {"breakdown": {"nlp": 0.8}},
            "triage": {"entropy_bits": 0.42},
            "execution_trace": [{
                "type": "agent", "agent": "NLP Agent", "status": "completed",
                "elapsed_ms": 42, "summary": "2 symptoms extracted",
            }],
            "disclaimer": "Decision support only.",
        },
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
    assert len(response.content) > 1500
    assert "aegismed-clinical-report.pdf" in response.headers["content-disposition"]
