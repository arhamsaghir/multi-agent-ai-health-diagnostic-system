"""Unit tests for the DEMAT Self-Generated Regression Harness and its metrics.

The harness compares DEMAT triage against single-pass ablation on 200 cases
generated from the same DISEASE_DATABASE the system reasons over, with
follow-up answers simulated from the same likelihood tables. The oracle is
the system under test, so every number it produces is an internal-consistency
measurement — NOT an accuracy result. These tests verify the harness's
regression value (entropy mechanics, ranking, stopping, determinism) and its
honesty contract (banner + harness_type in every output). See
`data/benchmarks/RETIREMENT.md` for why the old 98% accuracy framing was
retired.
"""

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
    REGRESSION_BANNER,
    simulate_patient_answer,
    normalize_disease_key,
    run_benchmark,
)
from src.core.disease_kb import DISEASE_DATABASE
from src.core.question_bank import CLINICAL_QUESTION_BANK


class TestRegressionMetricUtilities:
    """Metric utilities used by the regression harness (pure functions)."""

    def test_top_k_ranking_utility_exact_and_alias(self):
        """compute_top_k drives every consistency ratio the harness reports."""
        candidates = [("cardiovascular disease", 0.70), ("hypertension", 0.20), ("gerd", 0.10)]
        # Top 1 hit
        assert compute_top_k(candidates, ["Cardiovascular Disease"], k=1)
        assert compute_top_k(candidates, ["Heart Disease", "Coronary Artery Disease"], k=1)
        # Top 1 miss, top 2 hit
        assert not compute_top_k(candidates, ["Hypertension"], k=1)
        assert compute_top_k(candidates, ["Hypertension"], k=2)
        # Top 3 miss
        assert not compute_top_k(candidates, ["Pneumonia"], k=3)

    def test_brier_score_utility(self):
        """Brier is a belief-sharpness diagnostic, not an accuracy number."""
        # Perfect prediction
        perfect_probs = {"pneumonia": 1.0, "asthma": 0.0}
        assert compute_brier_score(perfect_probs, "pneumonia", ["Pneumonia"]) == 0.0

        # Uniform uncertain prediction
        uncertain_probs = {"pneumonia": 0.5, "asthma": 0.5}
        # (0.5 - 1)^2 + (0.5 - 0)^2 = 0.25 + 0.25 = 0.50
        assert abs(compute_brier_score(uncertain_probs, "pneumonia", ["Pneumonia"]) - 0.50) < 1e-4

    def test_ece_utility_perfect_vs_miscalibrated(self):
        """ECE on self-generated cases is reported but never cited as calibration."""
        # Completely calibrated: 10 predictions at 1.0 confidence, all 10 correct
        conf_perfect = [1.0] * 10
        acc_perfect = [True] * 10
        assert compute_ece(conf_perfect, acc_perfect, n_bins=10) == 0.0

        # Overconfident: 10 predictions at 0.95 confidence, but only 2 correct
        conf_over = [0.95] * 10
        acc_over = [True, True] + [False] * 8
        ece_over = compute_ece(conf_over, acc_over, n_bins=10)
        assert ece_over > 0.6  # |0.20 - 0.95| = 0.75

    def test_mcnemar_utility_statistical_test(self):
        """McNemar compares the two arms' consistency, not clinical performance."""
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


class TestSelfGeneratedCaseSupport:
    """Support functions for self-generated cases.

    simulate_patient_answer answers follow-ups from the same DISEASE_DATABASE
    the harness scores against — this is precisely why the harness is
    circular and its numbers are not accuracy.
    """

    def test_normalize_disease_key(self):
        assert normalize_disease_key("Type 2 Diabetes") == "type 2 diabetes"
        assert normalize_disease_key("GERD") == "gerd"
        assert normalize_disease_key("Lumbar Strain") == "back pain"
        assert normalize_disease_key("TIA") == "neurological disorder"
        assert normalize_disease_key("Atopic Dermatitis") == "eczema"

    def test_simulate_patient_answer_derives_from_same_kb(self):
        """Answers come from KB likelihoods — the circularity that retired the claim."""
        q_reflux = next(q for q in CLINICAL_QUESTION_BANK if q["id"] == "q_reflux_heartburn")
        # Text with heartburn should trigger the burning/regurgitation option
        ans = simulate_patient_answer(q_reflux, "gerd", "I have burning heartburn and sour regurgitation")
        assert "regurgitation" in ans.lower() or "burning" in ans.lower()

        # Text with rash should trigger eczema rash answer
        q_rash = next(q for q in CLINICAL_QUESTION_BANK if q["id"] == "q_dermatologic_rash")
        ans_rash = simulate_patient_answer(q_rash, "eczema", "My skin is cracking and itchy rash")
        assert ans_rash == "Yes"


class TestRegressionHarnessExecution:
    """End-to-end harness run: mechanics regressions and honesty contract."""

    def test_smoke_regression_on_self_generated_cases(self, tmp_path, capsys):
        """The harness still runs deterministically and labels its own output.

        Verifies (a) the DEMAT mechanics the harness is a regression fence
        for — entropy reduction from active inquiry on the self-generated
        set — and (b) that every output is labeled as internal-consistency
        only: harness_type metadata, the banner in the console output, and
        the banner in the generated summary file. None of these numbers may
        be cited as accuracy (data/benchmarks/RETIREMENT.md).
        """
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

        # Honesty contract: metadata declares the harness type.
        harness_type = results["metadata"]["harness_type"].lower()
        assert "regression harness" in harness_type
        assert "not an accuracy evaluation" in harness_type

        # Honesty contract: the banner is printed on every run.
        captured = capsys.readouterr()
        assert "SELF-GENERATED REGRESSION HARNESS" in captured.out
        assert "NOT AN ACCURACY EVALUATION" in captured.out

        # Verify output files written
        json_file = out_dir / "demat_research_benchmark.json"
        md_file = out_dir / "demat_benchmark_summary.md"
        assert json_file.exists()
        assert md_file.exists()

        # Honesty contract: the generated summary carries the banner.
        md_text = md_file.read_text()
        for banner_line in REGRESSION_BANNER:
            assert banner_line in md_text

        # Check JSON deserializability
        with open(json_file) as jf:
            loaded = json.load(jf)
        assert loaded["metadata"]["total_cases"] == 200
        assert "regression harness" in loaded["metadata"]["harness_type"].lower()
