"""Diagnosis API routes."""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import os
import tempfile
import asyncio
from loguru import logger

from src.agents.orchestrator.agent import OrchestratorAgent
from src.core.disease_kb import DISEASE_DATABASE
from src.utils.redaction import safe_error

router = APIRouter(prefix="/diagnosis", tags=["diagnosis"])

# Global orchestrator instance (lazy-loaded)
_orchestrator = None


def get_orchestrator() -> OrchestratorAgent:
    """Get or create the orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = OrchestratorAgent()
    return _orchestrator


def _ensure_explanation_flavors(synthesis: dict) -> dict:
    """Fill in any missing explanation flavor so dual-mode UI always has both.

    The Patient/Clinician persona switch renders ``patient_explanation`` and
    ``explanation`` respectively; when the LLM omits one, it is composed from
    the structured diagnosis entries via RuleBasedSynthesizer.
    """
    try:
        from src.agents.rule_based_synthesis import RuleBasedSynthesizer
        return RuleBasedSynthesizer().compose_explanations(synthesis)
    except Exception as e:
        logger.debug(f"Explanation fallback composition skipped: {e}")
        return synthesis


class DiagnosisRequest(BaseModel):
    """Request body for diagnostic analysis.

    Image input is not accepted here: the server-side upload endpoints
    (``/analyze-with-image``, ``/vision/analyze``) own the file path so a
    client can never point the pipeline at an arbitrary filesystem path.
    """
    text: str = Field(..., description="Symptom description in natural language")
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
    session_id: Optional[str] = Field(None, description="Persisted session identifier")
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
    triage: Optional[dict] = Field(None, description="DEMAT entropy and differential probability state")


@router.post("/analyze", response_model=DiagnosisResponse)
async def analyze_symptoms(request: DiagnosisRequest):
    """Run full diagnostic analysis on symptom text.

    This endpoint:
    1. Detects input language and translates to English if needed
    2. Extracts symptoms using the clinical NLP agent
    3. Retrieves relevant medical knowledge (RAG + FAISS)
    4. Assesses disease risk (GradientBoosting / rule-based)
    5. Synthesizes all findings into a diagnostic report (LLM or rule-based)
    6. Translates results back to input language if needed

    Image input is not accepted here; use ``/analyze-with-image`` or
    ``/api/vision/analyze`` so the server owns the file path.
    """
    try:
        return await run_analysis(request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Diagnosis analysis failed: {safe_error(e, request.text)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


async def run_analysis(
    request: DiagnosisRequest,
    progress_cb=None,
    image_path: Optional[str] = None,
) -> DiagnosisResponse:
    """Core analysis pipeline shared by /analyze and /analyze-stream.

    Extracted as a helper so the SSE route can pass a progress callback
    through to the orchestrator without duplicating the endpoint logic.

    ``image_path`` is server-owned (upload endpoints set it); it is never read
    from the client request body.
    """
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
        "image_path": image_path,
        "patient_history": request.patient_history,
    }

    result = await orchestrator.run(input_data, progress_cb=progress_cb)

    # Extract synthesis result
    synthesis = _ensure_explanation_flavors(result.get("synthesis_result", {}))

    # Translate results back to original language if needed
    if original_lang != "en" and original_lang in ["hi", "es", "ar", "fr", "de", "ur", "bn", "ta", "te", "mr", "gu"]:
        from src.llm.translation import TranslationService
        translator = TranslationService()
        synthesis = translator.translate_diagnosis(synthesis, original_lang)
        logger.info(f"Translated diagnosis results to {original_lang}")

    # Persist session and diagnosis to SQLite repository
    session_id = None
    try:
        import uuid
        from src.data.database.repository import DiagnosisRepository

        session_id = str(uuid.uuid4())
        repo = DiagnosisRepository()
        symptoms = result.get("symptoms", [])
        repo.save_session(
            session_id=session_id,
            user_input=request.text,
            symptoms=symptoms,
            patient_history=request.patient_history,
            image_path=image_path,
        )

        # Persist individual detected conditions
        diagnoses_list = synthesis.get("diagnosis", [])
        if not diagnoses_list and symptoms:
            primary_condition = synthesis.get("primary_condition") or (
                symptoms[0] if isinstance(symptoms[0], str) else "Reported Symptoms Assessment"
            )
            diagnoses_list = [{
                "condition": primary_condition,
                "confidence": float(synthesis.get("confidence", {}).get("overall_confidence", 0.6) if isinstance(synthesis.get("confidence"), dict) else 0.6),
                "severity": synthesis.get("severity") or "moderate",
            }]

        for diag in diagnoses_list:
            condition_name = diag.get("name") or diag.get("condition") or "Undetermined"
            conf = float(diag.get("confidence") or 0.0)
            sev = str(diag.get("severity") or synthesis.get("severity") or "low")
            repo.save_diagnosis(session_id, condition=condition_name, confidence=conf, severity=sev)

        if request.patient_history:
            repo.save_patient_record(session_id, request.patient_history)

        logger.info(f"Persisted diagnostic session: {session_id}")
    except Exception as db_err:
        logger.warning(f"Could not persist diagnosis session to database: {db_err}")

    triage_data = None
    try:
        from src.core.demat import demat_engine
        t_session = demat_engine.start_or_get_session(session_id, request.text, request.patient_history)
        triage_data = t_session.to_dict()
    except Exception as e:
        logger.debug(f"DEMAT session initialization skipped: {e}")

    return DiagnosisResponse(
        session_id=session_id,
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
        triage=triage_data,
    )


class FollowUpRequest(BaseModel):
    """Request for generating follow-up questions."""
    text: str = Field(..., description="Initial symptom description")
    patient_history: Optional[dict] = Field(None, description="Patient demographics and history")
    previous_questions: Optional[list[dict]] = Field(None, description="Previously asked questions and answers")
    session_id: Optional[str] = Field(None, description="Active triage session identifier")


class FollowUpResponse(BaseModel):
    """Response containing follow-up questions."""
    questions: list[dict] = Field(default_factory=list, description="List of clarifying questions")
    has_more: bool = False
    session_id: str = ""
    triage: Optional[dict] = Field(None, description="DEMAT entropy and differential probability state")


@router.post("/follow-up", response_model=FollowUpResponse)
async def generate_follow_up(request: FollowUpRequest):
    """Generate clarifying follow-up questions to refine diagnosis using DEMAT.

    Information-theoretic active triage:
    1. Computes Shannon diagnostic entropy H(D) across differential candidates
    2. Dynamically evaluates Expected Mutual Information I(D; Q)
    3. Selects inquiries with maximum entropy reduction potential
    4. Halts when diagnostic entropy satisfies clinical convergence criteria
    """
    import uuid
    try:
        from src.core.demat import demat_engine

        session = demat_engine.start_or_get_session(
            session_id=request.session_id,
            text=request.text,
            patient_history=request.patient_history,
        )

        # Apply previous questions/answers to update posterior belief
        if request.previous_questions:
            for qa in request.previous_questions:
                qid = qa.get("id") or qa.get("question_id")
                chosen_ans = qa.get("answer")
                if qid and chosen_ans and qid not in session.answered_question_ids:
                    session.belief, session.entropy = demat_engine.update_belief_from_answer(
                        session.belief, qid, chosen_ans
                    )
                    session.answered_question_ids.append(qid)

        # Convergence check: entropy below clinical threshold or max rounds reached
        if session.entropy <= demat_engine.ENTROPY_STOPPING_THRESHOLD or session.round_count >= demat_engine.MAX_TRIAGE_ROUNDS:
            session.converged = True
            return FollowUpResponse(
                questions=[],
                has_more=False,
                session_id=session.session_id,
                triage=session.to_dict(),
            )

        # Select next questions that maximize Expected Mutual Information
        selected_candidates = demat_engine.select_next_questions(
            current_belief=session.belief,
            excluded_ids=session.asked_question_ids,
            k=2,
        )

        # If marginal information gain is below threshold, converge early
        if not selected_candidates or selected_candidates[0].get("expected_information_gain", 0) < demat_engine.MIN_INFO_GAIN_THRESHOLD:
            session.converged = True
            return FollowUpResponse(
                questions=[],
                has_more=False,
                session_id=session.session_id,
                triage=session.to_dict(),
            )

        session.round_count += 1
        formatted_questions = []
        for q in selected_candidates:
            session.asked_question_ids.append(q["id"])
            ig = q.get("expected_information_gain", 0.0)
            formatted_questions.append({
                "id": q["id"],
                "question": q["question"],
                "type": q["type"],
                "options": q.get("options", []),
                "category": q.get("category", "general"),
                "rationale": f"{q.get('rationale', '')} (Expected information gain: {round(ig, 3)} bits)",
                "expected_information_gain": ig,
            })

        has_more = (not session.converged) and (session.round_count < demat_engine.MAX_TRIAGE_ROUNDS)

        return FollowUpResponse(
            questions=formatted_questions,
            has_more=has_more,
            session_id=session.session_id,
            triage=session.to_dict(),
        )
    except Exception as e:
        logger.error(f"DEMAT follow-up question generation failed: {e}")
        # Graceful fallback to rule-based questions
        fallback_q = _generate_rule_based_questions(request.text)
        return FollowUpResponse(
            questions=fallback_q[:2],
            has_more=False,
            session_id=request.session_id or str(uuid.uuid4()),
            triage=None,
        )


class RefineDiagnosisRequest(BaseModel):
    """Request to refine diagnosis with follow-up answers."""
    text: str = Field(..., description="Initial symptom description")
    patient_history: Optional[dict] = Field(None, description="Patient demographics and history")
    follow_up_answers: list[dict] = Field(default_factory=list, description="Answers to follow-up questions")
    session_id: Optional[str] = Field(None, description="Active triage session identifier")


@router.post("/refine", response_model=DiagnosisResponse)
async def refine_diagnosis(request: RefineDiagnosisRequest):
    """Re-run diagnosis incorporating follow-up question answers and DEMAT posterior."""
    try:
        return await run_refinement(request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Diagnosis refinement failed: {e}")
        raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")


async def run_refinement(request: RefineDiagnosisRequest, progress_cb=None) -> DiagnosisResponse:
    """Core refinement pipeline shared by /refine and /refine-stream."""
    import uuid
    from src.core.demat import demat_engine
    orchestrator = get_orchestrator()

    # Update DEMAT session belief if active session provided
    triage_dict = None
    if request.session_id:
        session = demat_engine.get_session(request.session_id)
        if session and request.follow_up_answers:
            for qa in request.follow_up_answers:
                qid = qa.get("id") or qa.get("question_id")
                ans = qa.get("answer")
                if qid and ans:
                    session.belief, session.entropy = demat_engine.update_belief_from_answer(
                        session.belief, qid, ans
                    )
                    if qid not in session.asked_question_ids:
                        session.asked_question_ids.append(qid)
            session.converged = True
            triage_dict = session.to_dict()

    if progress_cb is not None and triage_dict:
        top = triage_dict.get("top_candidates", [])
        top_label = f"top: {top[0]['name']} {round(top[0]['probability'] * 100)}%" if top else "converged"
        progress_cb({
            "type": "agent",
            "node": "triage",
            "agent": "DEMAT Active Triage",
            "model": "Entropy Minimization",
            "status": "completed",
            "elapsed_ms": 0,
            "summary": f"entropy {triage_dict.get('entropy_bits', '?')} bits · {top_label}",
        })

    # Enrich context with answers
    enriched_text = request.text
    if request.follow_up_answers:
        enriched_text += "\n\nAdditional clinical details from triage follow-up:\n"
        for qa in request.follow_up_answers:
            enriched_text += f"- {qa.get('question', '')}: {qa.get('answer', '')}\n"

    if triage_dict and triage_dict.get("top_candidates"):
        cands_str = ", ".join([f"{c['name']} ({round(c['probability']*100, 1)}%)" for c in triage_dict["top_candidates"][:3]])
        enriched_text += f"\nActive Triage Mathematical Prior: {cands_str} (Entropy: {triage_dict.get('entropy_bits')} bits)\n"

    input_data = {
        "text": enriched_text,
        "patient_history": request.patient_history,
    }

    result = await orchestrator.run(input_data, progress_cb=progress_cb)
    synthesis = _ensure_explanation_flavors(result.get("synthesis_result", {}))

    return DiagnosisResponse(
        session_id=request.session_id or str(uuid.uuid4()),
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
        triage=triage_dict,
    )


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
        synthesis = _ensure_explanation_flavors(result.get("synthesis_result", {}))

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
        logger.error(f"Analysis with image failed: {safe_error(e, text)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    finally:
        # Clean up temp image
        if image_path and os.path.exists(image_path):
            try:
                os.unlink(image_path)
            except Exception:
                pass




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
