"""Translation service for multilingual support via OpenRouter."""

from typing import Optional
from loguru import logger
import json

from src.llm.openrouter_client import OpenRouterClient


class TranslationService:
    """Translates text between languages using OpenRouter LLM."""

    def __init__(self):
        self._client = None
    
    @property
    def client(self) -> OpenRouterClient:
        """Lazy-load OpenRouter client."""
        if self._client is None:
            self._client = OpenRouterClient()
        return self._client
    
    def translate_to_english(self, text: str, source_language: str = "auto") -> str:
        """Translate text to English.
        
        Args:
            text: Text to translate.
            source_language: Source language code (e.g., 'hi' for Hindi).
        
        Returns:
            Translated text in English.
        """
        if source_language == "en" or not text.strip():
            return text
        
        lang_name = {
            "hi": "Hindi",
            "es": "Spanish",
            "ar": "Arabic",
            "fr": "French",
            "de": "German",
            "ur": "Urdu",
            "bn": "Bengali",
            "ta": "Tamil",
            "te": "Telugu",
            "mr": "Marathi",
            "gu": "Gujarati",
        }.get(source_language, "the source language")
        
        prompt = f"""Translate the following {lang_name} text to English. 
Preserve all medical terms and symptoms accurately.
Do not add any explanations or notes — return only the translated text.

Text to translate:
{text}

English translation:"""

        try:
            result = self.client.generate(
                prompt=prompt,
                system_message="You are a professional medical translator. Translate accurately while preserving medical terminology. Return only the translated text.",
                temperature=0.1,
                max_tokens=512,
                timeout=30,
            )
            
            # Clean up response
            result = result.strip()
            if result.startswith('"') and result.endswith('"'):
                result = result[1:-1]
            
            logger.info(f"Translated {lang_name} → English ({len(text)} chars)")
            return result
        except Exception as e:
            logger.error(f"Translation to English failed: {e}")
            return text
    
    def translate_from_english(self, text: str, target_language: str = "hi") -> str:
        """Translate text from English to target language.
        
        Args:
            text: English text to translate.
            target_language: Target language code (e.g., 'hi' for Hindi).
        
        Returns:
            Translated text in target language.
        """
        if target_language == "en" or not text.strip():
            return text
        
        lang_name = {
            "hi": "Hindi",
            "es": "Spanish",
            "ar": "Arabic",
            "fr": "French",
            "de": "German",
            "ur": "Urdu",
            "bn": "Bengali",
            "ta": "Tamil",
            "te": "Telugu",
            "mr": "Marathi",
            "gu": "Gujarati",
        }.get(target_language, "the target language")
        
        prompt = f"""Translate the following English text to {lang_name}.
Preserve medical terms accurately. If a medical term has no direct translation, keep it in English.
Do not add any explanations or notes — return only the translated text.

Text to translate:
{text}

{lang_name} translation:"""

        try:
            result = self.client.generate(
                prompt=prompt,
                system_message=f"You are a professional medical translator. Translate accurately to {lang_name} while preserving medical terminology. Return only the translated text.",
                temperature=0.1,
                max_tokens=1024,
                timeout=30,
            )
            
            # Clean up response
            result = result.strip()
            if result.startswith('"') and result.endswith('"'):
                result = result[1:-1]
            
            logger.info(f"Translated English → {lang_name} ({len(text)} chars)")
            return result
        except Exception as e:
            logger.error(f"Translation from English failed: {e}")
            return text
    
    def translate_diagnosis(self, diagnosis: dict, target_language: str = "hi") -> dict:
        """Translate entire diagnosis result to target language.
        
        Args:
            diagnosis: Diagnosis result dict.
            target_language: Target language code.
        
        Returns:
            Translated diagnosis dict.
        """
        if target_language == "en":
            return diagnosis
        
        translated = diagnosis.copy()
        
        # Translate text fields
        for field in ["explanation", "patient_explanation", "disclaimer"]:
            if diagnosis.get(field):
                translated[field] = self.translate_from_english(diagnosis[field], target_language)
        
        # Translate condition names and rationales
        for d in translated.get("diagnosis", []):
            if d.get("condition"):
                d["condition"] = self.translate_from_english(d["condition"], target_language)
            if d.get("rationale"):
                d["rationale"] = self.translate_from_english(d["rationale"], target_language)
        
        # Translate differential diagnoses
        translated["differential_diagnoses"] = [
            self.translate_from_english(dd, target_language)
            for dd in diagnosis.get("differential_diagnoses", [])
        ]
        
        # Translate red flags
        translated["red_flags"] = [
            self.translate_from_english(rf, target_language)
            for rf in diagnosis.get("red_flags", [])
        ]
        
        # Translate recommendations
        translated["recommendations"] = [
            self.translate_from_english(rec, target_language)
            for rec in diagnosis.get("recommendations", [])
        ]
        
        return translated
