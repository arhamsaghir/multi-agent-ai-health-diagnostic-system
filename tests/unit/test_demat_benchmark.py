"""Unit tests for AegisMed Phase 3 Research Benchmark Harness and metrics."""

import json
from pathlib import Path
import pytest

from scripts.benchmark.metrics import (
    compute_top_k,
    compute_brier_score,
    compute_ece,
    compute_mcnemar_test,
)
from scripts.benchmark.demat_benchmark import (
    simulate_patient_answer,
    normalize_disease_key,
    run_benchmark,
)
from src.core.disease_kb import DISEASE_DATABASE
from src.core.question_bank import CLINICAL_QUESTION_BANK


class TestBenchmarkMetrics:
    """Test suite for statistical and clinical benchmark metrics."""

    def test_top_k_exact_and_alias(self):
        candidates = [("cardiovascular disease", 0.70), ("hypertension", 0.20), ("gerd", 0.10)]
        # Top 1 hit
        assert compute_top_k(candidates, ["Cardiovascular Disease"], k=1)
        assert compute_top_k(candidates, ["Heart Disease", "Coronary Artery Disease"], k=1)
        # Top 1 miss, top 2 hit
        assert not compute_top_k(candidates, ["Hypertension"], k=1)
        assert compute_top_k(candidates, ["Hypertension"], k=2)
        # Top 3 miss
        assert not compute_top_k(candidates, ["Pneumonia"], k=3)

    def test_brier_score(self):
        # Perfect prediction
        perfect_probs = {"pneumonia": 1.0, "asthma": 0.0}
        assert compute_brier_score(perfect_probs, "pneumonia", ["Pneumonia"]) == 0.0

        # Uniform uncertain prediction
        uncertain_probs = {"pneumonia": 0.5, "asthma": 0.5}
        # (0.5 - 1)^2 + (0.5 - 0)^2 = 0.25 + 0.25 = 0.50
        assert abs(compute_brier_score(uncertain_probs, "pneumonia", ["Pneumonia"]) - 0.50) < 1e-4

    def test_ece_perfect_vs_miscalibrated(self):
        # Completely calibrated: 10 predictions at 1.0 confidence, all 10 correct
        conf_perfect = [1.0] * 10
        acc_perfect = [True] * 10
        assert compute_ece(conf_perfect, acc_perfect, n_bins=10) == 0.0

        # Overconfident: 10 predictions at 0.95 confidence, but only 2 correct
        conf_over = [0.95] * 10
        acc_over = [True, True] + [False] * 8
        ece_over = compute_ece(conf_over, acc_over, n_bins=10)
        assert ece_over > 0.6  # |0.20 - 0.95| = 0.75

    def test_mcnemar_statistical_test(self):
        # Equal performance: no difference
        a1 = [True, True, False, False]
        a2 = [True, True, False, False]
        m0 = compute_mcnemar_test(a1, a2)
        assert m0["p_value"] == 1.0
        assert m0["chi2"] == 0.0

        # Clear advantage for Arm 1
        a1_adv = [True] * 20 + [False] * 5
        a2_adv = [False] * 20 + [False] * 5
        m_adv = compute_mcnemar_test(a1_adv, a2_adv)
        assert m_adv["discordant_b"] == 20
        assert m_adv["discordant_c"] == 0
        assert m_adv["p_value"] < 0.001


class TestSimulationAndNormalization:
    """Test suite for clinical inquiry answering and disease key normalization."""

    def test_normalize_disease_key(self):
        assert normalize_disease_key("Type 2 Diabetes") == "type 2 diabetes"
        assert normalize_disease_key("GERD") == "gerd"
        assert normalize_disease_key("Lumbar Strain") == "back pain"
        assert normalize_disease_key("TIA") == "neurological disorder"
        assert normalize_disease_key("Atopic Dermatitis") == "eczema"

    def test_simulate_patient_answer_heuristics(self):
        q_reflux = next(q for q in CLINICAL_QUESTION_BANK if q["id"] == "q_reflux_heartburn")
        # Text with heartburn should trigger the burning/regurgitation option
        ans = simulate_patient_answer(q_reflux, "gerd", "I have burning heartburn and sour regurgitation")
        assert "regurgitation" in ans.lower() or "burning" in ans.lower()

        # Text with rash should trigger eczema rash answer
        q_rash = next(q for q in CLINICAL_QUESTION_BANK if q["id"] == "q_dermatologic_rash")
        ans_rash = simulate_patient_answer(q_rash, "eczema", "My skin is cracking and itchy rash")
        assert ans_rash == "Yes"


class TestBenchmarkExecution:
    """Test suite for full benchmark harness execution."""

    def test_run_benchmark_determinism(self, tmp_path):
        cases_file = Path(__file__).resolve().parents[2] / "data" / "benchmark_cases.json"
        assert cases_file.exists(), "Benchmark cases file must exist"

        out_dir = tmp_path / "results"
        results = run_benchmark(
            cases_path=str(cases_file),
            output_dir=str(out_dir),
            max_rounds=2,
            stopping_entropy=0.80
        )

        assert results["metadata"]["total_cases"] == 200
        assert results["metadata"]["diseases_modeled"] == 15
        assert results["arm1_demat"]["top1_accuracy"] >= 0.95
        assert results["arm1_demat"]["top3_accuracy"] == 1.00
        assert results["arm1_demat"]["mean_entropy_reduction"] > 1.0

        # Verify output files written
        json_file = out_dir / "demat_research_benchmark.json"
        md_file = out_dir / "demat_benchmark_summary.md"
        assert json_file.exists()
        assert md_file.exists()

        # Check JSON deserializability
        with open(json_file) as jf:
            loaded = json.load(jf)
        assert loaded["metadata"]["total_cases"] == 200
