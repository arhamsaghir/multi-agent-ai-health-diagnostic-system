"""NVIDIA NIM client wrapper for Nemotron 3 RAG synthesis."""

from typing import Optional
import requests
from loguru import logger
from config import settings


class NVIDIAClient:
    """Wrapper for NVIDIA NIM API calls using Nemotron 3."""

    DEFAULT_MODEL = "nvidia/nemotron-3-8b"
    BASE_URL = "https://integrate.api.nvidia.com/v1"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.model = model or settings.rag_model
        self.api_key = api_key or settings.nvidia_api_key
        self.base_url = settings.nvidia_nim_base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        logger.info(f"NVIDIA NIM client initialized — model: {self.model}")

    def generate(self, prompt: str, system_message: str = "",
                 temperature: float = 0.5, max_tokens: int = 1024) -> str:
        """Generate a text response via NVIDIA NIM API.

        Args:
            prompt: User prompt.
            system_message: System-level instructions.
            temperature: Sampling temperature.
            max_tokens: Maximum response length.

        Returns:
            Generated text response.
        """
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except requests.RequestException as e:
            logger.error(f"NVIDIA NIM API error: {e}")
            return f"Error generating response: {str(e)}"

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

        return self.generate(prompt, system_message, temperature=0.3, max_tokens=1500)

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

        return self.generate(prompt, temperature=0.5, max_tokens=1024)

    def is_api_available(self) -> bool:
        """Check if the NVIDIA NIM API is accessible."""
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10,
                },
                timeout=10,
            )
            return response.status_code == 200
        except Exception:
            return False
