"""NLP Symptom Agent — clinical symptom, entity and intent extraction.

Symptom extraction runs on deterministic clinical patterns by default and can
be extended with a biomedical NER model (see ``settings.enable_biobert_ner``).
Both paths feed the same downstream contract, so the pipeline degrades to the
pattern extractor whenever the model is unavailable.
"""

from typing import Any
import re
from loguru import logger

from config import settings
from src.agents.base import BaseAgent
from src.data.preprocessing.text_preprocessor import TextPreprocessor


class NLPAgent(BaseAgent):
    """NLP agent for symptom text analysis."""

    name = "nlp_agent"
    description = "Clinical NLP — symptom/entity extraction and intent classification"

    # Pattern-based symptom extraction by body system/category
    SYMPTOM_PATTERNS = {
        "respiratory": r'\b(cough|wheez(?:e|ing)|shortness of breath|difficulty breathing|trouble breathing|rapid breathing|shallow breathing|chest tightness|runny nose|nasal congestion|sneezing|postnasal drip|hemoptysis|coughing up blood|productive cough|dry cough|barking cough|whooping cough)\b',
        "cardiovascular": r'\b(chest pain|chest pressure|heart palpitations|irregular heartbeat|rapid heartbeat|skipped beats|swollen ankles|swollen legs|leg swelling|edema|orthopnea|paroxysmal nocturnal dyspnea|angina|heart murmur)\b',
        "gastrointestinal": r'\b(nausea|vomiting|diarrhea|constipation|abdominal pain|stomach pain|belly pain|bloating|heartburn|acid reflux|indigestion|loss of appetite|decreased appetite|bloody stool|black stool|jaundice|yellow skin|yellow eyes)\b',
        "neurological": r'\b(headache|migraine|dizziness|vertigo|fainting|syncope|numbness|tingling|pins and needles|tremor|seizure|confusion|memory loss|difficulty concentrating|brain fog|slurred speech|weakness on one side|paralysis)\b',
        "musculoskeletal": r'\b(back pain|joint pain|muscle pain|muscle ache|body ache|stiff joints|swollen joints|limited range of motion|muscle cramp|muscle spasm|neck pain|shoulder pain|hip pain|knee pain|lower back pain)\b',
        "dermatological": r'\b(rash|itching|hives|skin discoloration|bruising|dry skin|flaky skin|blister|boil|skin lesion|mole change|hair loss|nail changes|skin peeling|eczema|psoriasis)\b',
        "constitutional": r'\b(fever|chills|fatigue|tired|exhaustion|weight loss|weight gain|night sweats|swollen lymph nodes|swollen glands|malaise|cold intolerance|heat intolerance|excessive thirst|excessive hunger)\b',
        "urinary": r'\b(frequent urination|painful urination|burning when urinating|blood in urine|dark urine|incontinence|bed wetting|reduced urination|difficulty starting urine stream|foamy urine|flank pain|kidney pain)\b',
        "psychiatric": r'\b(anxiety|depression|panic attack|insomnia|sleeplessness|loss of interest|hopelessness|suicidal thoughts|mood swings|irritability|restlessness|social withdrawal|hallucinations|delusions)\b',
        "ENT": r'\b(sore throat|throat pain|ear pain|ear discharge|hearing loss|tinnitus|ringing in ears|sinus pain|facial pain|loss of smell|loss of taste|hoarse voice|difficulty swallowing|painful swallowing|swollen tonsils|tonsil stones)\b',
        "ophthalmological": r'\b(blurred vision|double vision|eye pain|red eyes|dry eyes|watery eyes|sensitivity to light|eye discharge|floaters|flashes of light|vision loss|halos around lights)\b',
    }

    # Body system keywords for contextual detection. Forms that are not
    # simple suffix variants of a base word ("headache", "arteries",
    # "heartburn") are listed explicitly, because whole-word matching would
    # otherwise miss them.
    BODY_SYSTEMS = {
        "respiratory": ["lung", "breath", "breathing", "breathless", "cough", "wheeze", "pneumonia", "asthma", "bronchitis", "airway", "trachea", "oxygen"],
        "cardiovascular": ["heart", "heartbeat", "palpitation", "blood pressure", "pulse", "artery", "arteries", "vein", "circulation", "cardiac", "angina", "cholesterol"],
        "gastrointestinal": ["stomach", "heartburn", "digestion", "bowel", "liver", "intestine", "colon", "gastric", "esophagus", "appendix"],
        "neurological": ["brain", "nerve", "head", "headache", "migraine", "vertigo", "cognitive", "seizure", "consciousness", "memory", "reflex", "spinal cord"],
        "musculoskeletal": ["bone", "muscle", "joint", "skeleton", "cartilage", "ligament", "tendon", "spine", "posture"],
        "dermatological": ["skin", "dermal", "epidermal", "rash", "lesion", "mole", "pigment", "dermatitis"],
        "endocrine": ["hormone", "thyroid", "insulin", "diabetes", "gland", "blood sugar", "metabolic", "cortisol"],
        "urinary": ["kidney", "bladder", "urine", "urinary", "renal", "ureter", "dialysis", "prostate"],
        "reproductive": ["menstrual", "pregnancy", "ovary", "ovaries", "testicular", "prostate", "fertility", "contraception"],
        "psychiatric": ["mood", "anxiety", "depression", "mental health", "psychological", "emotional", "stress", "trauma"],
        "immune": ["immune", "infection", "inflammation", "autoimmune", "allergy", "allergies", "antibody", "fever", "white blood cell"],
        "ENT": ["ear", "nose", "throat", "sinus", "hearing", "tongue", "tonsil", "larynx", "pharynx"],
        "ophthalmological": ["eye", "vision", "retina", "pupil", "cornea", "lens", "optic", "sight"],
        "hematological": ["blood", "anemia", "hemoglobin", "clot", "platelet", "bleeding", "bruise", "hematocrit"],
    }

    # Compiled word-boundary matchers so "ear" cannot match inside "heart".
    # A small suffix set is allowed so inflected forms still match
    # ("breath" covers "breathe" and "breathing").
    BODY_SYSTEM_PATTERNS = {
        system: [
            re.compile(rf"\b{re.escape(kw)}(?:s|es|ing|ed|e)?\b")
            for kw in keywords
        ]
        for system, keywords in BODY_SYSTEMS.items()
    }

    def __init__(self):
        super().__init__()
        self.preprocessor = TextPreprocessor()
        self.model = None
        self.tokenizer = None
        self._model_loaded = False
        self._load_attempted = False
        self._load_error = None
        # Don't load the NER model at init — lazy load on first use

    def _try_load_biobert(self):
        """Load the optional biomedical NER model, if enabled and reachable.

        The deterministic pattern extractor is the default path. When
        ``ENABLE_BIOBERT_NER`` is set, a token-classification checkpoint is
        loaded and its entities are merged with the pattern entities; any
        failure falls back to patterns alone.
        """
        if self._load_attempted:
            return

        self._load_attempted = True
        if not settings.enable_biobert_ner:
            return

        try:
            from transformers import AutoTokenizer, AutoModelForTokenClassification
            self.tokenizer = AutoTokenizer.from_pretrained(settings.biobert_model_id)
            self.model = AutoModelForTokenClassification.from_pretrained(settings.biobert_model_id)
            self._model_loaded = True
            self.log("info", f"NER model loaded: {settings.biobert_model_id}")
        except Exception as e:
            self._load_error = str(e)
            self.log("warning", f"NER model unavailable, using deterministic extraction: {e}")

    def _extract_biobert_entities(self, text: str) -> list[dict]:
        """Extract biomedical named entities with the NER model.

        Returns an empty list when the model is not loaded or inference fails,
        so the caller always has the pattern entities as a floor.
        """
        if not self._model_loaded or self.model is None or self.tokenizer is None:
            return []

        try:
            import torch

            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            with torch.no_grad():
                logits = self.model(**inputs).logits
            predictions = torch.argmax(logits, dim=-1)[0].tolist()
            tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
            id2label = self.model.config.id2label

            entities: list[dict] = []
            current: dict | None = None
            for token, pred_id in zip(tokens, predictions):
                label = id2label[pred_id]
                if token in self.tokenizer.all_special_tokens:
                    if current:
                        entities.append(current)
                        current = None
                    continue
                if label.startswith("B-"):
                    if current:
                        entities.append(current)
                    current = {"type": label[2:].lower(), "value": token}
                elif label.startswith("I-") and current:
                    current["value"] += token.replace("##", "")
                else:
                    if current:
                        entities.append(current)
                        current = None
            if current:
                entities.append(current)

            return [e for e in entities if e["value"].strip()]
        except Exception as e:
            self.log("warning", f"NER extraction failed, falling back to patterns: {e}")
            return []

    async def run(self, input_data: dict) -> dict:
        """Extract symptoms, entities, and intent from text.

        Args:
            input_data: Dict with 'text' key containing symptom description.

        Returns:
            Dict with extracted symptoms, entities, body systems, and intent.
        """
        text = input_data.get("text", "")

        if not text.strip():
            return {"error": "No text provided", "symptoms": [], "entities": []}

        # Lazy load BioBERT on first use
        self._try_load_biobert()

        # Preprocess text through the data layer
        processed = self.preprocessor.preprocess(text)
        normalized_text = processed["normalized"]
        duration = self.preprocessor.extract_duration(text)
        severity_indicators = self.preprocessor.extract_severity_indicators(text)

        symptoms = self._extract_symptoms(normalized_text)
        entities = self._extract_entities(normalized_text)
        entities.extend(self._extract_biobert_entities(normalized_text))
        body_systems = self._detect_body_systems(normalized_text)
        intent = self._classify_intent(normalized_text)

        # Determine overall severity from indicators
        if severity_indicators.get("severe"):
            severity = "high"
        elif severity_indicators.get("moderate"):
            severity = "moderate"
        else:
            severity = "mild"

        return {
            "symptoms": symptoms,
            "entities": entities,
            "body_systems": body_systems,
            "severity_indicator": severity,
            "severity_indicators": severity_indicators,
            "intent": intent,
            "duration": duration,
            "preprocessed": processed,
            "extractor": "ner_model" if self._model_loaded else "deterministic_patterns",
            "agent": self.name,
        }

    def _extract_symptoms(self, text: str) -> list[dict]:
        """Extract symptoms using pattern matching or BioBERT."""
        found = []
        for category, pattern in self.SYMPTOM_PATTERNS.items():
            matches = re.findall(pattern, text)
            for match in matches:
                found.append({"symptom": match, "category": category})

        # Deduplicate
        seen = set()
        unique = []
        for s in found:
            if s["symptom"] not in seen:
                seen.add(s["symptom"])
                unique.append(s)

        return unique

    def _extract_entities(self, text: str) -> list[dict]:
        """Extract medical named entities."""
        entities = []

        # Body parts
        body_part_pattern = r'\b(head|chest|stomach|back|arm|leg|throat|nose|eye|ear|hand|foot|knee|shoulder|abdomen|neck|jaw)\b'
        for match in re.finditer(body_part_pattern, text):
            entities.append({"type": "body_part", "value": match.group()})

        # Time references
        time_pattern = r'\b(\d+\s*(day|week|month|hour|year)s?)\b'
        for match in re.finditer(time_pattern, text):
            entities.append({"type": "duration", "value": match.group()})

        # Severity modifiers
        severity_pattern = r'\b(severe|moderate|mild|intense|extreme|slight|terrible|unbearable)\b'
        for match in re.finditer(severity_pattern, text):
            entities.append({"type": "severity_modifier", "value": match.group()})

        return entities

    def _detect_body_systems(self, text: str) -> list[str]:
        """Detect which body systems are referenced.

        Matching is word-boundary based so a keyword never matches inside an
        unrelated word (e.g. "ear" inside "heart").
        """
        return [
            system
            for system, patterns in self.BODY_SYSTEM_PATTERNS.items()
            if any(pattern.search(text) for pattern in patterns)
        ]

    def _assess_severity(self, text: str) -> str:
        """Assess symptom severity from language cues."""
        high_words = ["severe", "extreme", "unbearable", "worst", "terrible", "agony", "emergency"]
        moderate_words = ["moderate", "significant", "considerable", "persistent"]

        if any(w in text for w in high_words):
            return "high"
        elif any(w in text for w in moderate_words):
            return "moderate"
        return "mild"

    def _classify_intent(self, text: str) -> str:
        """Classify the user's intent."""
        if any(w in text for w in ["diagnos", "what do i have", "what is wrong", "condition"]):
            return "diagnosis_request"
        elif any(w in text for w in ["treat", "remedy", "medicine", "cure", "help"]):
            return "treatment_request"
        elif any(w in text for w in ["serious", "emergency", "urgent", "doctor"]):
            return "urgency_assessment"
        return "general_inquiry"

    def _extract_duration(self, text: str) -> str:
        """Extract symptom duration if mentioned."""
        duration_pattern = r'(\d+\s*(day|week|month|hour|year)s?)'
        match = re.search(duration_pattern, text)
        return match.group(1) if match else "not specified"
