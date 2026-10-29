"""Gemini client wrapper with automatic OpenRouter fallback."""

from typing import Optional
import google.generativeai as genai
from loguru import logger
from config import settings


class GeminiClient:
    """Wrapper for Google Gemini API calls with OpenRouter fallback.

    Attempts to use Gemini first; if unavailable (quota exceeded, model not found,
    etc.), falls back to OpenRouter using the same methods.
    """

    DEFAULT_MODEL = "gemini-2.0-flash"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.model = model or settings.synthesis_model
        self.api_key = api_key or settings.google_api_key
        self.gemini_available = True
        self._openrouter_client = None
        self._init_gemini()

    def _init_gemini(self):
        """Initialize Gemini client; mark unavailable if it fails."""
        if not self.api_key:
            self.gemini_available = False
            logger.warning("No Google API key — Gemini unavailable, will use OpenRouter fallback")
            return

        # If model name looks like an OpenRouter identifier, skip Gemini entirely
        if ":" in self.model or self.model.startswith(("openai/", "nvidia/", "meta-llama/", "anthropic/", "google/")):
            self.gemini_available = False
            logger.warning(f"Model '{self.model}' is an OpenRouter model — Gemini skipped, will use OpenRouter fallback")
            return

        try:
            genai.configure(api_key=self.api_key)
            self.model_instance = genai.GenerativeModel(self.model)
            logger.info(f"Gemini client initialized — model: {self.model}")
        except Exception as e:
            self.gemini_available = False
            logger.warning(f"Gemini unavailable ({e}), will use OpenRouter fallback")

    def _get_openrouter(self):
        """Lazy-load OpenRouter fallback client."""
        if self._openrouter_client is None:
            from src.llm.openrouter_client import OpenRouterClient
            self._openrouter_client = OpenRouterClient()
        return self._openrouter_client

    def generate(self, prompt: str, system_message: str = "",
                 temperature: float = 0.7, max_tokens: int = 2048) -> str:
        """Generate a text response from Gemini (falls back to OpenRouter).

        Args:
            prompt: User prompt.
            system_message: System instructions (prepended to prompt).
            temperature: Sampling temperature.
            max_tokens: Maximum response length.

        Returns:
            Generated text response.
        """
        if not self.gemini_available:
            logger.debug("Gemini unavailable — using OpenRouter fallback")
            return self._get_openrouter().generate(
                prompt=prompt,
                system_message=system_message,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        try:
            full_prompt = prompt
            if system_message:
                full_prompt = f"{system_message}\n\n---\n\n{prompt}"

            response = self.model_instance.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
            )

            # Check if response is valid (not blocked)
            if response.candidates and response.candidates[0].finish_reason.name not in ("STOP", "RECITATION"):
                finish_reason = response.candidates[0].finish_reason.name
                logger.warning(f"Gemini finished with: {finish_reason}")

            return response.text.strip()
        except Exception as e:
            logger.warning(f"Gemini API failed ({e}), falling back to OpenRouter")
            self.gemini_available = False
            return self._get_openrouter().generate(
                prompt=prompt,
                system_message=system_message,
                temperature=temperature,
                max_tokens=max_tokens,
            )

    def generate_report(self, agent_outputs: dict, patient_context: str = "") -> dict:
        """Generate a structured diagnostic report from agent outputs.

        Args:
            agent_outputs: Dict with outputs from NLP, Vision, RAG, Prediction agents.
            patient_context: Patient demographics and history.

        Returns:
            Dict with diagnosis list, explanation, recommendations, severity, doctor_alert.
        """
        if not self.gemini_available:
            logger.debug("Gemini unavailable — using OpenRouter for report synthesis")
            return self._get_openrouter().synthesize_report(agent_outputs, patient_context)

        import json

        nlp = agent_outputs.get("nlp", {})
        vision = agent_outputs.get("vision", {})
        rag = agent_outputs.get("rag", {})
        prediction = agent_outputs.get("prediction", {})

        prompt = f"""You are an AI medical diagnostician. Analyze the following agent outputs and produce a structured diagnostic report.

PATIENT CONTEXT:
{patient_context or "No patient history provided"}

SYMPTOM ANALYSIS (NLP Agent):
{json.dumps(nlp, indent=2)}

IMAGE FINDINGS (Vision Agent):
{json.dumps(vision, indent=2)}

MEDICAL KNOWLEDGE (RAG Agent):
{rag.get("knowledge", "No medical knowledge retrieved")}

RISK ASSESSMENT (Prediction Agent):
{json.dumps(prediction, indent=2)}

Produce a JSON response with this exact structure:
{{
  "diagnosis": [
    {{"condition": "name", "confidence": 0.0-1.0, "rationale": "brief explanation", "icd10_code": "optional code"}}
  ],
  "explanation": "Plain-language explanation of findings for the patient",
  "recommendations": ["actionable recommendation 1", "recommendation 2", "recommendation 3"],
  "severity": "critical|high|moderate|low",
  "doctor_alert": true/false,
  "escalation": {{"level": "none|caution|urgent|emergency", "findings": [{{"flag_id": "id", "tier": "emergency|urgent|caution|informational", "reason": "why", "evidence": "the triggering text"}}], "rationale": "why this level", "actions": ["action-first steps"]}},
  "differential_diagnoses": ["alternative condition 1", "alternative condition 2"],
  "red_flags": ["warning sign 1", "warning sign 2"],
  "disclaimer": "Always include: This is an AI-generated assessment and not a substitute for professional medical advice."
}}

IMPORTANT:
- Be conservative in severity assessments
- Always recommend professional consultation for moderate+ severity
- Base confidence on agreement between agents
- Include red flags that warrant immediate attention
- The "escalation" object is optional; if you include one it may only RAISE
  the level determined by the deterministic red-flag engine — the engine's
  level is a floor that synthesis enforces in code
- Respond with valid JSON only."""

        system_message = """You are a cautious medical AI assistant. Your role is to:
1. Synthesize findings from multiple diagnostic agents
2. Provide informative but conservative assessments
3. ALWAYS include the disclaimer that this is not a substitute for professional medical advice
4. When in doubt, recommend seeing a doctor

Respond with valid JSON only. No markdown, no explanations outside the JSON."""

        raw_response = self.generate(prompt, system_message, temperature=0.3, max_tokens=3000)

        # Parse JSON from response
        try:
            if isinstance(raw_response, dict) and "error" in raw_response:
                # OpenRouter fallback returned an error — use rule-based fallback
                logger.warning("LLM synthesis failed — using rule-based report generator")
                return self._rule_based_report(agent_outputs, patient_context)

            if "```" in raw_response:
                json_str = raw_response.split("```")[1]
                if json_str.startswith("json"):
                    json_str = json_str[4:]
                return json.loads(json_str.strip())
            return json.loads(raw_response)
        except (json.JSONDecodeError, TypeError, IndexError) as e:
            logger.error(f"Failed to parse report JSON: {e}")
            logger.warning("Using rule-based report generator as fallback")
            return self._rule_based_report(agent_outputs, patient_context)

    def _rule_based_report(self, agent_outputs: dict, patient_context: str = "") -> dict:
        """Generate report using rule-based logic when LLM synthesis fails."""
        from src.agents.rule_based_synthesis import RuleBasedSynthesizer
        synthesizer = RuleBasedSynthesizer()
        return synthesizer.generate_report(agent_outputs, patient_context)

    def _default_report(self, raw_text: str = "") -> dict:
        """Return a safe default report structure."""
        return {
            "diagnosis": [],
            "explanation": raw_text[:500] if raw_text else "",
            "recommendations": ["Consult a healthcare professional"],
            "severity": "unknown",
            "doctor_alert": False,
            "differential_diagnoses": [],
            "red_flags": [],
            "disclaimer": "This is an AI-generated assessment and not a substitute for professional medical advice.",
        }

    def explain_to_patient(self, diagnosis: dict, language: str = "simple") -> str:
        """Translate medical findings into patient-friendly language.

        Args:
            diagnosis: The structured diagnosis dict.
            language: "simple" for layperson, "moderate" for health-literate.

        Returns:
            Plain-language explanation.
        """
        if not self.gemini_available:
            return self._get_openrouter().explain_to_patient(diagnosis, language)

        conditions = ", ".join([d["condition"] for d in diagnosis.get("diagnosis", [])])
        prompt = f"""Explain the following medical diagnosis in {language} language that a patient can understand:

Conditions: {conditions}
Findings: {diagnosis.get("explanation", "No detailed findings")}

Write a clear, reassuring but honest explanation. Avoid medical jargon.
Include what the patient should do next."""

        return self.generate(prompt, temperature=0.5, max_tokens=1024)
