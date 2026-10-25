"""Dynamic Entropy-Minimizing Active Triage (DEMAT) Engine.

Patent-oriented algorithmic core for active clinical triaging using
Shannon diagnostic entropy minimization and expected mutual information gain.
"""

from typing import Dict, List, Optional, Any, Tuple
import math
import time
import uuid
from loguru import logger

from src.core.disease_kb import DISEASE_DATABASE, find_disease_in_kb
from src.core.question_bank import CLINICAL_QUESTION_BANK


class TriageSession:
    """Stateful container for an ongoing adaptive clinical triage session."""

    def __init__(self, session_id: str, initial_belief: Dict[str, float], initial_entropy: float):
        self.session_id: str = session_id
        self.belief: Dict[str, float] = initial_belief
        self.entropy: float = initial_entropy
        self.initial_entropy: float = initial_entropy
        self.round_count: int = 0
        self.asked_question_ids: List[str] = []
        self.answered_question_ids: List[str] = []
        self.history: List[Dict[str, Any]] = []
        self.converged: bool = False
        self.created_at: float = time.time()
        self.updated_at: float = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize state for API consumers and persistent storage."""
        # Top 3 differential candidates
        sorted_candidates = sorted(self.belief.items(), key=lambda x: x[1], reverse=True)
        top_candidates = [
            {
                "disease": k,
                "name": DISEASE_DATABASE.get(k, {}).get("name", k),
                "icd10": DISEASE_DATABASE.get(k, {}).get("icd10", ""),
                "probability": round(v, 4),
            }
            for k, v in sorted_candidates[:4]
        ]

        return {
            "session_id": self.session_id,
            "entropy_bits": round(self.entropy, 4),
            "entropy_reduction": round(max(0.0, self.initial_entropy - self.entropy), 4),
            "round_count": self.round_count,
            "converged": self.converged,
            "top_candidates": top_candidates,
            "asked_questions": self.asked_question_ids,
        }


class DEMATEngine:
    """Dynamic Entropy-Minimizing Active Triage (DEMAT) algorithmic engine."""

    ENTROPY_STOPPING_THRESHOLD = 0.45  # bits (high confidence convergence)
    MAX_TRIAGE_ROUNDS = 3             # max question batches
    MIN_INFO_GAIN_THRESHOLD = 0.02    # bits (marginal utility floor)

    def __init__(self):
        self.diseases = list(DISEASE_DATABASE.keys())
        self.question_bank = CLINICAL_QUESTION_BANK
        self._sessions: Dict[str, TriageSession] = {}

    @staticmethod
    def calculate_entropy(probabilities: Dict[str, float]) -> float:
        """Compute Shannon entropy H(D) in bits over a categorical probability distribution.

        H(D) = - sum( P(d) * log2(P(d)) )
        """
        entropy = 0.0
        for prob in probabilities.values():
            if prob > 1e-12:
                entropy -= prob * math.log2(prob)
        return float(entropy)

    def compute_initial_belief(
        self,
        text: str,
        patient_history: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, float], float]:
        """Construct the initial prior belief distribution P(D) from presentation text and history.

        Args:
            text: Chief complaint / symptom description.
            patient_history: Vitals, age, BMI, family history.

        Returns:
            Tuple of (normalized_belief_dict, shannon_entropy).
        """
        text_lower = text.lower()
        scores: Dict[str, float] = {d: 0.10 for d in self.diseases}  # Uniform baseline prior with smoothing

        # 1. Symptom matching against disease knowledge base
        for d_key, info in DISEASE_DATABASE.items():
            for symptom in info.get("symptoms", []):
                s_lower = symptom.lower()
                # Check direct or word overlap
                s_words = [w for w in s_lower.split() if len(w) > 3]
                if s_lower in text_lower:
                    scores[d_key] += 1.5
                elif any(w in text_lower for w in s_words):
                    scores[d_key] += 0.6

        # 2. Integrate patient history priors (fixing underscore vs space bug)
        if patient_history:
            age = float(patient_history.get("age") or 0)
            bmi = float(patient_history.get("bmi") or 0)
            raw_fam = patient_history.get("family_history") or patient_history.get("familyHistory") or []
            # Normalize tokens (heart_disease -> heart disease)
            fam_history = [str(item).lower().replace("_", " ") for item in raw_fam]

            # Age adjustments
            if age > 50:
                scores["cardiovascular disease"] += 0.5
                scores["hypertension"] += 0.5
                scores["type 2 diabetes"] += 0.4
            if age > 65:
                scores["pneumonia"] += 0.4

            # BMI adjustments
            if bmi > 28.0:
                scores["type 2 diabetes"] += 0.6
                scores["hypertension"] += 0.5
                scores["cardiovascular disease"] += 0.4

            # Family history adjustments
            if any("heart" in f or "cardio" in f for f in fam_history):
                scores["cardiovascular disease"] += 0.8
                scores["hypertension"] += 0.4
            if any("diabetes" in f or "sugar" in f for f in fam_history):
                scores["type 2 diabetes"] += 0.8
            if any("asthma" in f or "allerg" in f for f in fam_history):
                scores["asthma"] += 0.7
            if any("migraine" in f or "headache" in f for f in fam_history):
                scores["migraine"] += 0.7
            if any("anxiety" in f or "depress" in f for f in fam_history):
                scores["anxiety disorder"] += 0.6

        # Normalize into a proper probability distribution
        total_score = sum(scores.values())
        belief = {d: scores[d] / total_score for d in self.diseases}
        entropy = self.calculate_entropy(belief)

        return belief, entropy

    def expected_information_gain(self, question: Dict[str, Any], current_belief: Dict[str, float]) -> float:
        """Compute the Expected Mutual Information I(D; A_q) in bits for a candidate question.

        I(D; A_q) = H(D) - sum_a P(A_q = a) * H(D | A_q = a)
        """
        current_entropy = self.calculate_entropy(current_belief)
        likelihoods = question.get("likelihoods", {})
        if not likelihoods:
            return 0.0

        expected_conditional_entropy = 0.0

        for option, d_likelihoods in likelihoods.items():
            # Compute marginal probability P(A_q = a) = sum_d P(a | d) * P(d)
            p_a = 0.0
            for d in self.diseases:
                p_a_given_d = d_likelihoods.get(d, 0.10)
                p_a += p_a_given_d * current_belief.get(d, 0.0)

            if p_a < 1e-12:
                continue

            # Compute posterior distribution P(d | A_q = a)
            posterior_given_a: Dict[str, float] = {}
            for d in self.diseases:
                p_a_given_d = d_likelihoods.get(d, 0.10)
                posterior_given_a[d] = (p_a_given_d * current_belief.get(d, 0.0)) / p_a

            h_given_a = self.calculate_entropy(posterior_given_a)
            expected_conditional_entropy += p_a * h_given_a

        info_gain = max(0.0, current_entropy - expected_conditional_entropy)
        return float(info_gain)

    def select_next_questions(
        self,
        current_belief: Dict[str, float],
        excluded_ids: Optional[List[str]] = None,
        k: int = 3
    ) -> List[Dict[str, Any]]:
        """Select top k inquiries maximizing expected mutual information.

        Args:
            current_belief: Current probability distribution over diseases.
            excluded_ids: Question IDs already presented to the patient.
            k: Number of questions to return.

        Returns:
            List of question dicts sorted by descending information gain.
        """
        excluded = set(excluded_ids or [])
        ranked_questions = []

        for q in self.question_bank:
            if q["id"] in excluded:
                continue

            ig = self.expected_information_gain(q, current_belief)
            ranked_questions.append({
                **q,
                "expected_information_gain": round(ig, 4),
            })

        # Sort by expected information gain descending
        ranked_questions.sort(key=lambda x: x["expected_information_gain"], reverse=True)
        return ranked_questions[:k]

    def update_belief_from_answer(
        self,
        current_belief: Dict[str, float],
        question_id: str,
        chosen_answer: str
    ) -> Tuple[Dict[str, float], float]:
        """Perform Bayesian belief update given patient's observed answer.

        P_new(d) = ( P(answer | d) * P_old(d) ) / P(answer)
        """
        # Find question
        target_q = next((q for q in self.question_bank if q["id"] == question_id), None)
        if not target_q:
            logger.warning(f"Question id {question_id} not found in question bank; returning unchanged belief")
            return current_belief, self.calculate_entropy(current_belief)

        likelihoods = target_q.get("likelihoods", {})
        # Exact or closest option match
        chosen_clean = chosen_answer.strip().lower()
        matched_option = None
        for opt in likelihoods.keys():
            if opt.lower() == chosen_clean or opt.lower().startswith(chosen_clean):
                matched_option = opt
                break

        if not matched_option:
            matched_option = list(likelihoods.keys())[0]

        d_likelihoods = likelihoods[matched_option]

        # Bayesian update
        unnormalized: Dict[str, float] = {}
        for d in self.diseases:
            p_a_given_d = d_likelihoods.get(d, 0.10)
            unnormalized[d] = p_a_given_d * current_belief.get(d, 0.0)

        total = sum(unnormalized.values())
        if total > 1e-12:
            posterior = {d: unnormalized[d] / total for d in self.diseases}
        else:
            posterior = current_belief

        new_entropy = self.calculate_entropy(posterior)
        return posterior, new_entropy

    def start_or_get_session(
        self,
        session_id: Optional[str],
        text: str,
        patient_history: Optional[Dict[str, Any]] = None
    ) -> TriageSession:
        """Retrieve existing triage session or instantiate a new one."""
        sid = session_id or str(uuid.uuid4())

        if sid in self._sessions:
            return self._sessions[sid]

        initial_belief, initial_entropy = self.compute_initial_belief(text, patient_history)
        session = TriageSession(sid, initial_belief, initial_entropy)
        self._sessions[sid] = session
        return session

    def get_session(self, session_id: str) -> Optional[TriageSession]:
        """Get an existing triage session by id."""
        return self._sessions.get(session_id)


# Module-level singleton
demat_engine = DEMATEngine()
