"""OpenAI client wrapper with automatic OpenRouter fallback."""

from typing import Optional
import openai
import json
from loguru import logger
from config import settings


class OpenAIClient:
    """Wrapper for OpenAI API calls with OpenRouter fallback.

    Attempts to use OpenAI first; if unavailable (quota exceeded, invalid key, etc.),
    falls back to OpenRouter using free models.
    """

    DEFAULT_MODEL = "gpt-4o-mini"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.model = model or settings.orchestrator_model
        self.api_key = api_key or settings.openai_api_key
        self.openai_available = True
        self._openrouter_client = None
        self._init_openai()

    def _init_openai(self):
        """Initialize OpenAI client; mark unavailable if it fails."""
        if not self.api_key:
            self.openai_available = False
            logger.warning("No OpenAI API key — will use OpenRouter fallback")
            return

        # If model name looks like an OpenRouter identifier (contains colon or provider prefix), skip OpenAI
        if ":" in self.model or "/" in self.model:
            self.openai_available = False
            logger.warning(f"Model '{self.model}' is an OpenRouter model — OpenAI skipped, will use OpenRouter fallback")
            return

        try:
            self.client = openai.OpenAI(api_key=self.api_key)
            logger.info(f"OpenAI client initialized — model: {self.model}")
        except Exception as e:
            self.openai_available = False
            logger.warning(f"OpenAI unavailable ({e}), will use OpenRouter fallback")

    def _get_openrouter(self):
        """Lazy-load OpenRouter fallback client."""
        if self._openrouter_client is None:
            from src.llm.openrouter_client import OpenRouterClient
            self._openrouter_client = OpenRouterClient()
        return self._openrouter_client

    def generate(self, prompt: str, system_message: str = "You are a helpful medical AI assistant.",
                 temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """Generate a text response from the LLM (falls back to OpenRouter).

        Args:
            prompt: User prompt / question.
            system_message: System-level instructions.
            temperature: Sampling temperature (0-1).
            max_tokens: Maximum response length.

        Returns:
            Generated text response.
        """
        if not self.openai_available:
            logger.debug("OpenAI unavailable — using OpenRouter fallback")
            return self._get_openrouter().generate(
                prompt=prompt,
                system_message=system_message,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            error_str = str(e)
            # Check for quota/usage errors or invalid model (OpenRouter model used against OpenAI API)
            if ("quota" in error_str.lower() or "insufficient" in error_str.lower()
                    or "rate" in error_str.lower() or "invalid model" in error_str.lower()):
                logger.warning(f"OpenAI unavailable ({e}), falling back to OpenRouter")
                self.openai_available = False
                return self._get_openrouter().generate(
                    prompt=prompt,
                    system_message=system_message,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            logger.error(f"OpenAI API error: {e}")
            return f"Error generating response: {str(e)}"

    def generate_json(self, prompt: str, system_message: str = "Respond with valid JSON only.",
                      temperature: float = 0.3) -> dict:
        """Generate a structured JSON response (falls back to OpenRouter).

        Args:
            prompt: User prompt requesting structured output.
            system_message: System instructions emphasizing JSON format.
            temperature: Lower temperature for more deterministic output.

        Returns:
            Parsed JSON as a dictionary.
        """
        if not self.openai_available:
            return self._get_openrouter().generate_json(prompt, system_message, temperature)

        system_message += "\n\nIMPORTANT: Respond with valid JSON only. No markdown, no explanations."

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=2048,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content.strip()
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return {"error": "Invalid JSON response", "raw": content}
        except Exception as e:
            error_str = str(e)
            if "quota" in error_str.lower() or "insufficient" in error_str.lower():
                logger.warning(f"OpenAI quota exceeded, falling back to OpenRouter for JSON")
                self.openai_available = False
                return self._get_openrouter().generate_json(prompt, system_message, temperature)
            logger.error(f"OpenAI API error: {e}")
            return {"error": str(e)}

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

        return self.generate_json(prompt, system_message, temperature=0.2)

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

        return self.generate(prompt, system_message, temperature=0.5)
