"""Language detection utility for multilingual support."""

from typing import Optional
from loguru import logger

try:
    from langdetect import detect, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    logger.warning("langdetect not installed — language detection disabled")

# Supported languages
SUPPORTED_LANGUAGES = {
    "en": "English",
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
}

# Default language
DEFAULT_LANGUAGE = "en"


def detect_language(text: str) -> str:
    """Detect the language of input text.
    
    Args:
        text: Input text string.
    
    Returns:
        ISO 639-1 language code (e.g., 'en', 'hi').
    """
    if not text or not text.strip():
        return DEFAULT_LANGUAGE
    
    if not LANGDETECT_AVAILABLE:
        return DEFAULT_LANGUAGE
    
    try:
        lang = detect(text)
        if lang in SUPPORTED_LANGUAGES:
            logger.debug(f"Detected language: {lang} ({SUPPORTED_LANGUAGES[lang]})")
            return lang
        else:
            logger.debug(f"Unsupported language detected: {lang}, defaulting to English")
            return DEFAULT_LANGUAGE
    except LangDetectException as e:
        logger.warning(f"Language detection failed: {e}")
        return DEFAULT_LANGUAGE


def is_multilingual(text: str) -> bool:
    """Check if text is in a non-English supported language.
    
    Args:
        text: Input text string.
    
    Returns:
        True if text is in a supported non-English language.
    """
    lang = detect_language(text)
    return lang != DEFAULT_LANGUAGE


def get_language_name(lang_code: str) -> str:
    """Get human-readable language name from code.
    
    Args:
        lang_code: ISO 639-1 language code.
    
    Returns:
        Human-readable language name.
    """
    return SUPPORTED_LANGUAGES.get(lang_code, lang_code)
