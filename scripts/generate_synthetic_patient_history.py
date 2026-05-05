"""Generate synthetic patient history records for training and testing.

Produces medically plausible patient records with realistic demographics,
vitals, correlated conditions, and family history patterns.
"""

import os
import sys
import json
import random
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger


# Correlated condition patterns (if patient has X, they're more likely to have Y)
CONDITION_CORRELATIONS = {
    "obesity": {"diabetes": 0.5, "hypertension": 0.45, "sleep_apnea": 0.35, "heart_disease": 0.3},
    "hypertension": {"heart_disease": 0.4, "kidney_disease": 0.25, "stroke": 0.2},
    "diabetes": {"heart_disease": 0.35, "kidney_disease": 0.3, "neuropathy": 0.25, "retinopathy": 0.2},
    "smoking": {"copd": 0.3, "lung_cancer": 0.15, "heart_disease": 0.3},
    "high_cholesterol": {"heart_disease": 0.4, "stroke": 0.25},
    "asthma": {"allergies": 0.6, "sinusitis": 0.3, "copd": 0.15},
}

# Normal ranges for vital signs by age group
VITAL_RANGES = {
    "young": {  # 18-35
        "heart_rate": (60, 100),
        "systolic_bp": (90, 120),
        "diastolic_bp": (60, 80),
        "temperature": (36.1, 37.2),
        "respiratory_rate": (12, 20),
        "oxygen_saturation": (95, 100),
        "blood_glucose": (70, 100),
        "bmi": (18.5, 24.9),
    },
    "middle": {  # 36-55
        "heart_rate": (60, 100),
        "systolic_bp": (100, 140),
        "diastolic_bp": (65, 90),
        "temperature": (36.1, 37.2),
        "respiratory_rate": (12, 20),
        "oxygen_saturation": (94, 100),
        "blood_glucose": (70, 110),
        "bmi": (18.5, 29.9),
    },
    "senior": {  # 56+
        "heart_rate": (60, 100),
        "systolic_bp": (110, 160),
        "diastolic_bp": (70, 100),
        "temperature": (36.0, 37.0),
        "respiratory_rate": (12, 24),
        "oxygen_saturation": (92, 100),
        "blood_glucose": (70, 120),
        "bmi": (18.5, 34.9),
    },
}


def get_age_group(age: int) -> str:
    if age <= 35:
        return "young"
    elif age <= 55:
        return "middle"
    return "senior"


def generate_vitals(age: int, has_conditions: list[str]) -> dict:
    """Generate realistic vital signs with condition-based deviations."""
    age_group = get_age_group(age)
    ranges = VITAL_RANGES[age_group].copy()

    # Adjust ranges based on conditions
    if "hypertension" in has_conditions:
        ranges["systolic_bp"] = (130, 180)
        ranges["diastolic_bp"] = (85, 110)
    if "diabetes" in has_conditions:
        ranges["blood_glucose"] = (110, 300)
    if "copd" in has_conditions or "asthma" in has_conditions:
        ranges["oxygen_saturation"] = (88, 96)
        ranges["respiratory_rate"] = (16, 28)
    if "heart_disease" in has_conditions:
        ranges["heart_rate"] = (70, 120)
        ranges["oxygen_saturation"] = (90, 98)
    if "obesity" in has_conditions:
        ranges["bmi"] = (30, 45)
    if "infection" in has_conditions:
        ranges["temperature"] = (37.5, 39.5)
        ranges["heart_rate"] = (80, 120)
    if "anemia" in has_conditions:
        ranges["heart_rate"] = (80, 120)
        ranges["oxygen_saturation"] = (90, 96)

    vitals = {}
    for key, (min_val, max_val) in ranges.items():
        if key in ("temperature", "bmi", "blood_glucose"):
            vitals[key] = round(random.uniform(min_val, max_val), 1)
        else:
            vitals[key] = int(random.uniform(min_val, max_val))

    return vitals


def generate_chronic_conditions(age: int, lifestyle: dict, family_history: list[str]) -> list[str]:
    """Generate chronic conditions based on age, lifestyle, and family history."""
    conditions = []

    # Age-based probabilities
    if age > 50:
        if random.random() < 0.3:
            conditions.append("hypertension")
        if random.random() < 0.2:
            conditions.append("high_cholesterol")
        if random.random() < 0.15:
            conditions.append("diabetes")
    elif age > 35:
        if random.random() < 0.15:
            conditions.append("hypertension")
        if random.random() < 0.1:
            conditions.append("diabetes")

    # Lifestyle-based
    if lifestyle.get("smoking") == "current":
        conditions.append("smoking")
        if random.random() < 0.2 and age > 40:
            conditions.append("copd")
    if lifestyle.get("exercise") == "none" and random.random() < 0.2:
        conditions.append("obesity")

    # Family history influence
    if "diabetes" in family_history and random.random() < 0.4 and age > 30:
        conditions.append("diabetes")
    if "heart disease" in family_history and random.random() < 0.3 and age > 40:
        conditions.append("heart_disease")
    if "asthma" in family_history and random.random() < 0.5:
        conditions.append("asthma")
    if "cancer" in family_history and random.random() < 0.1 and age > 45:
        conditions.append("cancer")

    # Add correlated conditions
    for condition in conditions.copy():
        if condition in CONDITION_CORRELATIONS:
            for correlated, prob in CONDITION_CORRELATIONS[condition].items():
                if correlated not in conditions and random.random() < prob:
                    conditions.append(correlated)

    return list(set(conditions))


def generate_patient_records(n_records: int = 500, output_path: Optional[str] = None) -> str:
    """Generate synthetic patient history records.

    Args:
        n_records: Number of patient records to generate.
        output_path: Where to save the JSON dataset.

    Returns:
        Path to the generated dataset file.
    """
    if output_path is None:
        output_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
            "data", "datasets", "synthetic", "patient_history.json",
        )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    all_diseases = ["diabetes", "heart disease", "cancer", "asthma", "hypertension",
                    "kidney disease", "stroke", "arthritis", "thyroid disorder", "none"]

    records = []
    for i in range(n_records):
        # Demographics
        age = random.choices(
            range(18, 90),
            weights=[1]*10 + [2]*10 + [3]*12 + [4]*12 + [3]*12 + [2]*8 + [1]*8,
            k=1
        )[0]
        gender = random.choice(["male", "female"])

        # Family history (each has independent probability)
        family_history = [d for d in random.sample(all_diseases, random.randint(0, 3)) if d != "none"]

        # Lifestyle
        smoking = random.choices(["never", "former", "current"], weights=[0.6, 0.25, 0.15], k=1)[0]
        alcohol = random.choices(["none", "occasional", "moderate", "heavy"], weights=[0.3, 0.35, 0.25, 0.1], k=1)[0]
        exercise = random.choices(["none", "rare", "moderate", "frequent"], weights=[0.2, 0.3, 0.35, 0.15], k=1)[0]

        lifestyle = {"smoking": smoking, "alcohol": alcohol, "exercise": exercise}

        # Generate chronic conditions
        chronic_conditions = generate_chronic_conditions(age, lifestyle, family_history)

        # Generate vitals based on conditions
        vitals = generate_vitals(age, chronic_conditions)

        record = {
            "id": f"pat-{i+1:05d}",
            "age": age,
            "gender": gender,
            "bmi": vitals["bmi"],
            "vitals": {
                "heart_rate": vitals["heart_rate"],
                "systolic_bp": vitals["systolic_bp"],
                "diastolic_bp": vitals["diastolic_bp"],
                "temperature": vitals["temperature"],
                "respiratory_rate": vitals["respiratory_rate"],
                "oxygen_saturation": vitals["oxygen_saturation"],
                "blood_glucose": vitals["blood_glucose"],
            },
            "family_history": family_history,
            "chronic_conditions": chronic_conditions,
            "lifestyle": lifestyle,
            "risk_level": "high" if len(chronic_conditions) >= 3 else "moderate" if len(chronic_conditions) >= 1 else "low",
        }
        records.append(record)

        if (i + 1) % 100 == 0:
            logger.info(f"Generated {i+1}/{n_records} patient records")

    with open(output_path, "w") as f:
        json.dump(records, f, indent=2)

    logger.info(f"Saved {len(records)} patient records to {output_path}")

    # Print statistics
    ages = [r["age"] for r in records]
    logger.info(f"Age range: {min(ages)}-{max(ages)}, mean: {sum(ages)/len(ages):.1f}")

    condition_counts = {}
    for r in records:
        for c in r["chronic_conditions"]:
            condition_counts[c] = condition_counts.get(c, 0) + 1
    logger.info("Condition distribution:")
    for cond, count in sorted(condition_counts.items(), key=lambda x: -x[1]):
        logger.info(f"  {cond}: {count} ({count/len(records)*100:.1f}%)")

    return output_path


if __name__ == "__main__":
    random.seed(42)
    generate_patient_records(n_records=500)
