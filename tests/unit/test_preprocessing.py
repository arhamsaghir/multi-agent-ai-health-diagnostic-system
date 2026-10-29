"""Tests for data preprocessing pipelines."""

import pytest
import numpy as np
from src.data.preprocessing.text_preprocessor import TextPreprocessor
from src.data.preprocessing.tabular_preprocessor import TabularPreprocessor


class TestTextPreprocessor:
    """Test suite for text preprocessing."""

    @pytest.fixture
    def processor(self):
        return TextPreprocessor()

    def test_clean_basic(self, processor):
        result = processor.clean("  Hello   World  ")
        assert result == "hello world"

    def test_clean_empty(self, processor):
        assert processor.clean("") == ""
        assert processor.clean(None) == ""

    def test_clean_remove_special_chars(self, processor):
        result = processor.clean("Hello @world #test!")
        assert "@" not in result
        assert "#" not in result

    def test_expand_abbreviations(self, processor):
        result = processor.expand_abbreviations("I have HTN and DM")
        assert "hypertension" in result
        assert "diabetes mellitus" in result

    def test_expand_sob(self, processor):
        result = processor.expand_abbreviations("patient with SOB")
        assert "shortness of breath" in result

    def test_normalize_symptoms(self, processor):
        result = processor.normalize_symptoms("my head hurts and i'm feverish")
        assert "headache" in result
        assert "fever" in result

    def test_extract_keywords(self, processor):
        keywords = processor.extract_keywords("I have a headache and fever for 3 days")
        assert "headache" in keywords
        assert "fever" in keywords
        assert "days" in keywords

    def test_full_preprocess_pipeline(self, processor):
        result = processor.preprocess("I've been having HA and SOB for 2 wks")
        assert result["original"] == "I've been having HA and SOB for 2 wks"
        assert "headache" in result["normalized"]
        assert "shortness of breath" in result["normalized"]
        assert result["word_count"] > 0

    def test_extract_duration(self, processor):
        assert processor.extract_duration("fever for 3 days") == "3 days"
        assert processor.extract_duration("pain since 2 weeks ago") == "2 weeks"
        assert processor.extract_duration("no duration mentioned") is None

    def test_extract_severity_high(self, processor):
        result = processor.extract_severity_indicators("severe unbearable pain")
        assert result["severe"] is True
        assert result["moderate"] is False

    def test_extract_severity_moderate(self, processor):
        result = processor.extract_severity_indicators("moderate discomfort")
        assert result["moderate"] is True


class TestAssertionAwareNormalization:
    """The polarity map must not create symptoms the patient denied (R6/R7)."""

    @pytest.fixture
    def processor(self):
        return TextPreprocessor()

    def test_no_appetite_is_not_blindly_rewritten(self, processor):
        result = processor.normalize_symptoms("no appetite")
        assert "decreased appetite" not in result

    def test_negated_variant_preserves_negation(self, processor):
        result = processor.normalize_symptoms("no loss of appetite")
        assert "decreased appetite" not in result
        assert "loss of appetite" in result

    def test_affirmative_canonicalization_still_applies(self, processor):
        result = processor.normalize_symptoms("i have loss of appetite")
        assert "decreased appetite" in result

    def test_without_is_not_a_stop_word(self):
        assert "without" not in TextPreprocessor.STOP_WORDS

    def test_without_survives_keyword_extraction(self, processor):
        keywords = processor.extract_keywords("chest pain without fever")
        assert "without" in keywords


class TestTabularPreprocessor:
    """Test suite for tabular data preprocessing."""

    @pytest.fixture
    def processor(self):
        return TabularPreprocessor()

    def test_normalize_vitals(self, processor):
        vitals = {"age": 60, "bmi": 25.0, "heart_rate": 80}
        normalized = processor.normalize_vitals(vitals)
        assert 0 <= normalized["age"] <= 1
        assert 0 <= normalized["bmi"] <= 1
        assert 0 <= normalized["heart_rate"] <= 1

    def test_handle_missing(self, processor):
        record = {"age": 45, "bmi": None}
        filled = processor.handle_missing(record)
        assert filled["age"] == 45
        assert filled["bmi"] == 25.0  # default

    def test_encode_categorical(self, processor):
        assert processor.encode_categorical("male", "gender") == 0
        assert processor.encode_categorical("female", "gender") == 1
        assert processor.encode_categorical("current", "smoking_status") == 2

    def test_build_feature_vector(self, processor):
        patient = {
            "age": 50,
            "bmi": 28.0,
            "heart_rate": 78,
            "systolic_bp": 130,
            "diastolic_bp": 85,
            "temperature": 37.0,
            "respiratory_rate": 16,
            "oxygen_saturation": 97,
            "blood_glucose": 95,
            "gender": "male",
            "smoking_status": "former",
            "alcohol_use": "occasional",
            "exercise_frequency": "moderate",
            "family_history": ["diabetes", "heart disease"],
            "chronic_conditions": ["hypertension"],
        }
        vector = processor.build_feature_vector(patient)
        assert vector.shape[0] > 0
        assert len(processor.get_feature_names()) == vector.shape[0]

    def test_fit_transform_batch(self, processor):
        patients = [
            {"age": 30, "bmi": 22, "gender": "female", "family_history": [], "chronic_conditions": []},
            {"age": 65, "bmi": 30, "gender": "male", "family_history": ["diabetes"], "chronic_conditions": ["hypertension"]},
        ]
        matrix = processor.fit_transform(patients)
        assert matrix.shape[0] == 2
        assert matrix.shape[1] > 0
