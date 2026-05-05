"""Diagnosis API routes."""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import os
import tempfile
import asyncio
from loguru import logger

from src.agents.orchestrator.agent import OrchestratorAgent

router = APIRouter(prefix="/diagnosis", tags=["diagnosis"])

# Global orchestrator instance (lazy-loaded)
_orchestrator = None


def get_orchestrator() -> OrchestratorAgent:
    """Get or create the orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = OrchestratorAgent()
    return _orchestrator


class DiagnosisRequest(BaseModel):
    """Request body for diagnostic analysis."""
    text: str = Field(..., description="Symptom description in natural language")
    image_path: Optional[str] = Field(None, description="Path to uploaded medical image")
    patient_history: Optional[dict] = Field(None, description="Patient demographics and history")
    language: Optional[str] = Field(None, description="Target language for response (e.g., 'hi' for Hindi)")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "I have had a severe headache for 3 days with mild fever",
                "patient_history": {
                    "age": 35,
                    "gender": "female",
                    "bmi": 24.5,
                    "conditions": ["migraine"],
                    "family_history": ["diabetes"],
                },
                "language": "en",
            }
        }


class DiagnosisResponse(BaseModel):
    """Response from diagnostic analysis."""
    diagnosis: list[dict] = Field(default_factory=list, description="List of possible conditions")
    explanation: str = Field("", description="Medical explanation of findings")
    patient_explanation: str = Field("", description="Patient-friendly explanation")
    recommendations: list[str] = Field(default_factory=list)
    severity: str = "unknown"
    doctor_alert: bool = False
    differential_diagnoses: list[str] = Field(default_factory=list)
    red_flags: list[str] = Field(default_factory=list)
    confidence: dict = Field(default_factory=dict)
    disclaimer: str = ""


@router.post("/analyze", response_model=DiagnosisResponse)
async def analyze_symptoms(request: DiagnosisRequest):
    """Run full diagnostic analysis on symptom text and optional image.

    This endpoint:
    1. Detects input language and translates to English if needed
    2. Extracts symptoms using NLP (BioBERT)
    3. Retrieves relevant medical knowledge (RAG + FAISS)
    4. Assesses disease risk (XGBoost/rule-based)
    5. Analyzes uploaded image if provided (ResNet-50)
    6. Synthesizes all findings into a diagnostic report (Gemini 1.5 Flash)
    7. Translates results back to input language if needed
    """
    try:
        # Language detection
        from src.utils.language_detector import detect_language, is_multilingual
        
        detected_lang = detect_language(request.text)
        original_lang = request.language or detected_lang
        
        # If input is non-English, translate to English for processing
        processing_text = request.text
        if is_multilingual(request.text) and detected_lang != "en":
            from src.llm.translation import TranslationService
            translator = TranslationService()
            processing_text = translator.translate_to_english(request.text, detected_lang)
            logger.info(f"Translated input from {detected_lang} to English for processing")
        
        orchestrator = get_orchestrator()

        input_data = {
            "text": processing_text,
            "image_path": request.image_path,
            "patient_history": request.patient_history,
        }

        result = await orchestrator.run(input_data)

        # Extract synthesis result
        synthesis = result.get("synthesis_result", {})

        # Translate results back to original language if needed
        if original_lang != "en" and original_lang in ["hi", "es", "ar", "fr", "de", "ur", "bn", "ta", "te", "mr", "gu"]:
            from src.llm.translation import TranslationService
            translator = TranslationService()
            synthesis = translator.translate_diagnosis(synthesis, original_lang)
            logger.info(f"Translated diagnosis results to {original_lang}")

        return DiagnosisResponse(
            diagnosis=synthesis.get("diagnosis", []),
            explanation=synthesis.get("explanation", ""),
            patient_explanation=synthesis.get("patient_explanation", ""),
            recommendations=synthesis.get("recommendations", []),
            severity=synthesis.get("severity", "unknown"),
            doctor_alert=synthesis.get("doctor_alert", False),
            differential_diagnoses=synthesis.get("differential_diagnoses", []),
            red_flags=synthesis.get("red_flags", []),
            confidence=synthesis.get("confidence", {}),
            disclaimer=synthesis.get("disclaimer", ""),
        )
    except Exception as e:
        logger.error(f"Diagnosis analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


class FollowUpRequest(BaseModel):
    """Request for generating follow-up questions."""
    text: str = Field(..., description="Initial symptom description")
    patient_history: Optional[dict] = Field(None, description="Patient demographics and history")
    previous_questions: Optional[list[dict]] = Field(None, description="Previously asked questions and answers")


class FollowUpResponse(BaseModel):
    """Response containing follow-up questions."""
    questions: list[dict] = Field(default_factory=list, description="List of clarifying questions")
    has_more: bool = False
    session_id: str = ""


@router.post("/follow-up", response_model=FollowUpResponse)
async def generate_follow_up(request: FollowUpRequest):
    """Generate clarifying follow-up questions to refine diagnosis.

    This endpoint:
    1. Analyzes initial symptoms to identify information gaps
    2. Generates 2-3 targeted clarifying questions
    3. Returns questions with expected answer types
    """
    try:
        from src.llm.openrouter_client import OpenRouterClient
        import json
        import uuid

        client = OpenRouterClient()

        # Build context from patient history
        patient_ctx = ""
        if request.patient_history:
            parts = []
            if "age" in request.patient_history:
                parts.append(f"Age: {request.patient_history['age']}")
            if "gender" in request.patient_history:
                parts.append(f"Gender: {request.patient_history['gender']}")
            if "bmi" in request.patient_history:
                parts.append(f"BMI: {request.patient_history['bmi']}")
            if "conditions" in request.patient_history:
                parts.append(f"Existing conditions: {', '.join(request.patient_history['conditions'])}")
            if "family_history" in request.patient_history:
                parts.append(f"Family history: {', '.join(request.patient_history['family_history'])}")
            patient_ctx = "\n".join(parts)

        # Build conversation context from previous Q&A
        prev_ctx = ""
        if request.previous_questions:
            prev_ctx = "Previously asked questions and answers:\n"
            for qa in request.previous_questions:
                prev_ctx += f"Q: {qa.get('question', '')}\nA: {qa.get('answer', 'Not answered')}\n"

        prompt = f"""You are a medical diagnostic assistant. Based on the patient's initial symptom description, generate 2-3 clarifying follow-up questions that would help narrow down the diagnosis.

PATIENT CONTEXT:
{patient_ctx or "Not provided"}

INITIAL SYMPTOMS:
{request.text}

{prev_ctx}

Generate questions that:
1. Ask about symptom duration, severity, and timing
2. Ask about associated symptoms not yet mentioned
3. Ask about relevant medical history or triggers

Return a JSON array of questions with this structure:
[
  {{
    "question": "How long have you been experiencing this symptom?",
    "type": "text",
    "options": null,
    "category": "duration",
    "rationale": "Duration helps distinguish acute vs chronic conditions"
  }}
]

Question types: "text" (free text), "choice" (multiple choice with options), "yes_no" (yes/no question).
For "choice" type, include an "options" array with 3-4 options.

Categories: duration, severity, associated_symptoms, triggers, medical_history, lifestyle.

Return valid JSON array only. No markdown, no explanations."""

        system_message = "You are a medical diagnostic assistant that asks clarifying questions. Return valid JSON only."

        raw_response = client.generate_json(
            prompt=prompt,
            system_message=system_message,
            temperature=0.5,
            max_tokens=1024,
        )

        # Handle response - could be a list or a dict with "questions" key
        if isinstance(raw_response, list):
            questions = raw_response
        elif isinstance(raw_response, dict) and "questions" in raw_response:
            questions = raw_response["questions"]
        elif isinstance(raw_response, dict) and "error" in raw_response:
            # Fallback to rule-based questions
            questions = _generate_rule_based_questions(request.text)
        else:
            questions = _generate_rule_based_questions(request.text)

        # Ensure each question has required fields
        for q in questions:
            q.setdefault("type", "text")
            q.setdefault("options", None)
            q.setdefault("category", "general")
            q.setdefault("rationale", "")

        return FollowUpResponse(
            questions=questions[:3],  # Max 3 questions
            has_more=True,
            session_id=str(uuid.uuid4()),
        )
    except Exception as e:
        logger.error(f"Follow-up question generation failed: {e}")
        # Fallback
        return FollowUpResponse(
            questions=_generate_rule_based_questions(request.text),
            has_more=False,
            session_id=str(uuid.uuid4()),
        )


class RefineDiagnosisRequest(BaseModel):
    """Request to refine diagnosis with follow-up answers."""
    text: str = Field(..., description="Initial symptom description")
    patient_history: Optional[dict] = Field(None, description="Patient demographics and history")
    follow_up_answers: list[dict] = Field(default_factory=list, description="Answers to follow-up questions")


@router.post("/refine", response_model=DiagnosisResponse)
async def refine_diagnosis(request: RefineDiagnosisRequest):
    """Re-run diagnosis incorporating follow-up question answers.

    This endpoint:
    1. Combines initial symptoms with follow-up answers
    2. Re-runs the full diagnostic pipeline
    3. Returns refined diagnosis with higher confidence
    """
    try:
        orchestrator = get_orchestrator()

        # Combine initial text with follow-up answers for richer context
        enriched_text = request.text
        if request.follow_up_answers:
            answer_context = "\nAdditional context from follow-up:\n"
            for qa in request.follow_up_answers:
                answer_context += f"- {qa.get('question', '')}: {qa.get('answer', '')}\n"
            enriched_text += answer_context

        input_data = {
            "text": enriched_text,
            "patient_history": request.patient_history,
        }

        result = await orchestrator.run(input_data)
        synthesis = result.get("synthesis_result", {})

        return DiagnosisResponse(
            diagnosis=synthesis.get("diagnosis", []),
            explanation=synthesis.get("explanation", ""),
            patient_explanation=synthesis.get("patient_explanation", ""),
            recommendations=synthesis.get("recommendations", []),
            severity=synthesis.get("severity", "unknown"),
            doctor_alert=synthesis.get("doctor_alert", False),
            differential_diagnoses=synthesis.get("differential_diagnoses", []),
            red_flags=synthesis.get("red_flags", []),
            confidence=synthesis.get("confidence", {}),
            disclaimer=synthesis.get("disclaimer", ""),
        )
    except Exception as e:
        logger.error(f"Refined diagnosis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")


def _generate_rule_based_questions(text: str) -> list[dict]:
    """Generate rule-based follow-up questions when LLM is unavailable."""
    text_lower = text.lower()
    questions = []

    # Always ask about duration
    if not any(w in text_lower for w in ["days", "weeks", "months", "years", "since", "started"]):
        questions.append({
            "question": "How long have you been experiencing these symptoms?",
            "type": "choice",
            "options": ["Less than 24 hours", "1-3 days", "4-7 days", "More than a week"],
            "category": "duration",
            "rationale": "Duration helps distinguish acute vs chronic conditions",
        })

    # Ask about severity
    if not any(w in text_lower for w in ["severe", "mild", "moderate", "pain scale", "worse"]):
        questions.append({
            "question": "How would you rate the severity of your symptoms?",
            "type": "choice",
            "options": ["Mild - barely noticeable", "Moderate - uncomfortable but manageable", "Severe - significantly impacting daily life", "Very severe - unable to function"],
            "category": "severity",
            "rationale": "Severity assessment helps prioritize urgency",
        })

    # Ask about associated symptoms based on keywords
    if any(w in text_lower for w in ["headache", "head", "migraine"]):
        questions.append({
            "question": "Do you experience any of these accompanying symptoms?",
            "type": "choice",
            "options": ["Nausea or vomiting", "Sensitivity to light/sound", "Vision changes", "None of these"],
            "category": "associated_symptoms",
            "rationale": "Associated symptoms help differentiate headache types",
        })
    elif any(w in text_lower for w in ["chest", "heart", "breath"]):
        questions.append({
            "question": "Do you experience any of these accompanying symptoms?",
            "type": "choice",
            "options": ["Pain radiating to arm/jaw", "Sweating", "Nausea", "Dizziness"],
            "category": "associated_symptoms",
            "rationale": "These are important cardiac warning signs",
        })
    elif any(w in text_lower for w in ["fever", "cough", "cold"]):
        questions.append({
            "question": "What is your current temperature?",
            "type": "choice",
            "options": ["No fever (below 99°F)", "Low-grade (99-100.4°F)", "Moderate (100.5-102°F)", "High (above 102°F)"],
            "category": "severity",
            "rationale": "Fever level helps assess infection severity",
        })
    else:
        # Generic follow-up
        questions.append({
            "question": "Have you noticed anything that makes your symptoms better or worse?",
            "type": "text",
            "options": None,
            "category": "triggers",
            "rationale": "Identifying triggers helps narrow down causes",
        })

    # Add a medical history question if not already covered
    if not any(w in text_lower for w in ["history", "condition", "medication", "allergy", "diagnosed"]):
        questions.append({
            "question": "Do you have any existing medical conditions or take regular medications?",
            "type": "yes_no",
            "options": None,
            "category": "medical_history",
            "rationale": "Existing conditions can influence diagnosis and treatment",
        })

    return questions[:3]


@router.post("/analyze-with-image")
async def analyze_with_image(
    text: str = Form(..., description="Symptom description"),
    age: Optional[int] = Form(None),
    gender: Optional[str] = Form(None),
    bmi: Optional[float] = Form(None),
    conditions: Optional[str] = Form(None, description="Comma-separated existing conditions"),
    family_history: Optional[str] = Form(None, description="Comma-separated family history"),
    image: Optional[UploadFile] = File(None, description="Medical image (X-ray, etc.)"),
):
    """Analyze symptoms with an uploaded medical image.

    Accepts multipart form data with symptom text and optional image file.
    """
    image_path = None

    try:
        # Save uploaded image temporarily
        if image:
            suffix = os.path.splitext(image.filename)[1] if image.filename else ".jpg"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                content = await image.read()
                tmp.write(content)
                image_path = tmp.name

        # Build patient history
        patient_history = {}
        if age:
            patient_history["age"] = age
        if gender:
            patient_history["gender"] = gender
        if bmi:
            patient_history["bmi"] = bmi
        if conditions:
            patient_history["conditions"] = [c.strip() for c in conditions.split(",")]
        if family_history:
            patient_history["family_history"] = [h.strip() for h in family_history.split(",")]

        orchestrator = get_orchestrator()

        input_data = {
            "text": text,
            "image_path": image_path,
            "patient_history": patient_history if patient_history else None,
        }

        result = await orchestrator.run(input_data)
        synthesis = result.get("synthesis_result", {})

        return {
            "diagnosis": synthesis.get("diagnosis", []),
            "explanation": synthesis.get("explanation", ""),
            "patient_explanation": synthesis.get("patient_explanation", ""),
            "recommendations": synthesis.get("recommendations", []),
            "severity": synthesis.get("severity", "unknown"),
            "doctor_alert": synthesis.get("doctor_alert", False),
            "differential_diagnoses": synthesis.get("differential_diagnoses", []),
            "red_flags": synthesis.get("red_flags", []),
            "confidence": synthesis.get("confidence", {}),
            "disclaimer": synthesis.get("disclaimer", ""),
        }
    except Exception as e:
        logger.error(f"Analysis with image failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    finally:
        # Clean up temp image
        if image_path and os.path.exists(image_path):
            try:
                os.unlink(image_path)
            except Exception:
                pass


DISEASE_DATABASE = {
    "upper respiratory infection": {
        "name": "Upper Respiratory Infection",
        "icd10": "J06.9",
        "description": "Acute infection of the upper airway including nose, sinuses, pharynx, and larynx. Most commonly viral and self-limiting.",
        "symptoms": ["Runny nose", "Nasal congestion", "Sore throat", "Cough", "Sneezing", "Mild fever", "Headache"],
        "causes": ["Rhinovirus", "Coronavirus", "Adenovirus", "Respiratory syncytial virus", "Influenza virus"],
        "risk_factors": ["Close contact with infected individuals", "Weakened immune system", "Smoking", "Allergies", "Seasonal changes"],
        "treatment": ["Rest and hydration", "Over-the-counter analgesics (acetaminophen, ibuprofen)", "Saline nasal spray", "Decongestants", "Throat lozenges"],
        "when_to_see_doctor": ["Symptoms lasting more than 10 days", "Fever above 102°F (38.9°C)", "Difficulty breathing", "Severe sore throat with white patches", "Symptoms worsening after initial improvement"],
        "prognosis": "Excellent. Most cases resolve within 7-10 days without complications.",
        "prevention": ["Frequent handwashing", "Avoid close contact with sick individuals", "Don't touch face with unwashed hands", "Annual flu vaccination"],
    },
    "pneumonia": {
        "name": "Pneumonia",
        "icd10": "J18.9",
        "description": "Acute infection of the pulmonary parenchyma causing inflammation and fluid accumulation in the alveoli.",
        "symptoms": ["Productive cough", "Fever and chills", "Shortness of breath", "Chest pain when breathing", "Fatigue", "Nausea", "Confusion (elderly)"],
        "causes": ["Streptococcus pneumoniae", "Haemophilus influenzae", "Mycoplasma pneumoniae", "Viral pathogens", "Fungal organisms"],
        "risk_factors": ["Age >65 or <2", "Smoking", "Chronic lung disease", "Weakened immune system", "Recent viral infection", "Hospitalization"],
        "treatment": ["Antibiotics (bacterial)", "Antiviral medications (viral)", "Rest and fluids", "Fever reducers", "Hospitalization for severe cases"],
        "when_to_see_doctor": ["Difficulty breathing", "Chest pain", "Persistent fever above 102°F", "Coughing up blood", "Confusion or altered mental state"],
        "prognosis": "Good with prompt treatment. Recovery typically takes 1-3 weeks. Higher risk in elderly and immunocompromised.",
        "prevention": ["Pneumococcal vaccination", "Annual flu vaccine", "Hand hygiene", "Don't smoke", "Maintain healthy immune system"],
    },
    "type 2 diabetes": {
        "name": "Type 2 Diabetes Mellitus",
        "icd10": "E11.9",
        "description": "Chronic metabolic disorder characterized by insulin resistance and relative insulin deficiency, leading to elevated blood glucose levels.",
        "symptoms": ["Excessive thirst (polydipsia)", "Frequent urination (polyuria)", "Fatigue", "Blurred vision", "Slow wound healing", "Unexplained weight loss", "Tingling in extremities"],
        "causes": ["Insulin resistance", "Genetic predisposition", "Obesity", "Sedentary lifestyle", "Pancreatic beta-cell dysfunction"],
        "risk_factors": ["Age >45", "Overweight/obesity", "Family history", "Sedentary lifestyle", "Gestational diabetes history", "Polycystic ovary syndrome", "Certain ethnicities"],
        "treatment": ["Lifestyle modifications (diet, exercise)", "Metformin (first-line)", "Other oral medications (SGLT2 inhibitors, DPP-4 inhibitors)", "Insulin therapy if needed", "Regular blood glucose monitoring"],
        "when_to_see_doctor": ["Excessive thirst and urination", "Unexplained weight loss", "Blurred vision", "Slow-healing sores", "Frequent infections"],
        "prognosis": "Manageable with proper treatment. Poor control leads to complications: neuropathy, retinopathy, nephropathy, cardiovascular disease.",
        "prevention": ["Maintain healthy weight", "Regular physical activity", "Balanced diet", "Regular screening if high risk"],
    },
    "cardiovascular disease": {
        "name": "Cardiovascular Disease",
        "icd10": "I25.9",
        "description": "Broad category of disorders affecting the heart and blood vessels, including coronary artery disease, heart failure, and arrhythmias.",
        "symptoms": ["Chest pain or pressure", "Shortness of breath", "Pain radiating to arm/jaw", "Fatigue", "Dizziness", "Swelling in legs", "Palpitations"],
        "causes": ["Atherosclerosis", "High blood pressure", "High cholesterol", "Blood clots", "Coronary artery damage"],
        "risk_factors": ["Hypertension", "High cholesterol", "Smoking", "Diabetes", "Obesity", "Family history", "Sedentary lifestyle", "Age >55 (male) / >65 (female)"],
        "treatment": ["Lifestyle changes (diet, exercise)", "Statins for cholesterol", "Blood pressure medications", "Antiplatelet therapy", "Surgical interventions if needed"],
        "when_to_see_doctor": ["Chest pain or pressure", "Shortness of breath at rest", "Pain radiating to arm or jaw", "Sudden dizziness or fainting", "Rapid or irregular heartbeat"],
        "prognosis": "Varies by condition. Early detection and treatment significantly improve outcomes. Leading cause of death worldwide.",
        "prevention": ["Don't smoke", "Regular exercise", "Healthy diet", "Manage blood pressure and cholesterol", "Control diabetes", "Maintain healthy weight"],
    },
    "migraine": {
        "name": "Migraine",
        "icd10": "G43.9",
        "description": "Recurrent primary headache disorder characterized by moderate to severe throbbing pain, often unilateral, with associated neurological symptoms.",
        "symptoms": ["Throbbing headache", "Nausea and vomiting", "Sensitivity to light", "Sensitivity to sound", "Visual aura", "Dizziness", "Fatigue after attack"],
        "causes": ["Neurological disorder", "Genetic predisposition", "Neurotransmitter imbalances", "Blood vessel changes", "Trigeminal nerve activation"],
        "risk_factors": ["Family history", "Female sex", "Hormonal changes", "Stress", "Sleep disturbances", "Certain foods"],
        "treatment": ["Acute: triptans, NSAIDs", "Preventive: beta-blockers, anticonvulsants, CGRP inhibitors", "Lifestyle modifications", "Trigger avoidance", "Botox for chronic migraines"],
        "when_to_see_doctor": ["Sudden severe headache (thunderclap)", "Headache with fever, stiff neck", "New headaches after age 50", "Headache after head injury", "Headaches that worsen over time"],
        "prognosis": "Chronic but manageable. Many patients experience improvement with age. Quality of life can be significantly impacted without proper treatment.",
        "prevention": ["Identify and avoid triggers", "Regular sleep schedule", "Stress management", "Regular exercise", "Adequate hydration"],
    },
    "gastroenteritis": {
        "name": "Acute Gastroenteritis",
        "icd10": "K52.9",
        "description": "Inflammation of the stomach and intestines causing diarrhea, vomiting, and abdominal pain. Usually viral and self-limiting.",
        "symptoms": ["Diarrhea", "Nausea and vomiting", "Abdominal cramps", "Low-grade fever", "Dehydration", "Loss of appetite", "Muscle aches"],
        "causes": ["Norovirus", "Rotavirus", "Salmonella", "Campylobacter", "E. coli", "Giardia"],
        "risk_factors": ["Contaminated food/water", "Close contact with infected person", "Poor hygiene", "Travel to endemic areas", "Weakened immune system"],
        "treatment": ["Oral rehydration therapy", "Rest", "BRAT diet (bananas, rice, applesauce, toast)", "Anti-nausea medications", "Antibiotics only for bacterial cases"],
        "when_to_see_doctor": ["Signs of dehydration", "Blood in stool", "Fever above 102°F", "Vomiting lasting more than 2 days", "Severe abdominal pain"],
        "prognosis": "Excellent. Most cases resolve within 3-7 days. Dehydration is the main complication risk.",
        "prevention": ["Frequent handwashing", "Food safety practices", "Safe water sources", "Avoid close contact with infected individuals", "Vaccination (rotavirus for children)"],
    },
    "asthma": {
        "name": "Asthma",
        "icd10": "J45.9",
        "description": "Chronic inflammatory disease of the airways causing recurrent episodes of wheezing, breathlessness, chest tightness, and coughing.",
        "symptoms": ["Wheezing", "Shortness of breath", "Chest tightness", "Coughing (especially at night)", "Difficulty exercising", "Rapid breathing"],
        "causes": ["Airway inflammation", "Bronchial hyperresponsiveness", "Genetic predisposition", "Environmental triggers", "Allergic reactions"],
        "risk_factors": ["Family history of asthma", "Allergies", "Childhood respiratory infections", "Exposure to air pollution", "Obesity", "Smoking"],
        "treatment": ["Quick-relief inhalers (albuterol)", "Inhaled corticosteroids", "Long-acting bronchodilators", "Leukotriene modifiers", "Allergy medications"],
        "when_to_see_doctor": ["Frequent asthma attacks", "Using rescue inhaler more than twice weekly", "Wheezing that doesn't improve", "Difficulty speaking due to breathlessness", "Peak flow readings consistently low"],
        "prognosis": "Good with proper management. Many children outgrow symptoms. Adults typically have lifelong condition requiring ongoing management.",
        "prevention": ["Avoid known triggers", "Use preventive medications as prescribed", "Regular monitoring", "Create an asthma action plan", "Annual flu vaccination"],
    },
    "hypertension": {
        "name": "Hypertension (High Blood Pressure)",
        "icd10": "I10",
        "description": "Chronic condition where blood pressure in the arteries is persistently elevated, increasing risk of cardiovascular disease, stroke, and kidney disease.",
        "symptoms": ["Usually asymptomatic", "Headaches (severe cases)", "Shortness of breath", "Nosebleeds", "Flushing", "Dizziness", "Chest pain"],
        "causes": ["Primary: unknown (90-95%)", "Secondary: kidney disease, hormonal disorders", "Narrowed arteries", "Increased blood volume"],
        "risk_factors": ["Age >60", "Family history", "Obesity", "High sodium diet", "Excessive alcohol", "Sedentary lifestyle", "Stress", "Smoking"],
        "treatment": ["Lifestyle changes (DASH diet, exercise)", "ACE inhibitors", "Calcium channel blockers", "Diuretics", "ARBs", "Beta-blockers"],
        "when_to_see_doctor": ["Blood pressure consistently above 130/80", "Headaches with elevated BP", "Vision changes", "Chest pain", "Blood pressure above 180/120 (emergency)"],
        "prognosis": "Lifelong condition requiring ongoing management. Well-controlled hypertension significantly reduces complication risk.",
        "prevention": ["Healthy diet (low sodium)", "Regular exercise", "Maintain healthy weight", "Limit alcohol", "Don't smoke", "Manage stress", "Regular BP monitoring"],
    },
    "anxiety disorder": {
        "name": "Anxiety Disorder",
        "icd10": "F41.9",
        "description": "Mental health disorder characterized by excessive worry, fear, and physical symptoms that interfere with daily activities.",
        "symptoms": ["Excessive worry", "Restlessness", "Fatigue", "Difficulty concentrating", "Sleep disturbances", "Rapid heartbeat", "Muscle tension", "Trembling"],
        "causes": ["Neurotransmitter imbalances", "Genetic factors", "Environmental stress", "Traumatic experiences", "Medical conditions"],
        "risk_factors": ["Family history", "Traumatic experiences", "Chronic stress", "Other mental health conditions", "Substance use", "Female sex"],
        "treatment": ["Cognitive behavioral therapy", "SSRIs/SNRIs", "Benzodiazepines (short-term)", "Relaxation techniques", "Exercise", "Mindfulness meditation"],
        "when_to_see_doctor": ["Worry interfering with daily life", "Panic attacks", "Physical symptoms without medical cause", "Sleep disturbances", "Avoidance behavior"],
        "prognosis": "Good with treatment. Many people achieve significant improvement with therapy and/or medication. Untreated anxiety can worsen over time.",
        "prevention": ["Stress management", "Regular exercise", "Adequate sleep", "Limit caffeine and alcohol", "Seek help early"],
    },
    "urinary tract infection": {
        "name": "Urinary Tract Infection",
        "icd10": "N39.0",
        "description": "Infection in any part of the urinary system (kidneys, bladder, ureters, urethra). Most commonly affects the lower tract.",
        "symptoms": ["Burning during urination", "Frequent urge to urinate", "Cloudy or strong-smelling urine", "Pelvic pain", "Blood in urine", "Low-grade fever"],
        "causes": ["E. coli (most common)", "Other bacteria entering urinary tract", "Sexual activity", "Anatomical factors", "Catheter use"],
        "risk_factors": ["Female anatomy", "Sexual activity", "Menopause", "Urinary tract abnormalities", "Kidney stones", "Weakened immune system", "Catheter use"],
        "treatment": ["Antibiotics (nitrofurantoin, trimethoprim, ciprofloxacin)", "Increased fluid intake", "Pain relievers", "Cranberry supplements (preventive)"],
        "when_to_see_doctor": ["Symptoms lasting more than 2 days", "Fever or chills", "Back pain (possible kidney infection)", "Blood in urine", "Recurrent infections"],
        "prognosis": "Excellent with prompt antibiotic treatment. Untreated UTIs can progress to kidney infections (pyelonephritis).",
        "prevention": ["Drink plenty of water", "Urinate after intercourse", "Wipe front to back", "Avoid irritating feminine products", "Cranberry products may help"],
    },
}


class DiseaseInfoResponse(BaseModel):
    """Detailed disease information response."""
    name: str
    icd10: str = ""
    description: str = ""
    symptoms: list[str] = Field(default_factory=list)
    causes: list[str] = Field(default_factory=list)
    risk_factors: list[str] = Field(default_factory=list)
    treatment: list[str] = Field(default_factory=list)
    when_to_see_doctor: list[str] = Field(default_factory=list)
    prognosis: str = ""
    prevention: list[str] = Field(default_factory=list)
    found: bool = True


class DiseaseSearchResponse(BaseModel):
    """Search results for diseases."""
    query: str
    results: list[dict] = Field(default_factory=list)
    total: int = 0


@router.get("/disease/{disease_name}", response_model=DiseaseInfoResponse)
async def get_disease_info(disease_name: str):
    """Get detailed information about a specific disease or condition.

    Returns comprehensive medical information including symptoms, causes,
    risk factors, treatment options, prognosis, and prevention strategies.
    """
    name_lower = disease_name.replace("-", " ").replace("_", " ").lower()

    # Direct match
    if name_lower in DISEASE_DATABASE:
        return DISEASE_DATABASE[name_lower]

    # Partial match
    for key, info in DISEASE_DATABASE.items():
        if name_lower in key or key in name_lower:
            return info
        if name_lower in info["name"].lower():
            return info

    # Fallback: use LLM to generate disease info
    try:
        from src.llm.openrouter_client import OpenRouterClient
        import json

        client = OpenRouterClient()
        prompt = f"""Provide detailed medical information about: {disease_name}

Return a JSON object with these exact keys:
{{
  "name": "Disease name",
  "icd10": "ICD-10 code if known",
  "description": "Brief description",
  "symptoms": ["symptom1", "symptom2"],
  "causes": ["cause1", "cause2"],
  "risk_factors": ["risk1", "risk2"],
  "treatment": ["treatment1", "treatment2"],
  "when_to_see_doctor": ["warning1", "warning2"],
  "prognosis": "Outlook and recovery expectations",
  "prevention": ["prevention1", "prevention2"]
}}

Respond with valid JSON only."""

        result = client.generate_json(
            prompt=prompt,
            system_message="You are a medical information assistant. Provide accurate, evidence-based medical information. Respond with valid JSON only.",
            temperature=0.3,
        )

        if "error" not in result:
            result["found"] = True
            return result
    except Exception as e:
        logger.error(f"Disease info lookup failed for '{disease_name}': {e}")

    raise HTTPException(status_code=404, detail=f"Disease '{disease_name}' not found in database")


@router.get("/diseases/search", response_model=DiseaseSearchResponse)
async def search_diseases(q: str):
    """Search for diseases by name or symptoms.

    Returns matching diseases with brief descriptions.
    """
    query_lower = q.lower().strip()
    if not query_lower:
        return DiseaseSearchResponse(query=q, results=[], total=0)

    results = []
    for key, info in DISEASE_DATABASE.items():
        score = 0
        if query_lower in key:
            score += 10
        if query_lower in info["name"].lower():
            score += 10
        if query_lower in info["description"].lower():
            score += 5
        for symptom in info["symptoms"]:
            if query_lower in symptom.lower():
                score += 3
        for cause in info["causes"]:
            if query_lower in cause.lower():
                score += 2

        if score > 0:
            results.append({
                "name": info["name"],
                "icd10": info.get("icd10", ""),
                "description": info["description"][:150] + "...",
                "symptoms": info["symptoms"][:5],
                "relevance_score": score,
            })

    # Sort by relevance
    results.sort(key=lambda x: x["relevance_score"], reverse=True)

    return DiseaseSearchResponse(query=q, results=results[:10], total=len(results))


# ===== Emergency SOS Mode =====

EMERGENCY_KEYWORDS_EN = [
    # Cardiac emergencies
    "chest pain with sweating", "chest pressure radiating", "heart attack", 
    "severe chest pain", "pain radiating to arm", "angina attack",
    # Neurological emergencies
    "stroke symptoms", "sudden weakness", "facial drooping", "slurred speech",
    "sudden severe headache", "thunderclap headache", "loss of consciousness",
    "seizure", "convulsions", "unconscious",
    # Respiratory emergencies
    "can't breathe", "cannot breathe", "severe breathing difficulty",
    "choking", "unable to breathe", "gasping for air",
    # Trauma/bleeding
    "severe bleeding", "uncontrolled bleeding", "major trauma",
    "deep wound bleeding", "coughing up blood", "vomiting blood",
    # Mental health emergencies
    "suicidal", "suicide", "want to die", "self-harm", "overdose",
    # Other emergencies
    "severe allergic reaction", "anaphylaxis", "swollen throat",
    "poisoning", "swallowed poison", "burns all over body",
    "severe abdominal pain", "sudden blindness",
]

EMERGENCY_KEYWORDS_HI = [
    # Hindi emergency keywords
    "सीने में दर्द", "हार्ट अटैक", "दिल का दौरा",
    "ब्रेन स्ट्रोक", "लकवा", "अचानक कमजोरी",
    "सांस नहीं आ रही", "दम घुट रहा है",
    "बहुत ज्यादा खून बह रहा है", "आत्महत्या", "खुदकुशी",
    "बेहोश", "होश नहीं आ रहा", "दौरे पड़ना",
    "एलर्जी", "गला सूजना", "ज़हर", "विष",
]

EMERGENCY_RESPONSE = {
    "is_emergency": True,
    "severity": "critical",
    "alert_level": "immediate",
    "message": "⚠️ MEDICAL EMERGENCY DETECTED",
    "actions": [
        "Call 112 (National Emergency Number) or 108 (Ambulance) immediately",
        "Do not drive yourself to the hospital",
        "If alone, unlock your door and call a neighbor or family member",
        "Keep your phone nearby and stay calm",
        "If chest pain: Sit down, rest, and chew one aspirin (300mg) if available and not allergic",
        "If stroke symptoms: Note the time symptoms started — this is critical for treatment",
        "If severe bleeding: Apply direct pressure with a clean cloth",
        "Do not eat or drink anything until evaluated by a medical professional",
    ],
    "emergency_numbers": {
        "national": "112",
        "ambulance": "108",
        "maternal": "102",
        "police": "100",
    },
    "disclaimer": "This is an automated emergency detection. Always call emergency services immediately for any medical emergency.",
}

NORMAL_RESPONSE = {
    "is_emergency": False,
    "severity": "non-emergency",
    "alert_level": "none",
    "message": "No emergency detected",
    "actions": [],
    "emergency_numbers": {},
    "disclaimer": "If your symptoms worsen or you develop any emergency signs, seek immediate medical care.",
}


class EmergencyCheckRequest(BaseModel):
    """Request for emergency detection."""
    text: str = Field(..., description="Symptom description to check for emergencies")


class EmergencyCheckResponse(BaseModel):
    """Response from emergency detection."""
    is_emergency: bool
    severity: str
    alert_level: str
    message: str
    actions: list[str] = Field(default_factory=list)
    emergency_numbers: dict = Field(default_factory=dict)
    triggered_keywords: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    disclaimer: str = ""


@router.post("/emergency-check", response_model=EmergencyCheckResponse)
async def check_emergency(request: EmergencyCheckRequest):
    """Check if symptoms indicate a medical emergency.
    
    This endpoint uses keyword matching and pattern detection to identify
    potential medical emergencies and returns immediate action guidance.
    """
    text_lower = request.text.lower()
    text_hindi = request.text  # Keep original for Hindi matching
    
    triggered = []
    confidence = 0.0
    
    # Check English emergency keywords
    for keyword in EMERGENCY_KEYWORDS_EN:
        if keyword.lower() in text_lower:
            triggered.append(keyword)
            # Higher confidence for multi-word matches
            confidence = max(confidence, 0.7 if len(keyword.split()) > 2 else 0.5)
    
    # Check Hindi emergency keywords
    for keyword in EMERGENCY_KEYWORDS_HI:
        if keyword in text_hindi:
            triggered.append(f"Hindi: {keyword}")
            confidence = max(confidence, 0.7)
    
    # Pattern-based detection for combinations
    patterns = [
        (["chest", "pain", "sweat"], 0.85),
        (["chest", "pain", "radiating"], 0.85),
        (["chest", "pain", "arm"], 0.80),
        (["chest", "pain", "jaw"], 0.80),
        (["stroke", "symptoms"], 0.90),
        (["sudden", "weakness", "one side"], 0.85),
        (["can't", "breathe"], 0.80),
        (["cannot", "breathe"], 0.80),
        (["severe", "bleeding"], 0.85),
        (["coughing", "blood"], 0.80),
        (["vomiting", "blood"], 0.80),
        (["suicidal", "thoughts"], 0.95),
        (["want", "to", "die"], 0.90),
        (["overdose"], 0.95),
        (["unconscious"], 0.90),
        (["seizure"], 0.85),
        (["severe", "allergic", "reaction"], 0.85),
        (["swollen", "throat"], 0.80),
    ]
    
    for pattern, score in patterns:
        if all(word in text_lower for word in pattern):
            triggered.append(f"Pattern: {' + '.join(pattern)}")
            confidence = max(confidence, score)
    
    # Determine if emergency
    is_emergency = len(triggered) > 0 and confidence >= 0.5
    
    if is_emergency:
        logger.warning(f"EMERGENCY DETECTED (confidence: {confidence:.2f}): {triggered}")
        return EmergencyCheckResponse(
            is_emergency=True,
            severity="critical",
            alert_level="immediate",
            message="⚠️ MEDICAL EMERGENCY DETECTED",
            actions=EMERGENCY_RESPONSE["actions"],
            emergency_numbers=EMERGENCY_RESPONSE["emergency_numbers"],
            triggered_keywords=triggered,
            confidence=confidence,
            disclaimer=EMERGENCY_RESPONSE["disclaimer"],
        )
    else:
        return EmergencyCheckResponse(
            is_emergency=False,
            severity="non-emergency",
            alert_level="none",
            message="No emergency detected",
            actions=[],
            emergency_numbers={},
            triggered_keywords=[],
            confidence=0.0,
            disclaimer=NORMAL_RESPONSE["disclaimer"],
        )
