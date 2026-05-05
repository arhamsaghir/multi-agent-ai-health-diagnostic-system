"""Voice Agent — Speech-to-text transcription using Whisper.

Converts spoken symptom descriptions into text for NLP processing.
Supports multiple languages and medical terminology.
Uses OpenAI Whisper API for fast, accurate transcription.
"""

from typing import Any, Optional
import os
from loguru import logger

from src.agents.base import BaseAgent
from config import settings


class VoiceAgent(BaseAgent):
    """Voice-to-text agent using OpenAI Whisper API."""

    name = "voice_agent"
    description = "Whisper / ASR — Speech-to-text for symptom input"

    def __init__(self):
        super().__init__()
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initialize OpenAI client for Whisper API."""
        try:
            from openai import OpenAI
            api_key = settings.openai_api_key or os.environ.get("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
                self.log("info", "OpenAI Whisper API client initialized")
            else:
                self.log("warning", "No OpenAI API key found — voice transcription unavailable")
        except Exception as e:
            self.log("warning", f"Failed to initialize Whisper client: {e}")
            self.client = None

    async def run(self, input_data: dict) -> dict:
        """Transcribe audio to text.

        Args:
            input_data: Dict with 'audio_path' (file path) or 'audio_bytes'.

        Returns:
            Dict with transcribed text, language, and confidence.
        """
        audio_path = input_data.get("audio_path")
        audio_bytes = input_data.get("audio_bytes")

        if not audio_path and not audio_bytes:
            return {"error": "No audio input provided", "transcript": ""}

        if not self.client:
            return {
                "error": "OpenAI API key not configured. Set OPENAI_API_KEY in .env",
                "transcript": "",
                "hint": "Add your OpenAI API key to use voice transcription",
            }

        try:
            # If we have audio bytes, save to temp file first
            temp_file = None
            if audio_bytes and not audio_path:
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                temp_file.write(audio_bytes)
                temp_file.close()
                audio_path = temp_file.name

            if not audio_path or not os.path.exists(audio_path):
                return {"error": "Audio file not found", "transcript": ""}

            # Transcribe using OpenAI Whisper API
            with open(audio_path, "rb") as f:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    language="en",
                    response_format="verbose_json",
                )

            # Clean up temp file
            if temp_file:
                os.unlink(temp_file.name)

            return {
                "transcript": transcript.text.strip(),
                "language": transcript.language if hasattr(transcript, "language") else "en",
                "confidence": round(sum(seg.get("avg_logprob", 0) for seg in getattr(transcript, "segments", [])) / max(len(getattr(transcript, "segments", [])), 1), 3),
                "model_used": "whisper-api",
                "agent": self.name,
            }

        except Exception as e:
            self.log("error", f"Transcription failed: {e}")
            # Clean up temp file on error
            if temp_file and os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
            return {"error": str(e), "transcript": "", "confidence": 0.0}
