"""Tests for report export functionality."""

import pytest
from src.utils.report_exporter import (
    generate_csv_report,
    generate_pdf_report,
    generate_text_report,
)


@pytest.fixture
def sample_result():
    return {
        "symptom_input": "Chest pain for 2 days with shortness of breath",
        "age": 55,
        "gender": "Male",
        "bmi": 28.5,
        "severity": "severe",
        "severity_action": "Seek emergency care immediately",
        "diagnosis": [
            {
                "condition": "Cardiovascular Disease",
                "confidence": 0.85,
                "icd10_code": "I25.1",
                "rationale": "Chest pain with radiation to left arm.",
            },
            {
                "condition": "Angina",
                "confidence": 0.72,
                "icd10_code": "I20.9",
                "rationale": "Pressure-like chest pain triggered by exertion.",
            },
        ],
        "red_flags": ["Chest pain radiating to left arm", "Shortness of breath on exertion"],
        "symptoms": [
            {"symptom": "Chest pain", "category": "Cardiovascular"},
            {"symptom": "Shortness of breath", "category": "Respiratory"},
        ],
        "confidence": {
            "breakdown": {
                "nlp": 0.9,
                "rag": 0.8,
                "prediction": 0.85,
                "vision": 0.7,
            }
        },
        "recommendations": [
            "Seek emergency medical care immediately",
            "Do not drive yourself to the hospital",
        ],
        "explanation": "The symptoms strongly suggest a cardiovascular condition.",
        "patient_explanation": "Your chest pain may indicate a heart-related issue.",
        "disclaimer": "This is not medical advice.",
    }


class TestCSVReport:
    def test_csv_generates_bytes(self, sample_result):
        csv_bytes = generate_csv_report(sample_result)
        assert isinstance(csv_bytes, bytes)
        assert len(csv_bytes) > 100

    def test_csv_contains_header(self, sample_result):
        csv_bytes = generate_csv_report(sample_result)
        text = csv_bytes.decode("utf-8")
        assert "Multi-Agent AI Health Diagnostic Report" in text
        assert "INPUT DATA" in text
        assert "DIAGNOSES" in text

    def test_csv_contains_diagnoses(self, sample_result):
        csv_bytes = generate_csv_report(sample_result)
        text = csv_bytes.decode("utf-8")
        assert "Cardiovascular Disease" in text
        assert "Angina" in text
        assert "85%" in text
        assert "72%" in text

    def test_csv_empty_result(self):
        csv_bytes = generate_csv_report({})
        assert isinstance(csv_bytes, bytes)
        assert len(csv_bytes) > 0


class TestPDFReport:
    def test_pdf_generates_bytes(self, sample_result):
        pdf_bytes = generate_pdf_report(sample_result)
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 100

    def test_pdf_is_valid_format(self, sample_result):
        pdf_bytes = generate_pdf_report(sample_result)
        assert pdf_bytes.startswith(b"%PDF")

    def test_pdf_empty_result(self):
        pdf_bytes = generate_pdf_report({})
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0


class TestTextReport:
    def test_text_generates_string(self, sample_result):
        text = generate_text_report(sample_result)
        assert isinstance(text, str)
        assert len(text) > 100

    def test_text_contains_sections(self, sample_result):
        text = generate_text_report(sample_result)
        assert "MULTI-AGENT AI HEALTH DIAGNOSTIC REPORT" in text
        assert "PATIENT INFORMATION" in text
        assert "POSSIBLE CONDITIONS" in text
        assert "RED FLAGS" in text
        assert "RECOMMENDATIONS" in text

    def test_text_empty_result(self):
        text = generate_text_report({})
        assert isinstance(text, str)
        assert len(text) > 0
