"""Phase 3: Generate 200 synthetic benchmark cases with ground truth labels.

This script creates a comprehensive test dataset covering multiple disease
categories, each with symptom text, patient demographics, and ground truth
diagnoses for accuracy evaluation.
"""

import json
import random
from datetime import datetime

random.seed(42)

# Disease templates: category → [(condition_name, [symptom_templates], [optional_symptoms], risk_factors)]
DISEASE_TEMPLATES = {
    "Cardiovascular": [
        {
            "condition": "Cardiovascular Disease",
            "alternatives": ["Angina Pectoris", "Coronary Artery Disease", "Myocardial Infarction"],
            "symptoms": [
                "chest pain", "chest pressure", "shortness of breath", "pain radiating to left arm",
                "fatigue on exertion", "palpitations", "dizziness",
            ],
            "required": ["chest pain", "shortness of breath"],
            "optional": ["sweating", "nausea", "jaw pain", "back pain", "irregular heartbeat"],
            "age_range": (45, 75),
            "bmi_range": (25, 35),
            "risk_factors": ["Heart disease", "Diabetes", "Hypertension"],
            "severity": "high",
        },
        {
            "condition": "Hypertension",
            "alternatives": ["High Blood Pressure", "Essential Hypertension"],
            "symptoms": [
                "headache", "dizziness", "blurred vision", "nosebleeds",
                "shortness of breath", "chest pain", "fatigue",
            ],
            "required": ["headache", "dizziness"],
            "optional": ["nosebleeds", "blurred vision", "flushing", "anxiety"],
            "age_range": (40, 70),
            "bmi_range": (24, 34),
            "risk_factors": ["Heart disease", "Diabetes"],
            "severity": "moderate",
        },
    ],
    "Respiratory": [
        {
            "condition": "Respiratory Infection",
            "alternatives": ["Upper Respiratory Infection", "Bronchitis", "URI"],
            "symptoms": [
                "cough", "fever", "sore throat", "runny nose",
                "nasal congestion", "fatigue", "body aches",
            ],
            "required": ["cough", "fever"],
            "optional": ["sore throat", "runny nose", "sneezing", "headache", "chills"],
            "age_range": (18, 65),
            "bmi_range": (18, 30),
            "risk_factors": ["Asthma"],
            "severity": "moderate",
        },
        {
            "condition": "Pneumonia",
            "alternatives": ["Community-Acquired Pneumonia", "Bacterial Pneumonia"],
            "symptoms": [
                "cough with phlegm", "fever", "chills", "difficulty breathing",
                "chest pain when breathing", "fatigue", "confusion",
            ],
            "required": ["cough", "fever", "difficulty breathing"],
            "optional": ["chills", "chest pain", "confusion", "sweating", "nausea"],
            "age_range": (50, 80),
            "bmi_range": (20, 32),
            "risk_factors": ["Asthma", "Heart disease"],
            "severity": "high",
        },
        {
            "condition": "Asthma",
            "alternatives": ["Asthma Exacerbation", "Bronchial Asthma"],
            "symptoms": [
                "wheezing", "shortness of breath", "chest tightness", "coughing",
                "difficulty breathing at night", "fatigue",
            ],
            "required": ["wheezing", "shortness of breath"],
            "optional": ["chest tightness", "coughing", "anxiety", "rapid breathing"],
            "age_range": (10, 50),
            "bmi_range": (18, 28),
            "risk_factors": ["Asthma"],
            "severity": "moderate",
        },
    ],
    "Endocrine": [
        {
            "condition": "Type 2 Diabetes",
            "alternatives": ["Diabetes Mellitus", "Diabetes", "T2DM"],
            "symptoms": [
                "excessive thirst", "frequent urination", "fatigue", "blurred vision",
                "slow wound healing", "tingling in hands", "unexplained weight loss",
            ],
            "required": ["excessive thirst", "frequent urination", "fatigue"],
            "optional": ["blurred vision", "slow wound healing", "tingling", "weight loss", "hunger"],
            "age_range": (35, 65),
            "bmi_range": (28, 40),
            "risk_factors": ["Diabetes"],
            "severity": "moderate",
        },
    ],
    "Neurological": [
        {
            "condition": "Migraine",
            "alternatives": ["Migraine Headache", "Migraine with Aura"],
            "symptoms": [
                "severe headache", "nausea", "sensitivity to light", "sensitivity to sound",
                "throbbing pain", "visual disturbances", "dizziness",
            ],
            "required": ["severe headache", "nausea"],
            "optional": ["sensitivity to light", "sensitivity to sound", "dizziness", "vomiting", "visual aura"],
            "age_range": (20, 55),
            "bmi_range": (18, 30),
            "risk_factors": [],
            "severity": "moderate",
        },
        {
            "condition": "Neurological Disorder",
            "alternatives": ["TIA", "Transient Ischemic Attack", "Stroke"],
            "symptoms": [
                "severe headache", "dizziness", "confusion", "numbness",
                "weakness on one side", "difficulty speaking", "vision changes",
            ],
            "required": ["severe headache", "dizziness", "numbness"],
            "optional": ["confusion", "weakness", "difficulty speaking", "vision changes", "loss of balance"],
            "age_range": (55, 80),
            "bmi_range": (22, 35),
            "risk_factors": ["Heart disease", "Diabetes", "Hypertension"],
            "severity": "critical",
        },
    ],
    "Gastrointestinal": [
        {
            "condition": "Gastroenteritis",
            "alternatives": ["Acute Gastroenteritis", "Stomach Flu", "Food Poisoning"],
            "symptoms": [
                "diarrhea", "nausea", "vomiting", "abdominal pain",
                "cramping", "low-grade fever", "loss of appetite",
            ],
            "required": ["diarrhea", "nausea", "abdominal pain"],
            "optional": ["vomiting", "cramping", "fever", "loss of appetite", "dehydration"],
            "age_range": (15, 60),
            "bmi_range": (18, 30),
            "risk_factors": [],
            "severity": "moderate",
        },
        {
            "condition": "GERD",
            "alternatives": ["Gastroesophageal Reflux Disease", "Acid Reflux", "Heartburn"],
            "symptoms": [
                "heartburn", "chest pain", "sour taste", "difficulty swallowing",
                "regurgitation", "chronic cough", "hoarseness",
            ],
            "required": ["heartburn", "chest pain"],
            "optional": ["sour taste", "difficulty swallowing", "regurgitation", "cough", "hoarseness"],
            "age_range": (30, 65),
            "bmi_range": (25, 38),
            "risk_factors": [],
            "severity": "low",
        },
    ],
    "Musculoskeletal": [
        {
            "condition": "Osteoarthritis",
            "alternatives": ["Joint Degeneration", "Degenerative Joint Disease"],
            "symptoms": [
                "joint pain", "stiffness", "swelling", "reduced range of motion",
                "grating sensation", "bone spurs", "pain with movement",
            ],
            "required": ["joint pain", "stiffness"],
            "optional": ["swelling", "reduced range of motion", "grating", "pain with movement"],
            "age_range": (50, 80),
            "bmi_range": (26, 40),
            "risk_factors": [],
            "severity": "moderate",
        },
        {
            "condition": "Back Pain",
            "alternatives": ["Lumbar Strain", "Lower Back Pain", "Muscle Strain"],
            "symptoms": [
                "back pain", "muscle stiffness", "limited mobility", "muscle spasm",
                "pain radiating to leg", "numbness in legs",
            ],
            "required": ["back pain", "muscle stiffness"],
            "optional": ["limited mobility", "muscle spasm", "pain radiating to leg", "numbness"],
            "age_range": (25, 65),
            "bmi_range": (20, 35),
            "risk_factors": [],
            "severity": "moderate",
        },
    ],
    "Dermatological": [
        {
            "condition": "Eczema",
            "alternatives": ["Atopic Dermatitis", "Contact Dermatitis"],
            "symptoms": [
                "itchy skin", "red rash", "dry skin", "skin cracking",
                "swelling", "darkened skin patches", "oozing",
            ],
            "required": ["itchy skin", "red rash"],
            "optional": ["dry skin", "skin cracking", "swelling", "darkened patches", "oozing"],
            "age_range": (1, 40),
            "bmi_range": (18, 30),
            "risk_factors": ["Asthma"],
            "severity": "low",
        },
    ],
    "Urinary": [
        {
            "condition": "Urinary Tract Infection",
            "alternatives": ["UTI", "Bladder Infection", "Cystitis"],
            "symptoms": [
                "burning during urination", "frequent urination", "cloudy urine",
                "pelvic pain", "blood in urine", "strong-smelling urine",
            ],
            "required": ["burning during urination", "frequent urination"],
            "optional": ["cloudy urine", "pelvic pain", "blood in urine", "strong-smelling urine", "fever"],
            "age_range": (20, 60),
            "bmi_range": (18, 30),
            "risk_factors": [],
            "severity": "moderate",
        },
    ],
    "Psychiatric": [
        {
            "condition": "Anxiety Disorder",
            "alternatives": ["Generalized Anxiety", "Anxiety", "GAD"],
            "symptoms": [
                "excessive worry", "restlessness", "fatigue", "difficulty concentrating",
                "sleep disturbances", "rapid heartbeat", "muscle tension",
            ],
            "required": ["excessive worry", "restlessness", "fatigue"],
            "optional": ["difficulty concentrating", "sleep disturbances", "rapid heartbeat", "muscle tension", "irritability"],
            "age_range": (18, 50),
            "bmi_range": (18, 30),
            "risk_factors": [],
            "severity": "moderate",
        },
    ],
}


def generate_case(template: dict, case_id: int) -> dict:
    """Generate a single synthetic benchmark case from a template."""
    condition = template["condition"]
    required = template["required"]
    optional = template.get("optional", [])
    
    # Select 2-4 optional symptoms
    n_optional = random.randint(2, min(4, len(optional)))
    selected_optional = random.sample(optional, n_optional)
    
    # All symptoms = required + selected optional
    all_symptoms = required + selected_optional
    random.shuffle(all_symptoms)
    
    # Build natural language symptom description
    templates_nl = [
        f"I've been having {', '.join(all_symptoms[:-1])} and {all_symptoms[-1]}.",
        f"I have {', '.join(all_symptoms)}. It's been bothering me for a while.",
        f"For the past few days I've experienced {', '.join(all_symptoms)}.",
        f"My main symptoms are {', '.join(all_symptoms)}. Should I be concerned?",
        f"I'm experiencing {', '.join(all_symptoms[:3])} and also {', '.join(all_symptoms[3:])} if any.",
    ]
    symptom_text = random.choice(templates_nl).rstrip(".") + "."
    
    # Patient demographics
    age = random.randint(*template["age_range"])
    bmi = round(random.uniform(*template["bmi_range"]), 1)
    gender = random.choice(["Male", "Female"])
    
    # Risk factors
    risk_factors = template.get("risk_factors", [])
    n_risk = random.randint(0, min(2, len(risk_factors)))
    selected_risks = random.sample(risk_factors, n_risk) if risk_factors else []
    
    return {
        "case_id": case_id,
        "category": list(DISEASE_TEMPLATES.keys())[
            list(DISEASE_TEMPLATES.values()).index(
                next(
                    lst for lst in DISEASE_TEMPLATES.values()
                    if template in lst
                )
            )
        ],
        "symptom_text": symptom_text,
        "symptoms_list": all_symptoms,
        "patient_history": {
            "age": age,
            "gender": gender,
            "bmi": bmi,
            "family_history": selected_risks,
        },
        "ground_truth": {
            "primary_condition": condition,
            "acceptable_conditions": [condition] + template.get("alternatives", []),
            "severity": template["severity"],
        },
        "metadata": {
            "required_symptoms": required,
            "optional_symptoms_present": selected_optional,
            "template_index": DISEASE_TEMPLATES[list(DISEASE_TEMPLATES.keys())[
                list(DISEASE_TEMPLATES.values()).index(
                    next(
                        lst for lst in DISEASE_TEMPLATES.values()
                        if template in lst
                    )
                )
            ]].index(template),
        },
    }


def generate_benchmark_cases(n_cases: int = 200) -> list[dict]:
    """Generate a balanced benchmark dataset."""
    all_templates = []
    for category, templates in DISEASE_TEMPLATES.items():
        for t in templates:
            all_templates.append((category, t))
    
    # Calculate cases per template for balanced distribution
    n_templates = len(all_templates)
    base_per_template = n_cases // n_templates
    remainder = n_cases % n_templates
    
    cases = []
    case_id = 1
    
    for i, (category, template) in enumerate(all_templates):
        n = base_per_template + (1 if i < remainder else 0)
        for _ in range(n):
            case = generate_case(template, case_id)
            case["category"] = category
            cases.append(case)
            case_id += 1
    
    # Shuffle to avoid ordering bias
    random.shuffle(cases)
    
    # Re-number case IDs after shuffle
    for i, case in enumerate(cases):
        case["case_id"] = i + 1
    
    return cases


if __name__ == "__main__":
    print("Generating 200 synthetic benchmark cases...")
    cases = generate_benchmark_cases(200)
    
    # Save to file
    output_path = "data/benchmark_cases.json"
    with open(output_path, "w") as f:
        json.dump(cases, f, indent=2)
    
    # Print statistics
    categories = {}
    severities = {}
    for case in cases:
        cat = case["category"]
        sev = case["ground_truth"]["severity"]
        categories[cat] = categories.get(cat, 0) + 1
        severities[sev] = severities.get(sev, 0) + 1
    
    print(f"\nTotal cases: {len(cases)}")
    print(f"\nCases by category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    print(f"\nCases by severity:")
    for sev, count in sorted(severities.items()):
        print(f"  {sev}: {count}")
    print(f"\nSaved to: {output_path}")
