"""Unit tests for Dynamic Entropy-Minimizing Active Triage (DEMAT) engine."""

import math
import pytest
from src.core.demat import DEMATEngine, TriageSession


class TestDEMATMath:
    """Test information-theoretic mathematics of the DEMAT engine."""

    def test_shannon_entropy_uniform(self):
        """Uniform distribution across N states must have entropy equal to log2(N)."""
        engine = DEMATEngine()
        n = 10
        uniform_dist = {f"d_{i}": 1.0 / n for i in range(n)}
        entropy = engine.calculate_entropy(uniform_dist)
        expected = math.log2(n)
        assert abs(entropy - expected) < 1e-6

    def test_shannon_entropy_deterministic(self):
        """A deterministic distribution with a single condition certainty must have 0 entropy."""
        engine = DEMATEngine()
        certain_dist = {"pneumonia": 1.0, "asthma": 0.0, "migraine": 0.0}
        entropy = engine.calculate_entropy(certain_dist)
        assert abs(entropy - 0.0) < 1e-6

    def test_initial_belief_construction_and_priors(self):
        """Symptom keywords and patient demographics should shift the prior distribution."""
        engine = DEMATEngine()
        belief, entropy = engine.compute_initial_belief(
            text="Severe crushing chest pain radiating to left arm and shortness of breath",
            patient_history={"age": 62, "bmi": 29.5, "family_history": ["heart_disease"]},
        )

        assert abs(sum(belief.values()) - 1.0) < 1e-4
        assert entropy > 0.5
        # Cardiovascular disease should have the highest prior given clinical presentation
        assert belief["cardiovascular disease"] == max(belief.values())

    def test_expected_information_gain_ranking(self):
        """Questions must be ranked by descending expected mutual information."""
        engine = DEMATEngine()
        belief, _ = engine.compute_initial_belief("I have chest pain and cough")
        ranked_questions = engine.select_next_questions(belief, k=3)

        assert len(ranked_questions) <= 3
        assert len(ranked_questions) > 0

        # Assert descending order of information gain
        igs = [q["expected_information_gain"] for q in ranked_questions]
        assert igs == sorted(igs, reverse=True)
        assert igs[0] > 0.0

    def test_bayesian_belief_update_reduces_entropy(self):
        """Answering an informative diagnostic question must decrease Shannon entropy."""
        engine = DEMATEngine()
        belief, initial_entropy = engine.compute_initial_belief("I have chest discomfort and cough")

        top_questions = engine.select_next_questions(belief, k=1)
        best_q = top_questions[0]
        answer = list(best_q["likelihoods"].keys())[0]

        posterior_belief, posterior_entropy = engine.update_belief_from_answer(
            belief, best_q["id"], answer
        )

        assert abs(sum(posterior_belief.values()) - 1.0) < 1e-4
        assert posterior_entropy < initial_entropy
        entropy_reduction = initial_entropy - posterior_entropy
        assert entropy_reduction > 0.05

    def test_triage_session_state_and_stopping(self):
        """Multi-turn triage session tracks entropy reduction and halts when converged."""
        engine = DEMATEngine()
        session = engine.start_or_get_session(
            session_id=None,
            text="Headache and fever",
            patient_history={"age": 28},
        )

        assert session.session_id is not None
        assert session.round_count == 0
        assert not session.converged

        # Simulate round 1
        q_list = engine.select_next_questions(session.belief, k=1)
        session.round_count += 1
        session.asked_question_ids.append(q_list[0]["id"])

        ans = list(q_list[0]["likelihoods"].keys())[0]
        session.belief, session.entropy = engine.update_belief_from_answer(
            session.belief, q_list[0]["id"], ans
        )
        session.answered_question_ids.append(q_list[0]["id"])

        summary = session.to_dict()
        assert "entropy_bits" in summary
        assert "top_candidates" in summary
        assert len(summary["top_candidates"]) > 0
