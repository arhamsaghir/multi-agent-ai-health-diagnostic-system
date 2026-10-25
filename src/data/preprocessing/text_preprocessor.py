"""Text preprocessing for symptom descriptions and medical text."""

import re
from typing import Optional


class TextPreprocessor:
    """Cleans, normalizes, and standardizes medical symptom text."""

    # Common medical abbreviations → full forms
    ABBREVIATIONS = {
        "ha": "headache",
        "sob": "shortness of breath",
        "doe": "dyspnea on exertion",
        "cp": "chest pain",
        "fh": "family history",
        "pmh": "past medical history",
        "htn": "hypertension",
        "dm": "diabetes mellitus",
        "copd": "chronic obstructive pulmonary disease",
        "uri": "upper respiratory infection",
        "uti": "urinary tract infection",
        "gi": "gastrointestinal",
        "gu": "genitourinary",
        "neuro": "neurological",
        "resp": "respiratory",
        "cardio": "cardiovascular",
        "mild mod": "mild to moderate",
        "mod severe": "moderate to severe",
        "w/o": "without",
        "w/": "with",
        "dx": "diagnosis",
        "rx": "treatment",
        "tx": "treatment",
        "hx": "history",
        "sx": "symptoms",
        "fx": "fracture",
        "b/l": "bilateral",
        "r/t": "right",
        "l/t": "left",
    }

    # Symptom normalization → canonical form
    SYMPTOM_CANONICAL = {
        "head hurts": "headache",
        "head pain": "headache",
        "my head aches": "headache",
        "hurting head": "headache",
        "feverish": "fever",
        "high temperature": "fever",
        "hot body": "fever",
        "running nose": "runny nose",
        "blocked nose": "nasal congestion",
        "stuffy nose": "nasal congestion",
        "can't breathe": "shortness of breath",
        "cant breathe": "shortness of breath",
        "difficulty breathing": "shortness of breath",
        "trouble breathing": "shortness of breath",
        "breathing hard": "shortness of breath",
        "throwing up": "vomiting",
        "throw up": "vomiting",
        "upset stomach": "nausea",
        "stomach ache": "abdominal pain",
        "stomach pain": "abdominal pain",
        "belly pain": "abdominal pain",
        "tummy ache": "abdominal pain",
        "feeling dizzy": "dizziness",
        "dizzy spells": "dizziness",
        "lightheaded": "dizziness",
        "running eyes": "watery eyes",
        "sore throat": "throat pain",
        "throat hurts": "throat pain",
        "swollen glands": "swollen lymph nodes",
        "body ache": "body pain",
        "body aches": "body pain",
        "muscle pain": "muscle pain",
        "joint pain": "joint pain",
        "aching joints": "joint pain",
        "loss of appetite": "decreased appetite",
        "no appetite": "decreased appetite",
        "not hungry": "decreased appetite",
        "can't sleep": "insomnia",
        "cant sleep": "insomnia",
        "trouble sleeping": "insomnia",
        "sleeplessness": "insomnia",
        "feeling tired": "fatigue",
        "so tired": "fatigue",
        "exhausted": "fatigue",
        "no energy": "fatigue",
        "low energy": "fatigue",
        "lethargic": "fatigue",
        "weakness": "weakness",
        "feeling weak": "weakness",
    }

    # Stop words specific to symptom descriptions
    STOP_WORDS = {
        "i", "have", "been", "having", "got", "got", "a", "an", "the", "my",
        "is", "am", "are", "was", "were", "been", "being", "for", "since",
        "with", "without", "from", "to", "of", "in", "on", "at", "and", "or",
        "but", "so", "very", "really", "just", "also", "still", "already",
        "feeling", "feel", "think", "seem", "seems", "like", "kind", "sort",
        "sorta", "kinda", "pretty", "quite", "somewhat", "getting", "got",
        "been", "experiencing", "experience", "experienced",
    }

    def __init__(self):
        self._compiled_abbrevs = {
            re.compile(rf"\b{re.escape(k)}\b", re.IGNORECASE): v
            for k, v in self.ABBREVIATIONS.items()
        }

    def clean(self, text: str) -> str:
        """Basic text cleaning: lowercase, remove extra whitespace, fix punctuation."""
        if not text:
            return ""

        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\w\s.,!?()-]", "", text)
        text = re.sub(r"\s+([.,!?])", r"\1", text)
        return text.strip()

    def expand_abbreviations(self, text: str) -> str:
        """Expand medical abbreviations to full forms."""
        for pattern, replacement in self._compiled_abbrevs.items():
            text = pattern.sub(replacement, text)
        return text

    def normalize_symptoms(self, text: str) -> str:
        """Replace symptom variants with canonical medical terms."""
        text_lower = text.lower()
        for variant, canonical in sorted(
            self.SYMPTOM_CANONICAL.items(), key=lambda x: -len(x[0])
        ):
            text_lower = text_lower.replace(variant, canonical)
        return text_lower

    def extract_keywords(self, text: str) -> list[str]:
        """Extract meaningful keywords by removing stop words."""
        cleaned = self.clean(text)
        cleaned = self.expand_abbreviations(cleaned)
        cleaned = self.normalize_symptoms(cleaned)

        words = re.findall(r"\b[a-z]{2,}\b", cleaned)
        keywords = [w for w in words if w not in self.STOP_WORDS]
        return list(dict.fromkeys(keywords))

    def preprocess(self, text: str) -> dict:
        """Full preprocessing pipeline for symptom text.

        Args:
            text: Raw symptom description from user.

        Returns:
            Dict with cleaned text, keywords, and normalized form.
        """
        cleaned = self.clean(text)
        expanded = self.expand_abbreviations(cleaned)
        normalized = self.normalize_symptoms(expanded)
        keywords = self.extract_keywords(normalized)

        return {
            "original": text,
            "cleaned": cleaned,
            "expanded_abbreviations": expanded,
            "normalized": normalized,
            "keywords": keywords,
            "word_count": len(keywords),
        }

    def extract_duration(self, text: str) -> Optional[str]:
        """Extract symptom duration from text."""
        patterns = [
            r"(\d+)\s*(day|week|month|hour|year)s?\b",
            r"for\s+(\d+)\s*(day|week|month|hour|year)s?",
            r"since\s+(\d+)\s*(day|week|month|hour|year)s?\s*ago",
            r"past\s+(\d+)\s*(day|week|month|hour|year)s?",
            r"last\s+(\d+)\s*(day|week|month|hour|year)s?",
        ]
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                num = match.group(1)
                unit = match.group(2)
                # Pluralize if not 1
                if num != "1":
                    unit = unit + "s"
                return f"{num} {unit}"
        return None

    def extract_severity_indicators(self, text: str) -> dict:
        """Extract severity-related words from text."""
        severity_words = {
            "mild": ["mild", "slight", "minor", "small", "little"],
            "moderate": ["moderate", "medium", "considerable", "significant"],
            "severe": ["severe", "intense", "extreme", "terrible", "horrible", "unbearable", "agony", "worst"],
        }

        text_lower = text.lower()
        found = {"mild": False, "moderate": False, "severe": False}

        for level, words in severity_words.items():
            if any(w in text_lower for w in words):
                found[level] = True

        return found
