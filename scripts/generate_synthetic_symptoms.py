"""Generate synthetic symptom-disease pairs for training and testing.

Produces medically plausible symptom clusters based on real disease profiles
from clinical guidelines.
"""

import os
import sys
import json
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from loguru import logger

# Disease profiles with medically accurate symptom clusters
DISEASE_PROFILES = {
    "Upper Respiratory Infection": {
        "symptoms": ["cough", "runny nose", "sore throat", "nasal congestion", "fever", "fatigue", "headache", "sneezing"],
        "core_symptoms": ["cough", "runny nose", "sore throat"],
        "frequency": 0.15,
        "severity_range": ("mild", "moderate"),
        "duration_range": (3, 14),
        "body_systems": ["respiratory"],
    },
    "Pneumonia": {
        "symptoms": ["cough", "fever", "shortness of breath", "chest pain", "fatigue", "nausea", "chills", "confusion"],
        "core_symptoms": ["cough", "fever", "shortness of breath"],
        "frequency": 0.06,
        "severity_range": ("moderate", "severe"),
        "duration_range": (5, 21),
        "body_systems": ["respiratory"],
    },
    "Migraine": {
        "symptoms": ["headache", "nausea", "sensitivity to light", "sensitivity to sound", "dizziness", "visual disturbances"],
        "core_symptoms": ["headache", "nausea"],
        "frequency": 0.08,
        "severity_range": ("moderate", "severe"),
        "duration_range": (4, 72),
        "body_systems": ["neurological"],
    },
    "Tension Headache": {
        "symptoms": ["headache", "neck pain", "fatigue", "difficulty concentrating"],
        "core_symptoms": ["headache"],
        "frequency": 0.12,
        "severity_range": ("mild", "moderate"),
        "duration_range": (1, 7),
        "body_systems": ["neurological"],
    },
    "Gastroenteritis": {
        "symptoms": ["nausea", "vomiting", "diarrhea", "abdominal pain", "fever", "dehydration", "fatigue"],
        "core_symptoms": ["nausea", "diarrhea", "abdominal pain"],
        "frequency": 0.07,
        "severity_range": ("mild", "moderate"),
        "duration_range": (1, 7),
        "body_systems": ["gastrointestinal"],
    },
    "Type 2 Diabetes": {
        "symptoms": ["increased thirst", "frequent urination", "fatigue", "blurred vision", "slow healing", "weight loss", "tingling in hands"],
        "core_symptoms": ["increased thirst", "frequent urination", "fatigue"],
        "frequency": 0.05,
        "severity_range": ("mild", "moderate"),
        "duration_range": (30, 365),
        "body_systems": ["endocrine"],
    },
    "Hypertension": {
        "symptoms": ["headache", "dizziness", "chest pain", "shortness of breath", "nosebleeds", "fatigue"],
        "core_symptoms": ["headache", "dizziness"],
        "frequency": 0.08,
        "severity_range": ("mild", "severe"),
        "duration_range": (90, 3650),
        "body_systems": ["cardiovascular"],
    },
    "Asthma": {
        "symptoms": ["shortness of breath", "wheezing", "chest tightness", "cough", "difficulty breathing"],
        "core_symptoms": ["shortness of breath", "wheezing"],
        "frequency": 0.05,
        "severity_range": ("moderate", "severe"),
        "duration_range": (7, 3650),
        "body_systems": ["respiratory"],
    },
    "Urinary Tract Infection": {
        "symptoms": ["burning during urination", "frequent urination", "abdominal pain", "cloudy urine", "fever", "back pain"],
        "core_symptoms": ["burning during urination", "frequent urination"],
        "frequency": 0.05,
        "severity_range": ("mild", "moderate"),
        "duration_range": (1, 14),
        "body_systems": ["urological"],
    },
    "Anxiety Disorder": {
        "symptoms": ["racing heart", "shortness of breath", "sweating", "trembling", "dizziness", "difficulty sleeping", "nausea", "feeling of dread"],
        "core_symptoms": ["racing heart", "difficulty sleeping", "feeling of dread"],
        "frequency": 0.06,
        "severity_range": ("mild", "severe"),
        "duration_range": (30, 3650),
        "body_systems": ["psychiatric", "neurological"],
    },
    "Depression": {
        "symptoms": ["fatigue", "difficulty sleeping", "decreased appetite", "difficulty concentrating", "feelings of worthlessness", "body pain", "headache"],
        "core_symptoms": ["fatigue", "difficulty sleeping", "feelings of worthlessness"],
        "frequency": 0.06,
        "severity_range": ("moderate", "severe"),
        "duration_range": (14, 3650),
        "body_systems": ["psychiatric"],
    },
    "Acute Coronary Syndrome": {
        "symptoms": ["chest pain", "shortness of breath", "sweating", "nausea", "pain radiating to arm", "dizziness", "fatigue"],
        "core_symptoms": ["chest pain", "shortness of breath"],
        "frequency": 0.02,
        "severity_range": ("severe", "critical"),
        "duration_range": (0.5, 12),
        "body_systems": ["cardiovascular"],
    },
    "Bronchitis": {
        "symptoms": ["cough", "mucus production", "fatigue", "shortness of breath", "chest discomfort", "fever"],
        "core_symptoms": ["cough", "mucus production"],
        "frequency": 0.04,
        "severity_range": ("mild", "moderate"),
        "duration_range": (7, 21),
        "body_systems": ["respiratory"],
    },
    "Sinusitis": {
        "symptoms": ["nasal congestion", "facial pain", "headache", "runny nose", "decreased sense of smell", "fever"],
        "core_symptoms": ["nasal congestion", "facial pain", "headache"],
        "frequency": 0.04,
        "severity_range": ("mild", "moderate"),
        "duration_range": (7, 28),
        "body_systems": ["respiratory"],
    },
    "Anemia": {
        "symptoms": ["fatigue", "weakness", "shortness of breath", "dizziness", "pale skin", "cold hands", "headache"],
        "core_symptoms": ["fatigue", "weakness", "pale skin"],
        "frequency": 0.03,
        "severity_range": ("mild", "moderate"),
        "duration_range": (30, 3650),
        "body_systems": ["hematological"],
    },
}


def generate_symptom_text(disease_name: str, n_extra_symptoms: int = 1) -> str:
    """Generate a natural-language symptom description for a disease.

    Creates patient-like phrasing with core symptoms plus noise symptoms.
    """
    profile = DISEASE_PROFILES[disease_name]
    core = profile["core_symptoms"].copy()
    extras = [s for s in profile["symptoms"] if s not in core]

    # Always include core symptoms
    selected = core.copy()

    # Add some extra symptoms
    n_to_add = min(n_extra_symptoms, len(extras))
    if n_to_add > 0:
        selected.extend(random.sample(extras, n_to_add))

    # Add 0-2 noise symptoms from other diseases
    all_symptoms = []
    for p in DISEASE_PROFILES.values():
        all_symptoms.extend(p["symptoms"])
    noise = random.sample(set(all_symptoms) - set(selected), min(2, len(set(all_symptoms) - set(selected))))
    selected.extend(noise)
    random.shuffle(selected)

    # Build natural phrasing
    templates = [
        f"I've been experiencing {', '.join(selected)}.",
        f"I have {', '.join(selected[:-1])} and {selected[-1]}.",
        f"My main symptoms are {', '.join(selected[:3])}. Also {', '.join(selected[3:])}.",
        f"For a while now I've had {', '.join(selected)}.",
    ]

    duration = random.randint(*profile["duration_range"])
    if duration < 7:
        dur_text = f"{duration} days"
    elif duration < 30:
        dur_text = f"{duration // 7} weeks"
    else:
        dur_text = f"{duration // 30} months"

    text = random.choice(templates) + f" It's been going on for about {dur_text}."

    # Occasionally add severity modifier
    severity = random.choice(profile["severity_range"])
    severity_modifiers = {
        "mild": ["slightly", "a little", "not too bad"],
        "moderate": ["quite", "noticeably", "moderately"],
        "severe": ["really badly", "severely", "intensely"],
        "critical": ["extremely", "unbearably", "critically"],
    }
    if random.random() < 0.4:
        mod = random.choice(severity_modifiers.get(severity, [""]))
        text = text.replace("I have", f"I {mod} have", 1) if mod else text

    return text, duration, severity


def generate_symptom_dataset(n_samples: int = 1000, output_path: Optional[str] = None) -> str:
    """Generate a synthetic symptom-disease dataset.

    Args:
        n_samples: Number of symptom descriptions to generate.
        output_path: Where to save the JSON dataset.

    Returns:
        Path to the generated dataset file.
    """
    if output_path is None:
        output_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
            "data", "datasets", "synthetic", "symptom_disease_pairs.json",
        )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Weighted disease selection
    diseases = list(DISEASE_PROFILES.keys())
    weights = [DISEASE_PROFILES[d]["frequency"] for d in diseases]
    total = sum(weights)
    weights = [w / total for w in weights]

    dataset = []
    for i in range(n_samples):
        disease = random.choices(diseases, weights=weights, k=1)[0]
        profile = DISEASE_PROFILES[disease]

        n_extra = random.randint(0, 2)
        text, duration, severity = generate_symptom_text(disease, n_extra)

        # Random demographics
        age = random.randint(18, 85)
        gender = random.choice(["male", "female", "other"])

        dataset.append({
            "id": f"syn-{i+1:05d}",
            "disease": disease,
            "symptom_text": text,
            "symptoms_present": profile["core_symptoms"],
            "duration_days": duration,
            "severity": severity,
            "body_systems": profile["body_systems"],
            "age": age,
            "gender": gender,
        })

        if (i + 1) % 200 == 0:
            logger.info(f"Generated {i+1}/{n_samples} symptom descriptions")

    with open(output_path, "w") as f:
        json.dump(dataset, f, indent=2)

    logger.info(f"Saved {len(dataset)} symptom-disease pairs to {output_path}")

    # Print class distribution
    from collections import Counter
    dist = Counter(d["disease"] for d in dataset)
    logger.info("Class distribution:")
    for disease, count in sorted(dist.items(), key=lambda x: -x[1]):
        logger.info(f"  {disease}: {count} ({count/len(dataset)*100:.1f}%)")

    return output_path


if __name__ == "__main__":
    random.seed(42)
    generate_symptom_dataset(n_samples=1000)
