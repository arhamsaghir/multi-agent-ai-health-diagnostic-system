"""OpenRouter client wrapper — multi-model, multi-role LLM access via single free API key."""

from typing import Optional
import openai
import json
from loguru import logger
from config import settings


class OpenRouterClient:
    """Unified LLM client for OpenRouter — handles all model roles (chat, synthesis, RAG).

    OpenRouter supports the same chat completions API as OpenAI, so we
    reuse the OpenAI SDK with a custom base_url pointing to OpenRouter.

    Uses free models by default:
    - Chat: gpt-oss-120b (117B MoE from OpenAI, free)
    - Synthesis: nemotron-3-super-120b (120B MoE from NVIDIA, free)
    - RAG: nemotron-3-super-120b (same model, specialized prompt)
    """

    # Active free models on OpenRouter
    CHAT_MODEL = "nvidia/nemotron-3.5-lightning:free"
    SYNTHESIS_MODEL = "nvidia/nemotron-3.5-lightning:free"
    RAG_MODEL = "nvidia/nemotron-3.5-lightning:free"

    def __init__(self, api_key: Optional[str] = None):
        if getattr(settings, "use_omniroute", False) and getattr(settings, "omniroute_base_url", ""):
            self.base_url = settings.omniroute_base_url
            self.api_key = api_key or settings.omniroute_api_key or "omniroute-local"
            self.default_model = settings.omniroute_model or "antigravity/gemini-3.8-flash-high"
            self.CHAT_MODEL = self.default_model
            self.SYNTHESIS_MODEL = self.default_model
            self.RAG_MODEL = self.default_model
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )
            logger.info(f"OpenRouter/OmniRoute client initialized via {self.base_url} — default: {self.default_model}")
        else:
            self.client = openai.OpenAI(
                api_key=api_key or settings.openrouter_api_key,
                base_url=settings.openrouter_base_url,
            )
            self.default_model = settings.chatbot_model or self.CHAT_MODEL
            logger.info(f"OpenRouter client initialized — default: {self.default_model}")

    def generate(self, prompt: str, system_message: str = "",
                 temperature: float = 0.5, max_tokens: int = 1024,
                 model: Optional[str] = None, timeout: int = 30) -> str:
        """Generate a text response via OpenRouter API.

        Args:
            prompt: User prompt.
            system_message: System-level instructions.
            temperature: Sampling temperature.
            max_tokens: Maximum response length.
            model: Override default model (e.g., synthesis_model, rag_model).
            timeout: Request timeout in seconds (default 30s).

        Returns:
            Generated text response.
        """
        target_model = model or self.default_model
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        # Candidate models to try in sequence if OmniRoute is enabled
        models_to_try = [target_model]
        if getattr(settings, "use_omniroute", False):
            fallback_candidates = [
                "antigravity/gemini-3.8-flash-medium",
                "agy/gemini-3.8-flash",
                "auto/best-fast",
                "auto/best-chat"
            ]
            for cand in fallback_candidates:
                if cand not in models_to_try:
                    models_to_try.append(cand)

        last_error = None
        for m in models_to_try:
            try:
                response = self.client.chat.completions.create(
                    model=m,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=timeout,
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                last_error = e
                logger.warning(f"Model {m} failed ({e}), attempting next candidate if available...")
                continue

        logger.error(f"All model candidates failed. Last error: {last_error}")
        return f"Error generating response: {str(last_error)}"

    def generate_json(self, prompt: str, system_message: str = "Respond with valid JSON only.",
                      temperature: float = 0.3, model: Optional[str] = None) -> dict:
        """Generate a structured JSON response.

        Args:
            prompt: User prompt requesting structured output.
            system_message: System instructions emphasizing JSON format.
            temperature: Lower temperature for more deterministic output.
            model: Override default model.

        Returns:
            Parsed JSON as a dictionary.
        """
        system_message += "\n\nIMPORTANT: Respond with valid JSON only. No markdown, no explanations."

        target_model = model or self.default_model
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ]

        try:
            response = self.client.chat.completions.create(
                model=target_model,
                messages=messages,
                temperature=temperature,
                max_tokens=2048,
                timeout=30,
            )
            content = response.choices[0].message.content.strip()
            # Strip markdown code blocks if present
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return {"error": "Invalid JSON response", "raw": content}
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            return {"error": str(e)}

    # ===== Role-specific methods =====

    def chat(self, message: str, system_message: str = "You are a helpful medical AI assistant.",
             temperature: float = 0.7) -> str:
        """Chat endpoint — uses gpt-oss-120b for conversational responses."""
        return self.generate(
            prompt=message,
            system_message=system_message,
            temperature=temperature,
            max_tokens=512,
            model=self.CHAT_MODEL,
            timeout=30,
        )

    def synthesize_report(self, agent_outputs: dict, patient_context: str = "") -> dict:
        """Generate a structured diagnostic report from agent outputs using Nemotron 3 Super.

        Args:
            agent_outputs: Dict with outputs from NLP, Vision, RAG, Prediction agents.
            patient_context: Patient demographics and history.

        Returns:
            Dict with diagnosis list, explanation, recommendations, severity, doctor_alert.
        """
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
  "differential_diagnoses": ["alternative condition 1", "alternative condition 2"],
  "red_flags": ["warning sign 1", "warning sign 2"],
  "disclaimer": "Always include: This is an AI-generated assessment and not a substitute for professional medical advice."
}}

IMPORTANT:
- Be conservative in severity assessments
- Always recommend professional consultation for moderate+ severity
- Base confidence on agreement between agents
- Include red flags that warrant immediate attention
- Respond with valid JSON only."""

        system_message = """You are a cautious medical AI assistant. Your role is to:
1. Synthesize findings from multiple diagnostic agents
2. Provide informative but conservative assessments
3. ALWAYS include the disclaimer that this is not a substitute for professional medical advice
4. When in doubt, recommend seeing a doctor

Respond with valid JSON only. No markdown, no explanations outside the JSON."""

        target_model = settings.omniroute_model if getattr(settings, "use_omniroute", False) else self.SYNTHESIS_MODEL
        raw_response = self.generate(
            prompt=prompt,
            system_message=system_message,
            temperature=0.3,
            max_tokens=3000,
            model=target_model,
            timeout=30,
        )

        # Parse JSON from response
        try:
            if "```" in raw_response:
                json_str = raw_response.split("```")[1]
                if json_str.startswith("json"):
                    json_str = json_str[4:]
                return json.loads(json_str.strip())
            return json.loads(raw_response)
        except (json.JSONDecodeError, TypeError, IndexError) as e:
            logger.error(f"Failed to parse synthesis report JSON: {e}")
            logger.warning("Falling back to RuleBasedSynthesizer for diagnostic report")
            from src.agents.rule_based_synthesis import RuleBasedSynthesizer
            synthesizer = RuleBasedSynthesizer()
            return synthesizer.generate_report(agent_outputs, patient_context)

    def synthesize_knowledge(self, query: str, retrieved_docs: list[dict]) -> str:
        """Synthesize retrieved medical documents into a coherent knowledge summary.

        Args:
            query: The patient's symptom query.
            retrieved_docs: List of docs with 'content', 'source', 'score'.

        Returns:
            Synthesized medical knowledge summary.
        """
        docs_text = "\n\n".join([
            f"Source: {d.get('source', 'Unknown')}\n{d['content']}"
            for d in retrieved_docs[:5]
        ])

        prompt = f"""Based on the patient's symptoms and the retrieved medical literature, synthesize a concise knowledge summary.

PATIENT QUERY: {query}

RETRIEVED MEDICAL LITERATURE:
{docs_text}

Provide:
1. A brief summary of the most relevant conditions
2. Key clinical guidelines that apply
3. Important differential diagnoses to consider
4. Red flag symptoms that warrant immediate attention

Keep the response concise (3-5 paragraphs)."""

        system_message = """You are a medical knowledge synthesis assistant.
Your role is to summarize retrieved clinical guidelines and medical literature
in the context of a patient's symptoms.
Be factual, cite sources, and avoid making diagnoses."""

        target_model = settings.omniroute_model if getattr(settings, "use_omniroute", False) else self.RAG_MODEL
        return self.generate(
            prompt=prompt,
            system_message=system_message,
            temperature=0.3,
            max_tokens=1500,
            model=target_model,
            timeout=30,
        )

    def explain_to_patient(self, diagnosis: dict, language: str = "simple") -> str:
        """Translate medical findings into patient-friendly language.

        Args:
            diagnosis: The structured diagnosis dict.
            language: "simple" for layperson, "moderate" for health-literate.

        Returns:
            Plain-language explanation.
        """
        conditions = ", ".join([d["condition"] for d in diagnosis.get("diagnosis", [])])
        prompt = f"""Explain the following medical diagnosis in {language} language that a patient can understand:

Conditions: {conditions}
Findings: {diagnosis.get("explanation", "No detailed findings")}

Write a clear, reassuring but honest explanation. Avoid medical jargon.
Include what the patient should do next."""

        return self.generate(
            prompt=prompt,
            system_message="You are a patient-friendly medical communicator. Use simple language.",
            temperature=0.5,
            max_tokens=1024,
            model=self.CHAT_MODEL,
            timeout=30,
        )

    def classify(self, text: str, categories: list[str],
                 system_context: str = "") -> dict:
        """Classify text into categories with confidence scores.

        Args:
            text: Text to classify.
            categories: List of possible category names.
            system_context: Additional context for classification.

        Returns:
            Dict with category -> confidence scores.
        """
        prompt = f"""Classify the following text into one or more of these categories: {', '.join(categories)}.

Text: "{text}"

Return a JSON object with each category name as a key and a confidence score (0.0 to 1.0) as the value.
Only include categories that have a confidence > 0.1."""

        system_message = f"You are a medical classification expert. {system_context} Respond with valid JSON only."

        return self.generate_json(prompt, system_message, temperature=0.2, model=self.CHAT_MODEL)

    def reason(self, question: str, context: str = "",
               steps: int = 3) -> str:
        """Generate step-by-step reasoning for a medical question.

        Args:
            question: The medical question to reason about.
            context: Available context (symptoms, test results, etc.).
            steps: Number of reasoning steps to generate.

        Returns:
            Step-by-step reasoning text.
        """
        prompt = f"""Analyze the following medical scenario using {steps} clear reasoning steps.

Context: {context}
Question: {question}

Provide your reasoning in exactly {steps} steps, then give your conclusion.
Format: Step 1: ..., Step 2: ..., Conclusion: ..."""

        system_message = """You are a medical reasoning assistant. Think through problems methodically.
Be cautious — do not make definitive diagnoses. Always recommend professional medical consultation."""

        return self.generate(
            prompt=prompt,
            system_message=system_message,
            temperature=0.5,
            max_tokens=1024,
            model=self.SYNTHESIS_MODEL,
            timeout=30,
        )

    def answer_medical_question(self, question: str, context: str = "") -> str:
        """Answer a specific medical question using context.

        Args:
            question: The medical question.
            context: Relevant context (symptoms, test results).

        Returns:
            Answer to the medical question.
        """
        prompt = f"""Answer the following medical question based on the provided context.

CONTEXT: {context}
QUESTION: {question}

Provide a clear, evidence-based answer. If you're uncertain, say so.
Always recommend consulting a healthcare professional for definitive answers."""

        return self.generate(
            prompt=prompt,
            temperature=0.5,
            max_tokens=1024,
            model=self.RAG_MODEL,
            timeout=30,
        )

    def is_api_available(self, model: Optional[str] = None) -> bool:
        """Check if the OpenRouter API is accessible."""
        target_model = model or self.default_model
        try:
            response = self.client.chat.completions.create(
                model=target_model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10,
                timeout=10,
            )
            return response is not None
        except Exception:
            return False
