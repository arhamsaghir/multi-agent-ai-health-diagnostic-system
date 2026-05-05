"""Diagnosis page — redesigned with agent status, charts, demo mode, and report export."""

import streamlit as st
import requests
import json
import time
from datetime import datetime
from pathlib import Path

import sys
from pathlib import Path as StdPath
sys.path.insert(0, str(StdPath(__file__).resolve().parents[1]))

from src.utils.report_exporter import generate_csv_report, generate_pdf_report

API_BASE = "http://localhost:8000"

# Pre-computed demo scenarios
DEMO_SCENARIOS = {
    "Chest Pain": {
        "text": "I've been having chest pain for the past 2 days. It feels like pressure in the center of my chest and radiates to my left arm. I also feel short of breath when I walk upstairs. I'm a 55-year-old male with a history of high blood pressure.",
        "age": 55,
        "bmi": 28.5,
        "family_history": ["Heart disease"],
        "expected_severity": "high",
        "expected_conditions": ["Cardiovascular Disease", "Angina"],
    },
    "Respiratory Infection": {
        "text": "I have a persistent cough for the past week with yellow-green phlegm. I also have a fever of 101°F, chills, and difficulty breathing. My chest feels tight when I cough. I'm a 35-year-old female.",
        "age": 35,
        "bmi": 24.0,
        "family_history": ["Asthma"],
        "expected_severity": "moderate",
        "expected_conditions": ["Respiratory Infection", "Pneumonia"],
    },
    "Diabetes Screening": {
        "text": "I've been feeling extremely thirsty lately and urinating frequently, even at night. I'm also experiencing fatigue and blurred vision. I'm 45 years old and overweight. My father has type 2 diabetes.",
        "age": 45,
        "bmi": 32.0,
        "family_history": ["Diabetes"],
        "expected_severity": "moderate",
        "expected_conditions": ["Diabetes", "Type 2 Diabetes"],
    },
    "Neurological Symptoms": {
        "text": "I've been having severe headaches for the past 3 days, along with dizziness and confusion. Sometimes I feel numbness on the right side of my body. I'm 60 years old with a history of hypertension.",
        "age": 60,
        "bmi": 26.5,
        "family_history": ["Heart disease"],
        "expected_severity": "high",
        "expected_conditions": ["Neurological Disorder", "Stroke Risk"],
    },
    "Common Cold": {
        "text": "I have a runny nose, mild sore throat, and occasional sneezing for the past 2 days. No fever, just feeling a bit tired. I'm 25 years old and generally healthy.",
        "age": 25,
        "bmi": 22.0,
        "family_history": [],
        "expected_severity": "low",
        "expected_conditions": ["Upper Respiratory Infection", "Common Cold"],
    },
}


def run_diagnosis(text: str, patient_history: dict) -> dict:
    """Call the diagnosis API or return mock/demo results if unavailable."""
    try:
        response = requests.post(
            f"{API_BASE}/api/diagnosis/analyze",
            json={
                "text": text,
                "patient_history": patient_history,
            },
            timeout=120,
        )
        if response.status_code == 200:
            data = response.json()
            return {
                "diagnosis": data.get("diagnosis", []),
                "explanation": data.get("explanation", ""),
                "patient_explanation": data.get("patient_explanation", ""),
                "recommendations": data.get("recommendations", []),
                "severity": data.get("severity", "unknown"),
                "doctor_alert": data.get("doctor_alert", False),
                "differential_diagnoses": data.get("differential_diagnoses", []),
                "red_flags": data.get("red_flags", []),
                "confidence": data.get("confidence", {}),
                "disclaimer": data.get("disclaimer", ""),
                "confidence_score": data.get("confidence", {}).get("overall_confidence", 0),
                "symptoms": _extract_symptoms_from_text(text),
                "timestamp": datetime.now().isoformat(),
                "api_response": True,
            }
    except requests.ConnectionError:
        st.warning("⚠️ API server not running — showing demo results.")
    except Exception as e:
        st.error(f"API error: {e}")

    # Fallback to scenario-based demo results
    return _get_demo_result(text, patient_history)


def _get_demo_result(text: str, patient_history: dict) -> dict:
    """Generate realistic demo results based on symptom text analysis."""
    text_lower = text.lower()
    symptoms = _extract_symptoms_from_text(text)

    # Determine scenario based on symptoms with disambiguation logic
    # ====== SPECIFIC CONDITION DETECTORS (highest priority) ======

    # Asthma — wheezing is the key differentiator
    is_asthma = any(s in text_lower for s in ["wheezing", "chest tightness"]) and any(s in text_lower for s in ["shortness of breath", "difficulty breathing", "coughing"])

    # Diabetes — classic triad
    has_thirst = any(s in text_lower for s in ["excessive thirst", "thirsty", "very thirsty"])
    has_urination = any(s in text_lower for s in ["frequent urination", "urinating frequently", "urinating", "urination"])
    has_fatigue_or_vision = any(s in text_lower for s in ["fatigue", "blurred vision", "tiredness", "weight loss"])
    is_diabetes = has_thirst and has_urination and has_fatigue_or_vision

    # UTI — burning/painful urination + frequency (check before respiratory due to fever overlap)
    has_urinary_burning = any(s in text_lower for s in ["burning", "painful urination", "burning sensation"])
    has_urinary_freq = any(s in text_lower for s in ["frequent urination", "urinating frequently", "urination"])
    has_urinary_signs = any(s in text_lower for s in ["blood in urine", "bladder pain", "cloudy urine", "pelvic pain", "strong-smelling urine"])
    is_urinary = (has_urinary_burning or has_urinary_signs) or (has_urinary_freq and has_urinary_burning)

    # Migraine — severe headache + nausea/vomiting + sensitivity (check before generic neuro)
    has_severe_headache = any(s in text_lower for s in ["severe headache", "migraine", "throbbing headache"])
    has_migraine_associated = any(s in text_lower for s in ["nausea", "vomiting", "sensitivity to light", "sensitivity to sound", "visual aura", "aura"])
    is_migraine = has_severe_headache and has_migraine_associated

    # GERD — heartburn/regurgitation (GERD-specific, not shared with cardiac)
    has_gerd = any(s in text_lower for s in ["heartburn", "regurgitation", "sour taste", "acid reflux", "hoarseness"])

    # Gastroenteritis — diarrhea + GI upset
    has_diarrhea = any(s in text_lower for s in ["diarrhea", "loose stools"])
    has_gi_upset = any(s in text_lower for s in ["nausea", "vomiting", "cramping", "abdominal pain", "stomach pain", "dehydration", "loss of appetite"])
    is_gastroenteritis = has_diarrhea and has_gi_upset

    # IBS — chronic abdominal pain + bowel changes
    has_ibs = any(s in text_lower for s in ["abdominal pain", "bloating"]) and any(s in text_lower for s in ["diarrhea", "constipation", "alternating"])

    # Hypertension — headache + cardiovascular risk signs (no chest pain)
    has_hypertension_signs = any(s in text_lower for s in ["nosebleeds", "flushing", "blood pressure", "high blood pressure", "hypertension"])
    has_headache_dizzy = any(s in text_lower for s in ["headache", "dizziness", "blurred vision"])
    is_hypertension = has_hypertension_signs and has_headache_dizzy

    # Back Pain — back pain + musculoskeletal signs (check before neuro because numbness overlap)
    has_back_pain = any(s in text_lower for s in ["back pain", "lower back pain", "upper back pain"])
    has_muscle_signs = any(s in text_lower for s in ["muscle spasm", "muscle stiffness", "muscle pain", "limited mobility", "stiffness", "pain radiating to leg"])
    is_back_pain = has_back_pain and has_muscle_signs

    # ====== CATEGORY DETECTORS (after specific conditions) ======

    # Cardiovascular — chest pain/cardiac signs (but not if GERD-specific)
    is_cardiovascular = any(s in text_lower for s in ["chest pain", "chest pressure", "radiates to", "left arm", "palpitations", "irregular heartbeat", "shortness of breath"]) and not has_gerd

    # Pneumonia — cough + fever + breathing difficulty (even with chest pain)
    has_pneumonia_signs = any(s in text_lower for s in ["cough", "phlegm", "fever", "chills"]) and any(s in text_lower for s in ["difficulty breathing", "chest pain when breathing", "chest tightness"])
    is_pneumonia = has_pneumonia_signs and not is_asthma

    # Respiratory — cough/fever (after pneumonia, asthma, gastroenteritis)
    is_respiratory = any(s in text_lower for s in ["cough", "phlegm", "fever", "chills", "runny nose", "sore throat"]) and not is_asthma and not is_pneumonia and not is_gastroenteritis

    # Gastrointestinal — GI symptoms without being gastroenteritis or GERD already
    is_gastrointestinal = (has_gerd or is_gastroenteritis or has_ibs)

    # Neurological — headache/dizziness (after migraine, hypertension, back pain, respiratory)
    is_neurological = any(s in text_lower for s in ["headache", "dizziness", "confusion", "numbness", "weakness", "loss of balance", "seizure"]) and not is_migraine and not is_hypertension and not is_back_pain and not is_respiratory

    # Dermatological
    is_dermatological = any(s in text_lower for s in ["rash", "itching", "red patches", "scaling", "blisters", "dry skin", "hives", "oozing"])

    # Musculoskeletal — joint/bone/muscle (after back pain)
    is_musculoskeletal = any(s in text_lower for s in ["joint pain", "joint swelling", "stiffness", "muscle pain", "bone pain", "limited mobility"]) and not is_back_pain

    # Psychiatric
    is_psychiatric = any(s in text_lower for s in ["anxiety", "excessive worry", "irritability", "restlessness", "panic", "sadness", "hopelessness", "difficulty concentrating", "sleep disturbances", "mood swings", "loss of interest"])

    is_mild = any(s in text_lower for s in ["mild", "minor"])

    age = patient_history.get("age", 30)
    bmi = patient_history.get("bmi", 25)
    family_history = patient_history.get("family_history", [])

    # ====== IF/ELIF CHAIN — specific conditions before general categories ======

    if is_asthma:
        return {
            "diagnosis": [
                {"condition": "Asthma", "confidence": 0.80, "rationale": "Wheezing with chest tightness and shortness of breath is characteristic of bronchial asthma. Symptoms worsen at night or with triggers.", "icd10_code": "J45.9"},
                {"condition": "Reactive Airway Disease", "confidence": 0.45, "rationale": "Similar presentation to asthma, may require spirometry for differentiation.", "icd10_code": "J44.9"},
            ],
            "explanation": "Your symptoms suggest asthma. Wheezing, chest tightness, and difficulty breathing are classic signs of airway inflammation and bronchoconstriction. A pulmonary function test can help confirm the diagnosis.",
            "patient_explanation": "You may have asthma. The wheezing and chest tightness mean your airways are narrowed. This is treatable with inhalers, but you need to see a doctor for proper diagnosis and medication.",
            "recommendations": [
                "See a healthcare provider for pulmonary function testing",
                "Avoid known triggers (dust, smoke, cold air, exercise)",
                "Use a rescue inhaler if prescribed",
                "Monitor peak flow if you have a peak flow meter",
                "Seek emergency care if breathing becomes severely difficult",
            ],
            "severity": "moderate",
            "doctor_alert": True,
            "differential_diagnoses": ["Respiratory infection", "Allergic reaction", "Vocal cord dysfunction"],
            "red_flags": [
                "Severe difficulty breathing at rest",
                "Inability to speak in full sentences",
                "Blue lips or fingernails",
                "No improvement after rescue inhaler",
            ],
            "confidence": {
                "overall_confidence": 0.68,
                "breakdown": {"nlp": 0.78, "vision": 0.0, "rag": 0.65, "prediction": 0.72},
            },
            "confidence_score": 0.68,
            "symptoms": symptoms,
            "timestamp": datetime.now().isoformat(),
            "disclaimer": "This is an AI-generated assessment and not a substitute for professional medical advice. Always consult a qualified healthcare provider for diagnosis and treatment.",
            "api_response": False,
        }

    elif is_pneumonia:
        return {
            "diagnosis": [
                {"condition": "Pneumonia", "confidence": 0.80, "rationale": "Fever with productive cough, difficulty breathing, and chest pain when breathing strongly suggest pneumonia. Chest X-ray is recommended to confirm.", "icd10_code": "J18.9"},
                {"condition": "Respiratory Infection", "confidence": 0.55, "rationale": "Lower respiratory tract infection may present similarly but typically has less severe breathing difficulty.", "icd10_code": "J22"},
            ],
            "explanation": "Your symptoms are concerning for pneumonia. The combination of fever, cough with difficulty breathing, and chest discomfort suggests a lung infection that may require antibiotics and a chest X-ray for confirmation.",
            "patient_explanation": "You may have pneumonia, which is a lung infection. Your fever and breathing difficulty need medical attention. You'll likely need a chest X-ray and possibly antibiotics. Please see a doctor promptly.",
            "recommendations": [
                "See a healthcare provider urgently for evaluation and chest X-ray",
                "Antibiotics may be needed if bacterial pneumonia is confirmed",
                "Rest and stay well-hydrated",
                "Monitor temperature — seek urgent care if fever exceeds 103°F",
                "Use a humidifier to ease breathing discomfort",
            ],
            "severity": "high",
            "doctor_alert": True,
            "differential_diagnoses": ["Acute bronchitis", "Respiratory infection", "Pulmonary embolism"],
            "red_flags": [
                "Fever above 103°F",
                "Difficulty breathing at rest",
                "Coughing up blood",
                "Blue lips or face",
                "Confusion or altered mental state",
            ],
            "confidence": {
                "overall_confidence": 0.68,
                "breakdown": {"nlp": 0.80, "vision": 0.0, "rag": 0.65, "prediction": 0.60},
            },
            "confidence_score": 0.68,
            "symptoms": symptoms,
            "timestamp": datetime.now().isoformat(),
            "disclaimer": "This is an AI-generated assessment and not a substitute for professional medical advice. Always consult a qualified healthcare provider for diagnosis and treatment.",
            "api_response": False,
        }

    elif is_diabetes:
        return {
            "diagnosis": [
                {"condition": "Type 2 Diabetes", "confidence": 0.75, "rationale": "Classic symptoms of polydipsia (excessive thirst), polyuria (frequent urination), fatigue, and blurred vision. Age 45, elevated BMI, and family history are significant risk factors.", "icd10_code": "E11.9"},
                {"condition": "Prediabetes", "confidence": 0.45, "rationale": "Early stage glucose dysregulation may present with milder versions of these symptoms.", "icd10_code": "R73.03"},
            ],
            "explanation": "Your symptoms strongly suggest type 2 diabetes. The combination of excessive thirst, frequent urination, fatigue, and blurred vision are classic signs of elevated blood sugar. Your age, weight, and family history put you at higher risk. A fasting blood glucose test and HbA1c test are recommended.",
            "patient_explanation": "Your symptoms suggest you may have high blood sugar (diabetes). The excessive thirst, frequent urination, and tiredness are common signs. This is manageable with treatment, but you need to see a doctor for blood tests to confirm. Early treatment makes a big difference.",
            "recommendations": [
                "Get a fasting blood glucose test and HbA1c test",
                "Consult an endocrinologist or primary care physician",
                "Reduce sugar and refined carbohydrate intake",
                "Start regular physical activity (30 min walking daily)",
                "Monitor for signs of extremely high blood sugar: confusion, fruity breath, vomiting",
            ],
            "severity": "moderate",
            "doctor_alert": True,
            "differential_diagnoses": ["Thyroid dysfunction", "Urinary tract infection", "Medication side effects"],
            "red_flags": [
                "Confusion or drowsiness",
                "Fruity-smelling breath",
                "Nausea and vomiting",
                "Rapid breathing",
            ],
            "confidence": {
                "overall_confidence": 0.70,
                "breakdown": {"nlp": 0.82, "vision": 0.0, "rag": 0.72, "prediction": 0.78},
            },
            "confidence_score": 0.70,
            "symptoms": symptoms,
            "timestamp": datetime.now().isoformat(),
            "disclaimer": "This is an AI-generated assessment and not a substitute for professional medical advice. Always consult a qualified healthcare provider for diagnosis and treatment.",
            "api_response": False,
        }

    elif is_migraine:
        return {
            "diagnosis": [
                {"condition": "Migraine", "confidence": 0.80, "rationale": "Severe headache with associated symptoms including nausea, vomiting, and sensitivity to light/sound are classic migraine features. Visual aura further supports this diagnosis.", "icd10_code": "G43.9"},
                {"condition": "Tension Headache", "confidence": 0.35, "rationale": "Less severe headaches without associated symptoms may suggest tension-type headache.", "icd10_code": "G44.1"},
            ],
            "explanation": "Your symptoms are consistent with a migraine. Severe headache accompanied by nausea, sensitivity to light or sound, and visual changes are hallmark features. Migraines are neurological events that can be managed with preventive and acute treatments.",
            "patient_explanation": "You're likely experiencing a migraine. These are more than regular headaches — they involve nausea, sensitivity to light and sound, and can be very debilitating. There are good treatments available. See a doctor for medication that can help both stop attacks and prevent them.",
            "recommendations": [
                "Rest in a dark, quiet room",
                "Apply a cold compress to your forehead",
                "Stay hydrated — drink water",
                "Consider over-the-counter pain relief (ibuprofen, acetaminophen)",
                "See a neurologist for preventive treatment if migraines are frequent",
            ],
            "severity": "moderate",
            "doctor_alert": False,
            "differential_diagnoses": ["Tension headache", "Cluster headache", "Sinus headache"],
            "red_flags": [
                "Sudden worst headache of your life (thunderclap)",
                "Headache with fever and stiff neck",
                "New neurological symptoms: weakness, confusion",
                "Headache after head injury",
            ],
            "confidence": {
                "overall_confidence": 0.68,
                "breakdown": {"nlp": 0.80, "vision": 0.0, "rag": 0.62, "prediction": 0.70},
            },
            "confidence_score": 0.68,
            "symptoms": symptoms,
            "timestamp": datetime.now().isoformat(),
            "disclaimer": "This is an AI-generated assessment and not a substitute for professional medical advice. Always consult a qualified healthcare provider for diagnosis and treatment.",
            "api_response": False,
        }

    elif is_hypertension:
        return {
            "diagnosis": [
                {"condition": "Hypertension", "confidence": 0.78, "rationale": "Headache with nosebleeds, flushing, and visual changes are signs of elevated blood pressure. Blood pressure measurement is needed to confirm.", "icd10_code": "I10"},
                {"condition": "Essential Hypertension", "confidence": 0.55, "rationale": "Chronic high blood pressure without an identifiable cause may present with these symptoms.", "icd10_code": "I10"},
            ],
            "explanation": "Your symptoms suggest elevated blood pressure (hypertension). Headache, nosebleeds, flushing, and visual changes can all be signs of high blood pressure. A blood pressure reading is needed to confirm the diagnosis. Untreated hypertension increases risk of heart disease, stroke, and kidney problems.",
            "patient_explanation": "Your symptoms suggest you may have high blood pressure. This is very common but important to manage. You need to have your blood pressure checked by a doctor or at a pharmacy. If it's high, medication and lifestyle changes can help protect your heart and kidneys.",
            "recommendations": [
                "Get your blood pressure checked immediately",
                "Reduce salt intake in your diet",
                "Limit alcohol and caffeine",
                "Exercise regularly (30 min walking daily)",
                "See a doctor for ongoing blood pressure management",
            ],
            "severity": "high",
            "doctor_alert": True,
            "differential_diagnoses": ["Migraine", "Anxiety disorder", "Medication side effects"],
            "red_flags": [
                "Severe headache with confusion",
                "Chest pain with high blood pressure",
                "Difficulty breathing",
                "Vision loss or blurring",
            ],
            "confidence": {
                "overall_confidence": 0.65,
                "breakdown": {"nlp": 0.75, "vision": 0.0, "rag": 0.60, "prediction": 0.70},
            },
            "confidence_score": 0.65,
            "symptoms": symptoms,
            "timestamp": datetime.now().isoformat(),
            "disclaimer": "This is an AI-generated assessment and not a substitute for professional medical advice. Always consult a qualified healthcare provider for diagnosis and treatment.",
            "api_response": False,
        }

    elif is_back_pain:
        return {
            "diagnosis": [
                {"condition": "Back Pain", "confidence": 0.78, "rationale": "Back pain with muscle spasm, stiffness, and limited mobility is consistent with musculoskeletal back pain, possibly from strain or disc issues.", "icd10_code": "M54.9"},
                {"condition": "Lumbar Strain", "confidence": 0.50, "rationale": "Acute onset of back pain with muscle spasm may indicate a lumbar muscle strain.", "icd10_code": "S39.012"},
            ],
            "explanation": "Your symptoms suggest musculoskeletal back pain. The combination of back pain, muscle spasm, stiffness, and limited mobility is consistent with a strain or mechanical back issue. Most cases improve with conservative treatment, but imaging may be needed if symptoms persist.",
            "patient_explanation": "You have back pain with muscle tightness. This is very common and usually improves within a few weeks. Gentle stretching, heat, and over-the-counter pain relievers can help. If the pain spreads down your leg or you have numbness, see a doctor promptly.",
            "recommendations": [
                "Apply heat or ice packs for 15-20 minutes at a time",
                "Avoid heavy lifting and twisting motions",
                "Gentle stretching and walking can help",
                "Consider over-the-counter pain relievers (ibuprofen, acetaminophen)",
                "See a doctor if pain persists beyond 2 weeks or worsens",
            ],
            "severity": "moderate",
            "doctor_alert": False,
            "differential_diagnoses": ["Herniated disc", "Sciatica", "Kidney stones"],
            "red_flags": [
                "Pain radiating down leg past the knee",
                "Loss of bowel or bladder control",
                "Numbness in groin area",
                "Fever with back pain",
            ],
            "confidence": {
                "overall_confidence": 0.62,
                "breakdown": {"nlp": 0.72, "vision": 0.0, "rag": 0.58, "prediction": 0.65},
            },
            "confidence_score": 0.62,
            "symptoms": symptoms,
            "timestamp": datetime.now().isoformat(),
            "disclaimer": "This is an AI-generated assessment and not a substitute for professional medical advice. Always consult a qualified healthcare provider for diagnosis and treatment.",
            "api_response": False,
        }

    elif is_cardiovascular:
        return {
            "diagnosis": [
                {"condition": "Cardiovascular Disease", "confidence": 0.78, "rationale": "Chest pain radiating to left arm with shortness of breath are classic signs of cardiac involvement. Patient age and risk factors increase concern.", "icd10_code": "I25.9"},
                {"condition": "Angina Pectoris", "confidence": 0.65, "rationale": "Pressure-like chest pain triggered by exertion is consistent with stable angina.", "icd10_code": "I20.9"},
                {"condition": "Hypertension", "confidence": 0.35, "rationale": "Elevated blood pressure can cause chest discomfort and palpitations.", "icd10_code": "I10"},
            ],
            "explanation": "Based on your symptoms, the AI system has identified cardiovascular disease as the most likely condition. The combination of chest pain, shortness of breath, and your risk factors warrant prompt medical evaluation.",
            "patient_explanation": "Your symptoms suggest a possible heart-related issue. Chest pain and shortness of breath are important warning signs. Please see a doctor as soon as possible for proper evaluation.",
            "recommendations": [
                "Seek immediate medical evaluation — chest pain requires urgent assessment",
                "Do not drive yourself to the hospital — call emergency services if pain worsens",
                "Rest and avoid physical exertion until evaluated",
                "Monitor for additional symptoms: sweating, nausea, jaw pain",
                "Follow up with a cardiologist for comprehensive cardiac workup",
            ],
            "severity": "high",
            "doctor_alert": True,
            "differential_diagnoses": ["Gastroesophageal reflux disease (GERD)", "Musculoskeletal chest pain", "Anxiety-related chest discomfort"],
            "red_flags": [
                "Chest pain radiating to arm, jaw, or back",
                "Profuse sweating or nausea/vomiting",
                "Sudden worsening of shortness of breath",
                "Dizziness or near-fainting",
            ],
            "confidence": {
                "overall_confidence": 0.72,
                "breakdown": {"nlp": 0.85, "vision": 0.0, "rag": 0.70, "prediction": 0.82},
            },
            "confidence_score": 0.72,
            "symptoms": symptoms,
            "timestamp": datetime.now().isoformat(),
            "disclaimer": "This is an AI-generated assessment and not a substitute for professional medical advice. Always consult a qualified healthcare provider for diagnosis and treatment.",
            "api_response": False,
        }

    elif is_urinary:
        return {
            "diagnosis": [
                {"condition": "Urinary Tract Infection (UTI)", "confidence": 0.82, "rationale": "Burning sensation during urination, frequent urination, and lower abdominal discomfort are classic signs of a urinary tract infection.", "icd10_code": "N39.0"},
                {"condition": "Cystitis", "confidence": 0.55, "rationale": "Bladder inflammation with urinary frequency and urgency may indicate bacterial cystitis.", "icd10_code": "N30.9"},
            ],
            "explanation": "Your symptoms strongly suggest a urinary tract infection. The burning sensation during urination, increased frequency, and pelvic discomfort are typical signs. A urine test can confirm the diagnosis and guide antibiotic selection.",
            "patient_explanation": "You likely have a urinary tract infection. The burning feeling when you urinate and needing to go frequently are common signs. This needs antibiotics from a doctor — don't wait, as it can spread to your kidneys if untreated.",
            "recommendations": [
                "See a healthcare provider for a urine test and antibiotics",
                "Drink plenty of water to help flush bacteria",
                "Avoid caffeine, alcohol, and spicy foods until symptoms resolve",
                "Urinate frequently — don't hold it in",
                "Seek urgent care if you develop fever, back pain, or nausea",
            ],
            "severity": "moderate",
            "doctor_alert": True,
            "differential_diagnoses": ["Kidney stones", "Sexually transmitted infection", "Interstitial cystitis"],
            "red_flags": [
                "Fever with chills",
                "Flank or back pain (possible kidney infection)",
                "Blood in urine",
                "Nausea and vomiting",
            ],
            "confidence": {
                "overall_confidence": 0.70,
                "breakdown": {"nlp": 0.80, "vision": 0.0, "rag": 0.68, "prediction": 0.72},
            },
            "confidence_score": 0.70,
            "symptoms": symptoms,
            "timestamp": datetime.now().isoformat(),
            "disclaimer": "This is an AI-generated assessment and not a substitute for professional medical advice. Always consult a qualified healthcare provider for diagnosis and treatment.",
            "api_response": False,
        }

    elif is_gastroenteritis:
        return {
            "diagnosis": [
                {"condition": "Gastroenteritis", "confidence": 0.82, "rationale": "Diarrhea with nausea, vomiting, abdominal cramping, and possible fever suggest acute gastroenteritis, often viral or bacterial in origin.", "icd10_code": "K52.9"},
                {"condition": "Food Poisoning", "confidence": 0.50, "rationale": "Acute onset of GI symptoms after suspected contaminated food intake may indicate foodborne illness.", "icd10_code": "T62.9"},
            ],
            "explanation": "Your symptoms suggest acute gastroenteritis. The combination of diarrhea, nausea, vomiting, and abdominal cramping is consistent with a gastrointestinal infection. Most cases resolve within a few days with supportive care and hydration.",
            "patient_explanation": "You likely have a stomach bug (gastroenteritis). The diarrhea and vomiting mean your body is trying to clear an infection. The most important thing is to stay hydrated. Drink small sips of water or oral rehydration solution frequently.",
            "recommendations": [
                "Stay hydrated — drink oral rehydration solution or clear fluids",
                "Avoid dairy, fatty foods, and caffeine until symptoms resolve",
                "Rest and let your digestive system recover",
                "Consider over-the-counter anti-diarrheal medication (loperamide) if needed",
                "See a doctor if symptoms persist beyond 3 days or you show signs of dehydration",
            ],
            "severity": "moderate",
            "doctor_alert": False,
            "differential_diagnoses": ["Irritable Bowel Syndrome (IBS)", "Inflammatory bowel disease", "Appendicitis"],
            "red_flags": [
                "Blood in stool",
                "Severe dehydration (dark urine, dizziness, dry mouth)",
                "Fever above 102°F",
                "Severe abdominal pain localized to one area",
            ],
            "confidence": {
                "overall_confidence": 0.66,
                "breakdown": {"nlp": 0.78, "vision": 0.0, "rag": 0.60, "prediction": 0.70},
            },
            "confidence_score": 0.66,
            "symptoms": symptoms,
            "timestamp": datetime.now().isoformat(),
            "disclaimer": "This is an AI-generated assessment and not a substitute for professional medical advice. Always consult a qualified healthcare provider for diagnosis and treatment.",
            "api_response": False,
        }

    elif is_gastrointestinal:
        return {
            "diagnosis": [
                {"condition": "GERD", "confidence": 0.74, "rationale": "Heartburn, regurgitation, and chest discomfort after meals are classic signs of gastroesophageal reflux disease.", "icd10_code": "K21.0"},
                {"condition": "Peptic Ulcer Disease", "confidence": 0.42, "rationale": "Epigastric pain that improves or worsens with food intake may indicate gastric or duodenal ulcer.", "icd10_code": "K27.9"},
            ],
            "explanation": "Your symptoms suggest gastroesophageal reflux disease (GERD). The burning sensation in your chest, regurgitation, and discomfort after eating are typical of stomach acid flowing back into the esophagus.",
            "patient_explanation": "You may have acid reflux (GERD). The burning feeling in your chest and sour taste are caused by stomach acid coming back up. This is common and treatable. Avoid large meals, don't lie down right after eating, and see a doctor if it doesn't improve.",
            "recommendations": [
                "Avoid trigger foods: spicy, fatty, acidic foods, caffeine, alcohol",
                "Eat smaller meals and don't lie down for 2-3 hours after eating",
                "Elevate the head of your bed if symptoms worsen at night",
                "Consider over-the-counter antacids for temporary relief",
                "See a gastroenterologist if symptoms persist or worsen",
            ],
            "severity": "moderate",
            "doctor_alert": False,
            "differential_diagnoses": ["Peptic ulcer", "Esophagitis", "Gallbladder disease"],
            "red_flags": [
                "Difficulty swallowing",
                "Unintentional weight loss",
                "Vomiting blood or coffee-ground material",
                "Black, tarry stools",
            ],
            "confidence": {
                "overall_confidence": 0.66,
                "breakdown": {"nlp": 0.75, "vision": 0.0, "rag": 0.62, "prediction": 0.68},
            },
            "confidence_score": 0.66,
            "symptoms": symptoms,
            "timestamp": datetime.now().isoformat(),
            "disclaimer": "This is an AI-generated assessment and not a substitute for professional medical advice. Always consult a qualified healthcare provider for diagnosis and treatment.",
            "api_response": False,
        }

    elif is_dermatological:
        return {
            "diagnosis": [
                {"condition": "Eczema", "confidence": 0.72, "rationale": "Red, itchy patches with dry, scaly skin are characteristic of atopic dermatitis. Often worsens with environmental triggers.", "icd10_code": "L20.9"},
                {"condition": "Contact Dermatitis", "confidence": 0.48, "rationale": "Localized rash after exposure to an irritant or allergen may indicate contact dermatitis.", "icd10_code": "L25.9"},
            ],
            "explanation": "Your symptoms suggest eczema or contact dermatitis. The red, itchy, and scaly skin patches are consistent with inflammatory skin conditions.",
            "patient_explanation": "You have a skin condition that's causing redness and itching. This could be eczema or a reaction to something your skin touched. Keep the area moisturized, avoid scratching, and see a dermatologist for proper treatment.",
            "recommendations": [
                "Apply fragrance-free moisturizer frequently",
                "Avoid known irritants: harsh soaps, hot water, wool clothing",
                "Use lukewarm water for bathing, pat dry gently",
                "Consider over-the-counter hydrocortisone cream for mild cases",
                "See a dermatologist if the rash spreads or doesn't improve",
            ],
            "severity": "low",
            "doctor_alert": False,
            "differential_diagnoses": ["Psoriasis", "Fungal infection", "Allergic reaction"],
            "red_flags": [
                "Rash spreading rapidly",
                "Signs of infection: pus, warmth, increasing pain",
                "Fever with rash",
                "Rash involving eyes or mouth",
            ],
            "confidence": {
                "overall_confidence": 0.62,
                "breakdown": {"nlp": 0.72, "vision": 0.0, "rag": 0.58, "prediction": 0.65},
            },
            "confidence_score": 0.62,
            "symptoms": symptoms,
            "timestamp": datetime.now().isoformat(),
            "disclaimer": "This is an AI-generated assessment and not a substitute for professional medical advice. Always consult a qualified healthcare provider for diagnosis and treatment.",
            "api_response": False,
        }

    elif is_musculoskeletal:
        return {
            "diagnosis": [
                {"condition": "Osteoarthritis", "confidence": 0.70, "rationale": "Joint pain, stiffness, and reduced mobility are hallmark signs of osteoarthritis, especially in weight-bearing joints.", "icd10_code": "M19.9"},
                {"condition": "Rheumatoid Arthritis", "confidence": 0.45, "rationale": "Symmetrical joint involvement with morning stiffness lasting more than 30 minutes may suggest inflammatory arthritis.", "icd10_code": "M06.9"},
            ],
            "explanation": "Your symptoms suggest osteoarthritis. Joint pain, stiffness, and limited mobility are common signs of cartilage wear in the joints.",
            "patient_explanation": "Your joint pain and stiffness may be arthritis. This is common and manageable. Gentle exercise, weight management, and pain relievers can help. See a doctor for an accurate diagnosis and treatment plan.",
            "recommendations": [
                "Maintain a healthy weight to reduce joint stress",
                "Engage in low-impact exercise: swimming, cycling, walking",
                "Apply heat or cold packs for pain relief",
                "Consider over-the-counter pain relievers (NSAIDs)",
                "See an orthopedist or rheumatologist for proper evaluation",
            ],
            "severity": "moderate",
            "doctor_alert": False,
            "differential_diagnoses": ["Gout", "Fibromyalgia", "Tendonitis"],
            "red_flags": [
                "Sudden severe joint swelling",
                "Joint deformity",
                "Inability to bear weight",
                "Fever with joint pain",
            ],
            "confidence": {
                "overall_confidence": 0.60,
                "breakdown": {"nlp": 0.70, "vision": 0.0, "rag": 0.55, "prediction": 0.62},
            },
            "confidence_score": 0.60,
            "symptoms": symptoms,
            "timestamp": datetime.now().isoformat(),
            "disclaimer": "This is an AI-generated assessment and not a substitute for professional medical advice. Always consult a qualified healthcare provider for diagnosis and treatment.",
            "api_response": False,
        }

    elif is_neurological:
        return {
            "diagnosis": [
                {"condition": "Neurological Disorder", "confidence": 0.72, "rationale": "Headache with dizziness, confusion, and unilateral numbness are concerning for cerebrovascular involvement.", "icd10_code": "G93.9"},
                {"condition": "Migraine", "confidence": 0.55, "rationale": "Severe headache with associated symptoms may indicate migraine.", "icd10_code": "G43.9"},
            ],
            "explanation": "Your combination of headache, dizziness, and neurological symptoms requires medical attention. These symptoms could indicate various neurological conditions.",
            "patient_explanation": "Your symptoms need medical attention. Headache with dizziness or numbness can have several causes. Please see a doctor for proper evaluation.",
            "recommendations": [
                "Seek medical evaluation promptly",
                "Note when symptoms started and how they've changed",
                "Avoid driving if experiencing dizziness or confusion",
                "Bring a list of all medications you take",
                "Follow up with a neurologist if symptoms persist",
            ],
            "severity": "high",
            "doctor_alert": True,
            "differential_diagnoses": ["Migraine with aura", "Brain tumor", "Multiple sclerosis"],
            "red_flags": [
                "Sudden severe headache (thunderclap headache)",
                "Weakness or numbness on one side of body",
                "Difficulty speaking or understanding speech",
                "Loss of consciousness",
                "Sudden vision changes",
            ],
            "confidence": {
                "overall_confidence": 0.65,
                "breakdown": {"nlp": 0.78, "vision": 0.0, "rag": 0.60, "prediction": 0.75},
            },
            "confidence_score": 0.65,
            "symptoms": symptoms,
            "timestamp": datetime.now().isoformat(),
            "disclaimer": "This is an AI-generated assessment and not a substitute for professional medical advice. Always consult a qualified healthcare provider for diagnosis and treatment.",
            "api_response": False,
        }

    elif is_psychiatric:
        return {
            "diagnosis": [
                {"condition": "Anxiety Disorder", "confidence": 0.75, "rationale": "Excessive worry, restlessness, difficulty concentrating, and sleep disturbances are core features of generalized anxiety disorder.", "icd10_code": "F41.1"},
                {"condition": "Depression", "confidence": 0.50, "rationale": "Persistent sadness, loss of interest, sleep changes, and fatigue are characteristic of major depressive disorder.", "icd10_code": "F32.9"},
            ],
            "explanation": "Your symptoms suggest an anxiety disorder. Excessive worry, difficulty concentrating, restlessness, and sleep disturbances are common features.",
            "patient_explanation": "What you're experiencing sounds like anxiety or stress. The constant worry, trouble sleeping, and feeling restless are real symptoms that can be helped. Talking to a mental health professional can make a big difference.",
            "recommendations": [
                "Speak with a mental health professional (therapist or psychiatrist)",
                "Practice relaxation techniques: deep breathing, meditation, yoga",
                "Maintain a regular sleep schedule",
                "Limit caffeine and alcohol intake",
                "Stay physically active — exercise helps reduce anxiety",
            ],
            "severity": "moderate",
            "doctor_alert": False,
            "differential_diagnoses": ["Adjustment disorder", "Hyperthyroidism", "Bipolar disorder"],
            "red_flags": [
                "Thoughts of self-harm or suicide",
                "Inability to perform daily activities",
                "Panic attacks with chest pain",
                "Complete social withdrawal",
            ],
            "confidence": {
                "overall_confidence": 0.64,
                "breakdown": {"nlp": 0.72, "vision": 0.0, "rag": 0.60, "prediction": 0.68},
            },
            "confidence_score": 0.64,
            "symptoms": symptoms,
            "timestamp": datetime.now().isoformat(),
            "disclaimer": "This is an AI-generated assessment and not a substitute for professional medical advice. Always consult a qualified healthcare provider for diagnosis and treatment.",
            "api_response": False,
        }

    else:
        return {
            "diagnosis": [
                {"condition": "Upper Respiratory Infection", "confidence": 0.65, "rationale": "Runny nose, sore throat, and sneezing are consistent with a common viral upper respiratory infection.", "icd10_code": "J06.9"},
            ],
            "explanation": "Your symptoms suggest a mild upper respiratory infection, likely a common cold. These are typically viral and self-limiting, resolving within 7-10 days without specific treatment.",
            "patient_explanation": "You likely have a common cold. It's viral, so antibiotics won't help. Rest, drink fluids, and use over-the-counter remedies for comfort. You should feel better in about a week.",
            "recommendations": [
                "Rest and stay hydrated",
                "Use saline nasal spray for congestion",
                "Take acetaminophen or ibuprofen for discomfort",
                "Monitor for worsening symptoms",
                "See a doctor if symptoms persist beyond 10 days",
            ],
            "severity": "low",
            "doctor_alert": False,
            "differential_diagnoses": ["Allergic rhinitis", "Sinusitis", "COVID-19"],
            "red_flags": [
                "Fever above 102°F",
                "Difficulty breathing",
                "Symptoms lasting more than 10 days",
            ],
            "confidence": {
                "overall_confidence": 0.60,
                "breakdown": {"nlp": 0.70, "vision": 0.0, "rag": 0.55, "prediction": 0.55},
            },
            "confidence_score": 0.60,
            "symptoms": symptoms,
            "timestamp": datetime.now().isoformat(),
            "disclaimer": "This is an AI-generated assessment and not a substitute for professional medical advice. Always consult a qualified healthcare provider for diagnosis and treatment.",
            "api_response": False,
        }


def _extract_symptoms_from_text(text: str) -> list[dict]:
    """Extract symptoms from text for display."""
    text_lower = text.lower()
    symptoms = []
    symptom_map = {
        "chest pain": ("Chest Pain", "Cardiovascular"),
        "chest pressure": ("Chest Pressure", "Cardiovascular"),
        "radiates to": ("Radiating Pain", "Cardiovascular"),
        "left arm": ("Left Arm Pain", "Cardiovascular"),
        "short of breath": ("Shortness of Breath", "Respiratory"),
        "difficulty breathing": ("Breathing Difficulty", "Respiratory"),
        "cough": ("Cough", "Respiratory"),
        "phlegm": ("Productive Cough", "Respiratory"),
        "fever": ("Fever", "Constitutional"),
        "chills": ("Chills", "Constitutional"),
        "thirsty": ("Excessive Thirst", "Endocrine"),
        "urinating": ("Frequent Urination", "Endocrine"),
        "blurred vision": ("Blurred Vision", "Ophthalmological"),
        "fatigue": ("Fatigue", "Constitutional"),
        "headache": ("Headache", "Neurological"),
        "dizziness": ("Dizziness", "Neurological"),
        "confusion": ("Confusion", "Neurological"),
        "numbness": ("Numbness", "Neurological"),
        "runny nose": ("Runny Nose", "ENT"),
        "sore throat": ("Sore Throat", "ENT"),
        "sneezing": ("Sneezing", "ENT"),
        "nausea": ("Nausea", "Gastrointestinal"),
        "vomiting": ("Vomiting", "Gastrointestinal"),
        "back pain": ("Back Pain", "Musculoskeletal"),
        "joint pain": ("Joint Pain", "Musculoskeletal"),
    }
    for keyword, (symptom, category) in symptom_map.items():
        if keyword in text_lower:
            symptoms.append({"symptom": symptom, "category": category})
    return symptoms


def show_diagnosis_page():
    """Render the redesigned diagnosis input and results page."""
    st.markdown(
        '<p class="main-header">AI Health Diagnostic Assessment</p>',
        unsafe_allow_html=True,
    )
    st.caption("Describe your symptoms — our multi-agent AI system will analyze and provide insights.")

    # Demo mode toggle
    demo_mode = st.sidebar.toggle(
        "🎭 Demo Mode",
        value=True,
        help="Use pre-computed results for smooth demonstrations (no API needed)",
    )

    if demo_mode:
        st.sidebar.info("Demo mode enabled — uses realistic pre-computed results")
    
    # Language detection indicator
    symptom_input_preview = st.session_state.get("symptom_text", "")
    if symptom_input_preview:
        from src.utils.language_detector import detect_language, get_language_name
        detected_lang = detect_language(symptom_input_preview)
        lang_name = get_language_name(detected_lang)
        if detected_lang != "en":
            st.sidebar.success(f"🌐 Detected: {lang_name}")
        else:
            st.sidebar.caption(f"Language: English")

    # Initialize follow-up session state
    if "follow_up_session" not in st.session_state:
        st.session_state.follow_up_session = {
            "active": False,
            "initial_text": "",
            "patient_history": {},
            "questions": [],
            "answers": [],
            "session_id": None,
        }
    
    if "show_sos" not in st.session_state:
        st.session_state.show_sos = False

    # Tabs for different input modes
    tab_text, tab_voice, tab_scenario = st.tabs(["Text Input", "Voice Input", "Quick Scenarios"])

    with tab_text:
        symptom_text = st.text_area(
            "Describe your symptoms",
            placeholder="e.g., I've had chest pain for 2 days with shortness of breath when walking upstairs...",
            height=120,
            key="symptom_text",
            disabled=st.session_state.follow_up_session.get("active", False),
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input("Age", min_value=0, max_value=120, value=30, key="age_input")
        with col2:
            bmi = st.number_input("BMI (optional)", min_value=10.0, max_value=60.0, value=25.0, step=0.5, key="bmi_input")
        with col3:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="gender_input")

        family_history = st.multiselect(
            "Family history (optional)",
            ["Diabetes", "Heart disease", "Cancer", "Asthma", "None"],
            key="family_history",
        )

    with tab_voice:
        st.info("Click the microphone button below and speak your symptoms. Audio will be transcribed automatically.")
        
        from streamlit_mic_recorder import mic_recorder
        
        audio = mic_recorder(
            start_prompt="Start Recording",
            stop_prompt="Stop Recording",
            key="mic_recorder",
            use_container_width=True,
        )
        
        if audio:
            with st.spinner("Transcribing audio..."):
                import tempfile
                import os
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    f.write(audio["bytes"])
                    temp_path = f.name
                
                from src.agents.voice.agent import VoiceAgent
                voice_agent = VoiceAgent()
                import asyncio
                result = asyncio.run(voice_agent.run({"audio_path": temp_path}))
                
                if result.get("transcript"):
                    st.session_state["symptom_text"] = result["transcript"]
                    st.success(f"Transcribed: {result['transcript']}")
                    st.caption(f"Language: {result.get('language', 'en')} | Confidence: {result.get('confidence', 0):.2f}")
                else:
                    st.error("Could not transcribe audio. Please try again or type your symptoms.")
                
                os.unlink(temp_path)

    with tab_scenario:
        st.info("Select a pre-built patient scenario for quick demonstration")
        scenario_name = st.selectbox(
            "Choose a scenario",
            list(DEMO_SCENARIOS.keys()),
            index=0,
            key="scenario_selector",
        )
        if scenario_name:
            scenario = DEMO_SCENARIOS[scenario_name]
            st.text_area("Symptoms", value=scenario["text"], height=100, disabled=True, key="scenario_text_display")
            st.button("Load This Scenario", type="primary", use_container_width=True, key="load_scenario_btn")
            if st.session_state.get("load_scenario_btn"):
                st.session_state["symptom_text"] = scenario["text"]
                st.session_state["age_input"] = scenario["age"]
                st.session_state["bmi_input"] = scenario["bmi"]
                st.session_state["family_history"] = scenario["family_history"]
                st.rerun()

    # Check if we're in follow-up mode
    if st.session_state.follow_up_session.get("active"):
        show_follow_up_flow(demo_mode)
        return

    # SOS Emergency Button
    st.sidebar.divider()
    st.sidebar.markdown("### 🚨 Emergency?")
    if st.sidebar.button("SOS — Emergency Symptoms", type="primary", use_container_width=True):
        st.session_state.show_sos = True
    
    # Show SOS panel
    if st.session_state.get("show_sos"):
        show_emergency_panel()
        if st.button("← Back", key="back_from_sos"):
            st.session_state.show_sos = False
            st.rerun()
        return

    # Submit button
    if st.button("Run Diagnosis", type="primary", use_container_width=True, key="run_diagnosis_btn"):
        symptom_input = st.session_state.get("symptom_text", "")
        if not symptom_input.strip():
            st.warning("Please describe your symptoms or select a scenario.")
            return

        # Check for emergency first
        with st.spinner("Checking for emergency symptoms..."):
            try:
                emergency_response = requests.post(
                    f"{API_BASE}/api/diagnosis/emergency-check",
                    json={"text": symptom_input},
                    timeout=10,
                )
                if emergency_response.status_code == 200:
                    emergency_data = emergency_response.json()
                    if emergency_data.get("is_emergency"):
                        show_emergency_panel(emergency_data)
                        return
            except Exception:
                pass  # Continue with normal diagnosis if emergency check fails

        with st.spinner("Running multi-agent diagnostic pipeline..."):
            # Agent status tracker
            status_container = st.empty()
            agents = [
                ("Orchestrator", "Planning diagnostic tasks..."),
                ("NLP Agent", "Extracting symptoms and medical entities..."),
                ("RAG Agent", "Retrieving medical knowledge from guidelines..."),
                ("Prediction Agent", "Assessing disease risk factors..."),
                ("Vision Agent", "Checking for medical images..."),
                ("Synthesis Agent", "Generating diagnostic report..."),
            ]

            progress_bar = st.progress(0)
            status_col1, status_col2 = st.columns([3, 1])

            for i, (agent_name, agent_action) in enumerate(agents):
                with status_col1:
                    status_container.info(f"🔄 **{agent_name}**: {agent_action}")
                with status_col2:
                    st.metric("", f"{i+1}/{len(agents)}")
                progress_bar.progress((i + 1) / len(agents))
                time.sleep(0.5)  # Brief pause for visual effect

            status_container.success("✅ All agents completed analysis!")
            progress_bar.progress(1.0)

            # Build patient history
            patient_history = {
                "age": st.session_state.get("age_input", 30),
                "bmi": st.session_state.get("bmi_input", 25.0),
                "gender": st.session_state.get("gender_input", ""),
            }
            fh = st.session_state.get("family_history", [])
            if fh and fh != ["None"]:
                patient_history["family_history"] = fh

            result = run_diagnosis(symptom_input, patient_history)
            display_results(result, demo_mode)


def show_disease_info(condition_name: str):
    """Display detailed information about a specific disease/condition."""
    st.divider()
    st.markdown(f"### ℹ️ {condition_name}")

    with st.spinner(f"Loading information about {condition_name}..."):
        try:
            response = requests.get(
                f"{API_BASE}/api/diagnosis/disease/{condition_name}",
                timeout=15,
            )
            if response.status_code == 200:
                data = response.json()
                display_disease_details(data)
            else:
                st.info(f"Detailed information for '{condition_name}' is not available in the database.")
        except Exception:
            st.info(f"Detailed information for '{condition_name}' is not available. API server may not be running.")

    if st.button("← Back to Results", key="back_to_results"):
        st.rerun()


def display_disease_details(data: dict):
    """Render detailed disease information."""
    # Description
    st.markdown(f"**{data.get('name', 'Unknown')}**")
    if data.get("icd10"):
        st.caption(f"ICD-10: {data['icd10']}")
    
    st.info(data.get("description", "No description available."))

    # Symptoms
    symptoms = data.get("symptoms", [])
    if symptoms:
        st.subheader("Symptoms")
        cols = st.columns(min(len(symptoms), 4))
        for i, symptom in enumerate(symptoms):
            with cols[i % 4]:
                st.markdown(f"• {symptom}")

    # Causes
    causes = data.get("causes", [])
    if causes:
        st.subheader("Common Causes")
        for cause in causes:
            st.markdown(f"• {cause}")

    # Risk Factors
    risk_factors = data.get("risk_factors", [])
    if risk_factors:
        st.subheader("Risk Factors")
        for rf in risk_factors:
            st.markdown(f"⚠️ {rf}")

    # Treatment
    treatment = data.get("treatment", [])
    if treatment:
        st.subheader("Treatment Options")
        for i, t in enumerate(treatment, 1):
            st.markdown(f"{i}. {t}")

    # When to see a doctor
    when_to_see = data.get("when_to_see_doctor", [])
    if when_to_see:
        st.subheader("🚨 When to See a Doctor")
        for w in when_to_see:
            st.warning(w)

    # Prognosis
    prognosis = data.get("prognosis", "")
    if prognosis:
        st.subheader("Prognosis")
        st.success(prognosis)

    # Prevention
    prevention = data.get("prevention", [])
    if prevention:
        st.subheader("Prevention")
        for p in prevention:
            st.markdown(f"✓ {p}")


def display_results(result: dict, demo_mode: bool = True):
    """Display diagnosis results with enhanced visualization."""
    st.divider()

    # Header row with severity, confidence, and alert
    severity = result.get("severity", "unknown")
    severity_config = {
        "critical": ("Critical", "🔴", "#dc3545", "Seek immediate medical attention"),
        "high": ("High", "🟠", "#fd7e14", "Medical consultation recommended"),
        "moderate": ("Moderate", "🟡", "#ffc107", "Monitor and consult if worsens"),
        "low": ("Low", "🟢", "#28a745", "Self-care likely sufficient"),
        "unknown": ("Unknown", "⚪", "#6c757d", "Insufficient data"),
    }
    sev_label, sev_icon, sev_color, sev_action = severity_config.get(severity, severity_config["unknown"])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div style="padding: 1rem; background: {sev_color}22; border-left: 4px solid {sev_color}; border-radius: 8px;">
                <div style="font-size: 1.5rem; font-weight: bold; color: {sev_color};">
                    {sev_icon} {sev_label}
                </div>
                <div style="color: {sev_color}; font-size: 0.9rem;">{sev_action}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        conf = result.get("confidence_score", 0)
        if isinstance(conf, dict):
            conf = conf.get("overall_confidence", 0)
        st.metric("Confidence", f"{conf * 100:.0f}%")
    with col3:
        alert = "⚠️ Yes" if result.get("doctor_alert") else "No"
        st.metric("Doctor Alert", alert)

    # Red flags - prominent display
    red_flags = result.get("red_flags", [])
    if red_flags:
        st.error("### 🚨 Red Flags — Seek Immediate Care If Present\n" + "\n".join(f"- **{f}**" for f in red_flags))

    # Diagnoses with confidence bars
    st.subheader("Possible Conditions")
    diagnoses = result.get("diagnosis", [])
    if diagnoses:
        for d in diagnoses:
            conf = d.get("confidence", 0)
            condition = d.get("condition", "Unknown")
            rationale = d.get("rationale", "")
            icd10 = d.get("icd10_code", "")

            # Color based on confidence
            bar_color = "#28a745" if conf > 0.7 else ("#ffc107" if conf > 0.4 else "#fd7e14")

            with st.expander(f"{condition} — {conf*100:.0f}% confidence", expanded=True):
                st.progress(conf, text=f"Confidence: {conf*100:.0f}%")
                if rationale:
                    st.write(f"**Rationale:** {rationale}")
                if icd10:
                    st.caption(f"ICD-10: {icd10}")
                if conf > 0.7:
                    st.warning("High confidence — medical consultation strong recommended")
                
                # Disease info button
                col_info, _ = st.columns([1, 4])
                with col_info:
                    if st.button(f"ℹ️ Learn More", key=f"info_{condition}_{conf}", use_container_width=True):
                        show_disease_info(condition)
    else:
        st.caption("No specific conditions identified")

    # Confidence breakdown chart
    confidence = result.get("confidence", {})
    breakdown = confidence.get("breakdown", {})
    if breakdown:
        st.subheader("Agent Confidence Breakdown")
        cols = st.columns(4)
        for i, (agent, score) in enumerate(breakdown.items()):
            with cols[i]:
                st.metric(agent.upper(), f"{score*100:.0f}%")
                st.progress(score)

    # Symptoms detected
    st.subheader("Symptoms Detected")
    symptoms = result.get("symptoms", [])
    if symptoms:
        # Group by category
        categories = {}
        for s in symptoms:
            cat = s.get("category", "Other")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(s["symptom"])

        cols = st.columns(min(len(categories), 4))
        for i, (cat, syms) in enumerate(categories.items()):
            with cols[i]:
                st.markdown(f"**{cat}**")
                for sym in syms:
                    st.write(f"• {sym}")
    else:
        st.caption("No symptoms detected")

    # Differential diagnoses
    differentials = result.get("differential_diagnoses", [])
    if differentials:
        st.subheader("Differential Diagnoses (Alternative Possibilities)")
        for d in differentials:
            st.write(f"• {d}")

    # AI Explanation
    st.subheader("AI Analysis Summary")
    st.info(result.get("explanation", "No explanation available."))

    # Patient-friendly explanation
    patient_exp = result.get("patient_explanation", "")
    if patient_exp:
        st.subheader("What This Means for You")
        st.success(patient_exp)

    # Recommendations
    st.subheader("Recommendations")
    for i, rec in enumerate(result.get("recommendations", []), 1):
        icon = "⚠️" if "immediate" in rec.lower() or "emergency" in rec.lower() else "✓"
        st.write(f"{icon} **{i}.** {rec}")

    # Follow-up questions section
    st.divider()
    st.subheader("Want a More Accurate Diagnosis?")
    st.caption("Answer a few clarifying questions to refine your results.")
    
    if st.button("Ask Follow-up Questions", type="secondary", use_container_width=True, key="ask_followup_btn"):
        # Start follow-up flow
        st.session_state.follow_up_session = {
            "active": True,
            "initial_text": st.session_state.get("symptom_text", ""),
            "patient_history": {
                "age": st.session_state.get("age_input", 30),
                "bmi": st.session_state.get("bmi_input", 25.0),
                "gender": st.session_state.get("gender_input", ""),
                "family_history": st.session_state.get("family_history", []),
            },
            "questions": [],
            "answers": [],
            "session_id": None,
        }
        st.rerun()

    # Report Export
    st.divider()
    st.subheader("Export Report")
    
    export_col1, export_col2, export_col3 = st.columns(3)
    
    # Prepare export data
    export_data = {
        "symptom_input": st.session_state.get("symptom_text", ""),
        "age": st.session_state.get("age_input", ""),
        "gender": st.session_state.get("gender_input", ""),
        "bmi": st.session_state.get("bmi_input", ""),
        "severity": severity,
        "severity_action": sev_action,
        "diagnosis": diagnoses,
        "red_flags": red_flags,
        "symptoms": symptoms,
        "confidence": confidence,
        "recommendations": result.get("recommendations", []),
        "explanation": result.get("explanation", ""),
        "patient_explanation": result.get("patient_explanation", ""),
        "disclaimer": result.get("disclaimer", ""),
    }
    
    with export_col1:
        pdf_bytes = generate_pdf_report(export_data)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="📄 Download PDF",
            data=pdf_bytes,
            file_name=f"diagnosis_report_{timestamp}.pdf",
            mime="application/pdf" if pdf_bytes.startswith(b"%PDF") else "text/plain",
            use_container_width=True,
        )
    
    with export_col2:
        csv_bytes = generate_csv_report(export_data)
        st.download_button(
            label="📊 Download CSV",
            data=csv_bytes,
            file_name=f"diagnosis_report_{timestamp}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    
    with export_col3:
        text_report = export_data.get("explanation", "N/A")
        st.download_button(
            label="📝 Copy Summary",
            data=text_report,
            file_name=f"diagnosis_summary_{timestamp}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    # Disclaimer
    st.divider()
    st.caption(result.get("disclaimer", ""))

    # Source indicator
    if not result.get("api_response", False):
        st.info("🎭 Showing demo results — start the API server with `make api` for live AI analysis.")


def show_follow_up_flow(demo_mode: bool = True):
    """Display and process follow-up clarifying questions."""
    st.divider()
    st.markdown("### Follow-up Questions")
    st.caption("Answer these questions to refine your diagnosis.")

    session = st.session_state.follow_up_session

    # Fetch questions if not already loaded
    if not session.get("questions"):
        with st.spinner("Generating clarifying questions..."):
            if not demo_mode:
                try:
                    response = requests.post(
                        f"{API_BASE}/api/diagnosis/follow-up",
                        json={
                            "text": session["initial_text"],
                            "patient_history": session["patient_history"],
                        },
                        timeout=30,
                    )
                    if response.status_code == 200:
                        data = response.json()
                        session["questions"] = data.get("questions", [])
                        session["session_id"] = data.get("session_id")
                    else:
                        session["questions"] = _get_demo_follow_up_questions(session["initial_text"])
                except Exception:
                    session["questions"] = _get_demo_follow_up_questions(session["initial_text"])
            else:
                session["questions"] = _get_demo_follow_up_questions(session["initial_text"])

    # Display questions
    if session["questions"]:
        for i, q in enumerate(session["questions"]):
            st.markdown(f"**{i+1}. {q['question']}**")
            if q.get("rationale"):
                st.caption(f"💡 {q['rationale']}")

            q_type = q.get("type", "text")
            if q_type == "choice" and q.get("options"):
                answer = st.selectbox(
                    "Your answer:",
                    q["options"],
                    key=f"followup_q_{i}",
                    label_visibility="collapsed",
                )
            elif q_type == "yes_no":
                answer = st.radio(
                    "Your answer:",
                    ["Yes", "No"],
                    key=f"followup_yn_{i}",
                    horizontal=True,
                    label_visibility="collapsed",
                )
            else:
                answer = st.text_input(
                    "Your answer:",
                    key=f"followup_txt_{i}",
                    label_visibility="collapsed",
                )

            session["answers"].append({
                "question": q["question"],
                "answer": answer,
                "category": q.get("category", "general"),
            })
            st.divider()

        # Submit answers button
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Submit Answers & Refine Diagnosis", type="primary", use_container_width=True):
                with st.spinner("Refining diagnosis with your answers..."):
                    # Build enriched text
                    enriched_text = session["initial_text"]
                    answer_context = "\nAdditional context:\n"
                    for qa in session["answers"]:
                        answer_context += f"- {qa['question']}: {qa['answer']}\n"
                    enriched_text += answer_context

                    # Re-run diagnosis
                    result = run_diagnosis(enriched_text, session["patient_history"])
                    
                    # End follow-up session
                    session["active"] = False
                    session["questions"] = []
                    session["answers"] = []
                    
                    # Show refined results
                    st.success("Diagnosis refined with your answers!")
                    display_results(result, demo_mode)
        with col2:
            if st.button("Skip Follow-up", use_container_width=True):
                session["active"] = False
                session["questions"] = []
                session["answers"] = []
                st.rerun()
    else:
        st.warning("No follow-up questions available.")
        if st.button("Back to Results"):
            session["active"] = False
            st.rerun()


def _get_demo_follow_up_questions(text: str) -> list[dict]:
    """Generate demo follow-up questions based on symptom text."""
    text_lower = text.lower()
    questions = []

    if any(w in text_lower for w in ["chest", "heart", "breath"]):
        questions = [
            {
                "question": "How long have you been experiencing chest pain?",
                "type": "choice",
                "options": ["Less than 24 hours", "1-3 days", "4-7 days", "More than a week"],
                "category": "duration",
                "rationale": "Duration helps distinguish acute cardiac events from chronic conditions",
            },
            {
                "question": "Does the pain radiate to your arm, jaw, or back?",
                "type": "yes_no",
                "category": "associated_symptoms",
                "rationale": "Radiating pain is a key indicator of cardiac involvement",
            },
            {
                "question": "Do you experience sweating or nausea with the pain?",
                "type": "yes_no",
                "category": "associated_symptoms",
                "rationale": "These are important cardiac warning signs",
            },
        ]
    elif any(w in text_lower for w in ["headache", "head", "migraine"]):
        questions = [
            {
                "question": "How would you describe the pain?",
                "type": "choice",
                "options": ["Throbbing/pulsing", "Constant pressure", "Sharp/stabbing", "Dull ache"],
                "category": "severity",
                "rationale": "Pain type helps differentiate migraine from tension headache",
            },
            {
                "question": "Do you experience sensitivity to light or sound?",
                "type": "yes_no",
                "category": "associated_symptoms",
                "rationale": "Photophobia and phonophobia are common in migraines",
            },
            {
                "question": "Have you noticed any triggers (stress, certain foods, lack of sleep)?",
                "type": "text",
                "category": "triggers",
                "rationale": "Identifying triggers helps with prevention and diagnosis",
            },
        ]
    elif any(w in text_lower for w in ["fever", "cough", "cold"]):
        questions = [
            {
                "question": "What is your current temperature?",
                "type": "choice",
                "options": ["No fever (below 99°F)", "Low-grade (99-100.4°F)", "Moderate (100.5-102°F)", "High (above 102°F)"],
                "category": "severity",
                "rationale": "Fever level helps assess infection severity",
            },
            {
                "question": "Are you coughing up phlegm? If so, what color?",
                "type": "choice",
                "options": ["No phlegm (dry cough)", "Clear/white", "Yellow/green", "Brown or blood-tinged"],
                "category": "associated_symptoms",
                "rationale": "Phlegm color can indicate bacterial vs viral infection",
            },
            {
                "question": "Do you have any difficulty breathing?",
                "type": "yes_no",
                "category": "associated_symptoms",
                "rationale": "Breathing difficulty may indicate lower respiratory involvement",
            },
        ]
    else:
        questions = [
            {
                "question": "How long have you been experiencing these symptoms?",
                "type": "choice",
                "options": ["Less than 24 hours", "1-3 days", "4-7 days", "More than a week"],
                "category": "duration",
                "rationale": "Duration helps distinguish acute vs chronic conditions",
            },
            {
                "question": "How would you rate the severity?",
                "type": "choice",
                "options": ["Mild - barely noticeable", "Moderate - uncomfortable", "Severe - impacting daily life", "Very severe - unable to function"],
                "category": "severity",
                "rationale": "Severity assessment helps prioritize urgency",
            },
            {
                "question": "Do you have any existing medical conditions?",
                "type": "yes_no",
                "category": "medical_history",
                "rationale": "Existing conditions can influence diagnosis",
            },
        ]

    return questions


def show_emergency_panel(emergency_data: dict = None):
    """Display emergency SOS panel with immediate action guidance."""
    st.markdown("---")
    st.error("### 🚨 MEDICAL EMERGENCY DETECTED")
    
    if emergency_data:
        triggered = emergency_data.get("triggered_keywords", [])
        confidence = emergency_data.get("confidence", 0)
        
        st.markdown(f"**Emergency signals detected:** {', '.join(triggered)}")
        st.markdown(f"**Confidence:** {confidence*100:.0f}%")
    
    st.divider()
    
    # Emergency actions
    st.markdown("### Immediate Actions Required")
    
    actions = [
        "Call **112** (National Emergency Number) or **108** (Ambulance) immediately",
        "Do **not** drive yourself to the hospital",
        "If alone, unlock your door and call a neighbor or family member",
        "Keep your phone nearby and stay calm",
    ]
    
    if emergency_data and emergency_data.get("actions"):
        actions = emergency_data["actions"]
    
    for i, action in enumerate(actions, 1):
        st.markdown(f"**{i}.** {action}")
    
    st.divider()
    
    # Emergency numbers
    st.markdown("### Emergency Numbers (India)")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div style="background: #dc354522; padding: 1rem; border-radius: 8px; text-align: center;">
            <div style="font-size: 2rem; font-weight: bold; color: #dc3545;">112</div>
            <div>National Emergency</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background: #dc354522; padding: 1rem; border-radius: 8px; text-align: center;">
            <div style="font-size: 2rem; font-weight: bold; color: #dc3545;">108</div>
            <div>Ambulance</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background: #dc354522; padding: 1rem; border-radius: 8px; text-align: center;">
            <div style="font-size: 2rem; font-weight: bold; color: #dc3545;">102</div>
            <div>Maternal/Child</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div style="background: #dc354522; padding: 1rem; border-radius: 8px; text-align: center;">
            <div style="font-size: 2rem; font-weight: bold; color: #dc3545;">100</div>
            <div>Police</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Situation-specific guidance
    st.markdown("### Situation-Specific Guidance")
    
    with st.expander("💓 If Chest Pain"):
        st.markdown("""
        - Sit down, rest, and stay calm
        - Chew one aspirin (300mg) if available and not allergic
        - Loosen tight clothing
        - Do not eat or drink anything
        - Wait for ambulance — do not drive yourself
        """)
    
    with st.expander("🧠 If Stroke Symptoms"):
        st.markdown("""
        - **Note the time symptoms started** — this is critical for treatment
        - Look for FAST signs:
          - **F**ace drooping
          - **A**rm weakness
          - **S**peech difficulty
          - **T**ime to call emergency
        - Do not give food or drink
        - Keep the person lying on their side if unconscious
        """)
    
    with st.expander("🩸 If Severe Bleeding"):
        st.markdown("""
        - Apply direct pressure with a clean cloth or bandage
        - Elevate the injured area above heart level if possible
        - Do not remove the cloth if it soaks through — add more on top
        - Do not apply a tourniquet unless trained to do so
        """)
    
    with st.expander("😰 If Severe Allergic Reaction"):
        st.markdown("""
        - Use an epinephrine auto-injector (EpiPen) if available
        - Lie down with legs elevated
        - Remove the allergen if possible
        - Do not give oral medications if throat is swelling
        """)
    
    st.divider()
    st.warning("This is an automated emergency detection. Always call emergency services immediately for any medical emergency.")
