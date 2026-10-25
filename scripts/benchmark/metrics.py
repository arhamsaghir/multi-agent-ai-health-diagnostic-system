"""Statistical and clinical evaluation metrics for CDSS benchmarks.

Implements Top-k accuracy, Shannon diagnostic entropy metrics,
Expected Calibration Error (ECE), Brier score, and McNemar statistical tests.
"""

from typing import List, Dict, Any, Tuple
import math
import numpy as np


def compute_top_k(
    ranked_candidates: List[Tuple[str, float]],
    acceptable_conditions: List[str],
    k: int = 1
) -> bool:
    """Check if any acceptable condition is present in top-k candidates.

    Args:
        ranked_candidates: List of (disease_key, probability) tuples sorted desc.
        acceptable_conditions: List of acceptable ground-truth names/aliases.
        k: Cutoff rank.

    Returns:
        True if hit in top k, False otherwise.
    """
    top_k_keys = [cand[0].lower().strip() for cand in ranked_candidates[:k]]
    acceptable_normalized = [acc.lower().strip() for acc in acceptable_conditions]

    for cand_key in top_k_keys:
        for acc in acceptable_normalized:
            if cand_key == acc or cand_key in acc or acc in cand_key:
                return True
            # Special aliases
            if "upper respiratory infection" in cand_key and "respiratory infection" in acc:
                return True
            if ("heart disease" in acc or "coronary" in acc) and "cardiovascular" in cand_key:
                return True
            if "stroke" in acc and "neurological" in cand_key:
                return True
            if "tia" in acc and "neurological" in cand_key:
                return True
            if "lumbar" in acc and "back pain" in cand_key:
                return True
            if "atopic" in acc and "eczema" in cand_key:
                return True

    return False


def compute_brier_score(
    probabilities: Dict[str, float],
    true_disease: str,
    acceptable_conditions: List[str]
) -> float:
    """Compute multiclass Brier score: sum((p_j - y_j)^2).

    Lower is better (0.0 is perfect calibration, 2.0 is worst-case).
    """
    score = 0.0
    true_norm = true_disease.lower().strip()
    acceptable_norm = [a.lower().strip() for a in acceptable_conditions]

    for d, p in probabilities.items():
        is_true = (d == true_norm or any(d in a or a in d for a in acceptable_norm))
        y = 1.0 if is_true else 0.0
        score += (p - y) ** 2
    return float(score)


def compute_ece(
    confidences: List[float],
    accuracies: List[bool],
    n_bins: int = 10
) -> float:
    """Compute Expected Calibration Error (ECE).

    Partitions predictions into M equally spaced confidence bins and
    computes weighted average absolute difference between accuracy and confidence.
    """
    if not confidences or len(confidences) != len(accuracies):
        return 0.0

    bins = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    n = len(confidences)

    for i in range(n_bins):
        bin_lower = bins[i]
        bin_upper = bins[i + 1]

        # Find items in bin
        indices = [
            idx for idx, conf in enumerate(confidences)
            if (bin_lower <= conf < bin_upper) or (i == n_bins - 1 and conf == bin_upper)
        ]

        if not indices:
            continue

        bin_size = len(indices)
        bin_acc = sum(1.0 for idx in indices if accuracies[idx]) / bin_size
        bin_conf = sum(confidences[idx] for idx in indices) / bin_size

        ece += (bin_size / n) * abs(bin_acc - bin_conf)

    return float(ece)


def compute_mcnemar_test(
    arm1_correct: List[bool],
    arm2_correct: List[bool]
) -> Dict[str, float]:
    """Compute McNemar's test with Edwards continuity correction.

    Tests null hypothesis that marginal proportions of correct classifications
    are equal between Arm 1 (DEMAT) and Arm 2 (Single-pass).
    """
    assert len(arm1_correct) == len(arm2_correct), "Sample sizes must match"

    b = 0  # Arm 1 correct, Arm 2 incorrect (discordant pairs favoring Arm 1)
    c = 0  # Arm 1 incorrect, Arm 2 correct (discordant pairs favoring Arm 2)

    for a1, a2 in zip(arm1_correct, arm2_correct):
        if a1 and not a2:
            b += 1
        elif not a1 and a2:
            c += 1

    if b + c == 0:
        return {"chi2": 0.0, "p_value": 1.0, "discordant_b": 0, "discordant_c": 0}

    # Edwards continuity correction
    chi2 = ((abs(b - c) - 1.0) ** 2) / (b + c) if (b + c) > 0 else 0.0

    # Approximate p-value from chi2 with 1 degree of freedom:
    # Survival function 1 - erf(sqrt(chi2 / 2))
    p_value = math.erfc(math.sqrt(chi2 / 2.0))

    return {
        "chi2": round(float(chi2), 4),
        "p_value": round(float(p_value), 6),
        "discordant_b": b,
        "discordant_c": c,
    }
