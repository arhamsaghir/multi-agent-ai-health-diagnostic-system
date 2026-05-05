"""Train an XGBoost prediction model on synthetic patient data.

Uses the synthetic patient history dataset to train a model that predicts
disease risk from patient demographics, vitals, and history.
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from loguru import logger
from config import settings
from src.data.preprocessing.tabular_preprocessor import TabularPreprocessor


DISEASE_TARGETS = ["cardiovascular_disease", "respiratory_infection", "diabetes", "neurological_disorder"]


def generate_training_data(n_samples: int = 500):
    """Generate training data from synthetic patient records with disease labels."""
    import random
    random.seed(42)

    patients = []
    labels = []

    for i in range(n_samples):
        age = random.randint(18, 85)
        gender = random.choice([0, 1])
        bmi = round(random.uniform(16, 45), 1)
        heart_rate = random.randint(50, 120)
        systolic_bp = random.randint(80, 200)
        diastolic_bp = random.randint(50, 120)
        temperature = round(random.uniform(35.5, 40.5), 1)
        respiratory_rate = random.randint(10, 30)
        oxygen_saturation = random.randint(85, 100)
        blood_glucose = random.randint(50, 350)

        smoking = random.choice([0, 1, 2])
        alcohol = random.choice([0, 1, 2, 3])
        exercise = random.choice([0, 1, 2, 3])

        family_history = []
        if random.random() < 0.3:
            family_history.append("diabetes")
        if random.random() < 0.25:
            family_history.append("heart disease")
        if random.random() < 0.15:
            family_history.append("cancer")
        if random.random() < 0.2:
            family_history.append("asthma")
        if random.random() < 0.25:
            family_history.append("hypertension")

        chronic = []
        if random.random() < 0.2 and age > 40:
            chronic.append("hypertension")
        if random.random() < 0.15:
            chronic.append("obesity")
        if random.random() < 0.1 and age > 50:
            chronic.append("diabetes")

        patient = {
            "age": age,
            "bmi": bmi,
            "heart_rate": heart_rate,
            "systolic_bp": systolic_bp,
            "diastolic_bp": diastolic_bp,
            "temperature": temperature,
            "respiratory_rate": respiratory_rate,
            "oxygen_saturation": oxygen_saturation,
            "blood_glucose": blood_glucose,
            "gender": gender,
            "smoking_status": ["never", "former", "current"][smoking],
            "alcohol_use": ["none", "occasional", "moderate", "heavy"][alcohol],
            "exercise_frequency": ["none", "rare", "moderate", "frequent"][exercise],
            "family_history": family_history,
            "chronic_conditions": chronic,
        }

        # Generate disease labels based on patient characteristics
        cardio_risk = 0.0
        if age > 60:
            cardio_risk += 0.3
        if bmi > 30:
            cardio_risk += 0.2
        if "heart disease" in family_history:
            cardio_risk += 0.2
        if systolic_bp > 140:
            cardio_risk += 0.2
        if smoking == 2:
            cardio_risk += 0.15

        resp_risk = 0.0
        if respiratory_rate > 20:
            resp_risk += 0.3
        if oxygen_saturation < 95:
            resp_risk += 0.3
        if temperature > 38:
            resp_risk += 0.2
        if "asthma" in family_history:
            resp_risk += 0.2

        diabetes_risk = 0.0
        if age > 50:
            diabetes_risk += 0.2
        if bmi > 30:
            diabetes_risk += 0.3
        if "diabetes" in family_history:
            diabetes_risk += 0.25
        if blood_glucose > 120:
            diabetes_risk += 0.2

        neuro_risk = 0.0
        if age > 65:
            neuro_risk += 0.2
        if oxygen_saturation < 92:
            neuro_risk += 0.2
        if "stroke" in family_history or "cancer" in family_history:
            neuro_risk += 0.15

        label = [
            1 if cardio_risk > random.random() else 0,
            1 if resp_risk > random.random() else 0,
            1 if diabetes_risk > random.random() else 0,
            1 if neuro_risk > random.random() else 0,
        ]

        patients.append(patient)
        labels.append(label)

    return patients, np.array(labels)


def train_prediction_model_from_file(data_path: str, n_samples: int = 500, output_path: str = None):
    """Train XGBoost model from existing synthetic patient data file.

    Args:
        data_path: Path to patient_history.json.
        n_samples: Number of samples to use (0 = all).
        output_path: Where to save the trained model.
    """
    if output_path is None:
        output_path = settings.prediction_model_path

    logger.info("=" * 60)
    logger.info("Training Prediction Model — XGBoost on synthetic patient data")
    logger.info("=" * 60)

    with open(data_path, "r") as f:
        records = json.load(f)

    if n_samples > 0:
        records = records[:n_samples]

    # Generate labels based on patient characteristics
    patients = []
    labels = []
    import random
    random.seed(42)

    for record in records:
        patient = {
            "age": record["age"],
            "bmi": record["bmi"],
            "heart_rate": record["vitals"]["heart_rate"],
            "systolic_bp": record["vitals"]["systolic_bp"],
            "diastolic_bp": record["vitals"]["diastolic_bp"],
            "temperature": record["vitals"]["temperature"],
            "respiratory_rate": record["vitals"]["respiratory_rate"],
            "oxygen_saturation": record["vitals"]["oxygen_saturation"],
            "blood_glucose": record["vitals"]["blood_glucose"],
            "gender": record["gender"],
            "smoking_status": record["lifestyle"]["smoking"],
            "alcohol_use": record["lifestyle"]["alcohol"],
            "exercise_frequency": record["lifestyle"]["exercise"],
            "family_history": record["family_history"],
            "chronic_conditions": record["chronic_conditions"],
        }

        chronic = record["chronic_conditions"]

        cardio = 1 if any(c in chronic for c in ["heart_disease", "hypertension", "stroke"]) else 0
        resp = 1 if any(c in chronic for c in ["copd", "asthma", "sinusitis"]) else 0
        diabetes = 1 if "diabetes" in chronic else 0
        neuro = 1 if any(c in chronic for c in ["neuropathy", "stroke"]) else 0

        # Add some noise for more realistic training
        if cardio == 0 and record["vitals"]["systolic_bp"] > 140 and random.random() < 0.3:
            cardio = 1
        if resp == 0 and record["vitals"]["oxygen_saturation"] < 94 and random.random() < 0.3:
            resp = 1
        if diabetes == 0 and record["vitals"]["blood_glucose"] > 120 and random.random() < 0.2:
            diabetes = 1

        patients.append(patient)
        labels.append([cardio, resp, diabetes, neuro])

    labels = np.array(labels)
    logger.info(f"Loaded {len(patients)} patient records with labels")

    # Preprocess features
    preprocessor = TabularPreprocessor()
    X = preprocessor.fit_transform(patients)
    feature_names = preprocessor.get_feature_names()
    y = labels

    logger.info(f"Feature matrix: {X.shape}")
    logger.info(f"Features: {feature_names}")

    for i, disease in enumerate(DISEASE_TARGETS):
        n_positive = sum(y[:, i])
        logger.info(f"  {disease}: {n_positive} positive ({n_positive/len(patients)*100:.1f}%)")

    # Train one model per disease
    models = {}
    results = {}

    for i, disease in enumerate(DISEASE_TARGETS):
        logger.info(f"\nTraining model for: {disease}")

        # Handle edge case where all labels are same class
        if len(set(y[:, i])) < 2:
            logger.warning(f"  Skipping {disease} — only one class present")
            continue

        X_train, X_test, y_train, y_test = train_test_split(
            X, y[:, i], test_size=0.2, random_state=42, stratify=y[:, i]
        )

        model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8,
            random_state=42,
        )

        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        results[disease] = {"accuracy": round(accuracy, 4)}

        logger.info(f"  Accuracy: {accuracy:.4f}")
        models[disease] = model

    # Save all models using joblib (avoids pickle/xgboost segfault on Python 3.13)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    model_dir = os.path.dirname(output_path)
    model_basename = os.path.splitext(os.path.basename(output_path))[0]

    import joblib
    metadata = {
        "feature_names": feature_names,
        "results": results,
        "n_samples": len(patients),
        "diseases": list(models.keys()),
        "model_format": "joblib",
    }

    for disease, model in models.items():
        model_path = os.path.join(model_dir, f"{model_basename}_{disease}.joblib")
        joblib.dump(model, model_path)
        logger.info(f"  Saved {disease} model to {model_path}")

    # Save metadata as JSON
    meta_path = os.path.join(model_dir, f"{model_basename}_metadata.json")
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"\nModel metadata saved to {meta_path}")

    logger.info("\n" + "=" * 60)
    logger.info("Training Results Summary")
    logger.info("=" * 60)
    for disease, metrics in results.items():
        logger.info(f"  {disease}: accuracy={metrics['accuracy']}")

    return metadata


if __name__ == "__main__":
    # Try to use the generated synthetic patient data first
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    synthetic_path = os.path.join(base_dir, "data", "datasets", "synthetic", "patient_history.json")
    if os.path.exists(synthetic_path):
        logger.info(f"Using synthetic patient data from {synthetic_path}")
        train_prediction_model_from_file(synthetic_path, n_samples=500)
    else:
        logger.info("No synthetic data found — generating training data on the fly")
        train_prediction_model(n_samples=500)
