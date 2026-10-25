"""Tabular data preprocessing for patient history and vitals."""

from typing import Optional
import numpy as np


class TabularPreprocessor:
    """Normalizes and encodes patient tabular data for ML models."""

    # Clinical reference ranges for vital signs
    VITAL_RANGES = {
        "age": (0, 120),
        "bmi": (10, 60),
        "heart_rate": (40, 200),
        "systolic_bp": (70, 250),
        "diastolic_bp": (40, 150),
        "temperature": (35, 42),
        "respiratory_rate": (8, 40),
        "oxygen_saturation": (70, 100),
        "blood_glucose": (40, 600),
    }

    # Categorical feature mappings
    CATEGORICAL_ENCODINGS = {
        "gender": {"male": 0, "female": 1, "other": 2},
        "smoking_status": {"never": 0, "former": 1, "current": 2},
        "alcohol_use": {"none": 0, "occasional": 1, "moderate": 2, "heavy": 3},
        "exercise_frequency": {"none": 0, "rare": 1, "moderate": 2, "frequent": 3},
        "severity": {"mild": 0, "moderate": 1, "severe": 2, "critical": 3},
    }

    def __init__(self):
        self.feature_names = []
        self.fitted = False

    def normalize_vitals(self, vitals: dict) -> dict:
        """Normalize vital signs to 0-1 range based on clinical ranges.

        Args:
            vitals: Dict with vital sign names and values.

        Returns:
            Dict with normalized values (0-1 scale).
        """
        normalized = {}
        for key, value in vitals.items():
            if key in self.VITAL_RANGES:
                min_val, max_val = self.VITAL_RANGES[key]
                normalized[key] = max(0, min(1, (value - min_val) / (max_val - min_val)))
            else:
                normalized[key] = value
        return normalized

    def encode_categorical(self, value: str, feature: str) -> int:
        """Encode a categorical value to integer.

        Args:
            value: String categorical value.
            feature: Feature name for encoding lookup.

        Returns:
            Encoded integer value.
        """
        if feature in self.CATEGORICAL_ENCODINGS:
            mapping = self.CATEGORICAL_ENCODINGS[feature]
            return mapping.get(value.lower(), 0)
        return 0

    def handle_missing(self, record: dict, defaults: Optional[dict] = None) -> dict:
        """Fill missing values with clinical defaults.

        Args:
            record: Patient record dict (may have missing keys).
            defaults: Custom default values.

        Returns:
            Record with all missing values filled.
        """
        clinical_defaults = {
            "age": 30,
            "bmi": 25.0,
            "heart_rate": 72,
            "systolic_bp": 120,
            "diastolic_bp": 80,
            "temperature": 37.0,
            "respiratory_rate": 16,
            "oxygen_saturation": 98,
            "blood_glucose": 90,
            "gender": "unknown",
            "smoking_status": "never",
            "alcohol_use": "none",
            "exercise_frequency": "moderate",
            "family_history": [],
            "chronic_conditions": [],
        }

        if defaults:
            clinical_defaults.update(defaults)

        for key, default in clinical_defaults.items():
            if key not in record or record[key] is None:
                record[key] = default

        return record

    def build_feature_vector(self, patient: dict) -> np.ndarray:
        """Convert a patient record into a numeric feature vector.

        Args:
            patient: Dict with patient demographics, vitals, history.
                     Supports both flat and nested (vitals, lifestyle) structures.

        Returns:
            Numpy array of features ready for model input.
        """
        patient = self._flatten_patient(patient)
        patient = self.handle_missing(patient)
        features = []
        feature_names = []

        # Numeric vitals (normalized)
        for key in ["age", "bmi", "heart_rate", "systolic_bp", "diastolic_bp",
                     "temperature", "respiratory_rate", "oxygen_saturation", "blood_glucose"]:
            value = patient.get(key, 0)
            if key in self.VITAL_RANGES:
                min_val, max_val = self.VITAL_RANGES[key]
                value = max(0, min(1, (value - min_val) / (max_val - min_val)))
            features.append(value)
            feature_names.append(key)

        # Categorical features (encoded)
        for key in ["gender", "smoking_status", "alcohol_use", "exercise_frequency"]:
            value = patient.get(key, "")
            encoded = self.encode_categorical(str(value), key)
            features.append(encoded)
            feature_names.append(key)

        # Family history flags (binary)
        family_conditions = ["diabetes", "heart disease", "cancer", "hypertension", "asthma"]
        family_history = [f.lower() for f in patient.get("family_history", [])]
        for condition in family_conditions:
            flag = 1 if condition in family_history else 0
            features.append(flag)
            feature_names.append(f"family_{condition.replace(' ', '_')}")

        # Chronic conditions count
        chronic_count = len(patient.get("chronic_conditions", []))
        features.append(min(chronic_count, 5) / 5.0)
        feature_names.append("chronic_condition_count")

        self.feature_names = feature_names
        self.fitted = True

        return np.array(features, dtype=np.float32)

    def _flatten_patient(self, patient: dict) -> dict:
        """Flatten nested patient structure (vitals, lifestyle) into flat dict."""
        flat = {}
        # Top-level fields
        for key in ["age", "bmi", "gender", "family_history", "chronic_conditions"]:
            if key in patient:
                flat[key] = patient[key]
        # Nested vitals
        vitals = patient.get("vitals", {})
        for key in ["heart_rate", "systolic_bp", "diastolic_bp", "temperature",
                     "respiratory_rate", "oxygen_saturation", "blood_glucose"]:
            if key in vitals:
                flat[key] = vitals[key]
            elif key in patient:
                flat[key] = patient[key]
        # Nested lifestyle
        lifestyle = patient.get("lifestyle", {})
        for src_key, flat_key in [("smoking", "smoking_status"), ("alcohol", "alcohol_use"),
                                   ("exercise", "exercise_frequency")]:
            if src_key in lifestyle:
                flat[flat_key] = lifestyle[src_key]
            elif flat_key in patient:
                flat[flat_key] = patient[flat_key]
        return flat

    def fit_transform(self, patients: list[dict]) -> np.ndarray:
        """Fit preprocessor and transform a batch of patient records.

        Args:
            patients: List of patient record dicts.

        Returns:
            2D numpy array (n_patients, n_features).
        """
        vectors = [self.build_feature_vector(p) for p in patients]
        return np.array(vectors)

    def get_feature_names(self) -> list[str]:
        """Return names of features in the output vector."""
        return self.feature_names
