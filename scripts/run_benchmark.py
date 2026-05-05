"""Phase 3: Benchmark runner — evaluates diagnostic accuracy against 200 synthetic cases.

Computes Top-1 and Top-5 accuracy rates, per-category breakdowns, and generates
a comprehensive benchmark report.
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from frontend.pages.diagnosis import _get_demo_result


# Mapping: benchmark condition names → demo function output condition names
# The demo function returns specific conditions; we need to map them to benchmark ground truth
DEMO_TO_BENCHMARK = {
    # Cardiovascular branch
    "cardiovascular disease": ["Cardiovascular Disease", "Coronary Artery Disease", "Heart Disease"],
    "angina pectoris": ["Angina Pectoris", "Cardiovascular Disease"],
    "hypertension": ["Hypertension", "High Blood Pressure", "Essential Hypertension"],
    # Respiratory branch
    "respiratory infection": ["Respiratory Infection", "Upper Respiratory Infection", "Bronchitis", "URI"],
    "pneumonia": ["Pneumonia", "Community-Acquired Pneumonia", "Bacterial Pneumonia"],
    # Asthma branch
    "asthma": ["Asthma", "Asthma Exacerbation", "Bronchial Asthma"],
    "reactive airway disease": ["Asthma", "Reactive Airway Disease"],
    # Diabetes branch
    "type 2 diabetes": ["Type 2 Diabetes", "Diabetes Mellitus", "Diabetes", "T2DM"],
    "prediabetes": ["Prediabetes", "Type 2 Diabetes"],
    # Neurological branch
    "neurological disorder": ["Neurological Disorder", "Stroke", "Cerebrovascular Disease"],
    "migraine": ["Migraine", "Migraine with Aura", "Chronic Migraine"],
    "transient ischemic attack (tia)": ["Transient Ischemic Attack (TIA)", "Neurological Disorder"],
    # Gastrointestinal branch
    "gerd": ["GERD", "Gastroesophageal Reflux Disease", "Gastroesophageal Reflux", "Acid Reflux"],
    "peptic ulcer disease": ["Peptic Ulcer Disease", "Peptic Ulcer", "Gastric Ulcer"],
    "irritable bowel syndrome (ibs)": ["Irritable Bowel Syndrome (IBS)", "Irritable Bowel Syndrome", "IBS"],
    # Urinary branch
    "urinary tract infection (uti)": ["Urinary Tract Infection (UTI)", "Urinary Tract Infection", "UTI"],
    "cystitis": ["Cystitis", "Urinary Tract Infection (UTI)"],
    # Dermatological branch
    "eczema": ["Eczema", "Atopic Dermatitis"],
    "contact dermatitis": ["Contact Dermatitis", "Dermatitis"],
    # Musculoskeletal branch
    "osteoarthritis": ["Osteoarthritis", "Degenerative Joint Disease"],
    "rheumatoid arthritis": ["Rheumatoid Arthritis", "RA"],
    # Psychiatric branch
    "anxiety disorder": ["Anxiety Disorder", "Generalized Anxiety Disorder", "GAD"],
    "depression": ["Depression", "Major Depressive Disorder", "Clinical Depression"],
    # Default/mild
    "upper respiratory infection": ["Upper Respiratory Infection", "Common Cold", "URI"],
}


def normalize_condition(name: str) -> str:
    """Normalize condition name for comparison."""
    return name.lower().strip().replace("-", " ").replace("_", " ").strip()


def get_acceptable_for_demo_condition(demo_condition: str) -> list[str]:
    """Get all acceptable benchmark condition names for a demo output condition."""
    key = normalize_condition(demo_condition)
    if key in DEMO_TO_BENCHMARK:
        return DEMO_TO_BENCHMARK[key]
    # Fallback: the demo condition name itself is acceptable
    return [demo_condition]


def is_match(predicted: str, acceptable: list[str]) -> bool:
    """Check if a predicted condition matches any acceptable ground truth."""
    pred_norm = normalize_condition(predicted)
    for acc in acceptable:
        acc_norm = normalize_condition(acc)
        if pred_norm == acc_norm:
            return True
        # Partial match: e.g., "Respiratory Infection" matches "Upper Respiratory Infection"
        if pred_norm in acc_norm or acc_norm in pred_norm:
            return True
    return False


def run_benchmark(cases_path: str = "data/benchmark_cases.json") -> dict:
    """Run the full benchmark suite."""
    with open(cases_path) as f:
        cases = json.load(f)

    print(f"Loaded {len(cases)} benchmark cases")
    print("=" * 60)

    results = []
    category_stats = {}
    severity_stats = {}
    start_time = time.time()

    top1_correct = 0
    top3_correct = 0
    top5_correct = 0
    total = len(cases)

    for i, case in enumerate(cases):
        case_id = case["case_id"]
        ground_truth = case["ground_truth"]
        acceptable = ground_truth["acceptable_conditions"]
        category = case["category"]
        severity = ground_truth["severity"]

        # Run diagnosis through demo function
        result = _get_demo_result(case["symptom_text"], case.get("patient_history", {}))

        if result is None:
            # No matching branch — record as miss
            case_result = {
                "case_id": case_id,
                "category": category,
                "severity": severity,
                "symptom_text": case["symptom_text"],
                "ground_truth": ground_truth["primary_condition"],
                "acceptable_conditions": acceptable,
                "predicted_conditions": [],
                "top1_match": False,
                "top3_match": False,
                "top5_match": False,
                "severity_match": False,
                "predicted_severity": "unknown",
                "confidence": 0,
            }
            results.append(case_result)

            if category not in category_stats:
                category_stats[category] = {"top1": 0, "top3": 0, "top5": 0, "total": 0, "severity_match": 0}
            category_stats[category]["total"] += 1

            if severity not in severity_stats:
                severity_stats[severity] = {"top1": 0, "top3": 0, "top5": 0, "total": 0}
            severity_stats[severity]["total"] += 1

            continue

        diagnoses = result.get("diagnosis", [])

        # Extract predicted conditions
        predicted_conditions = [d.get("condition", "") for d in diagnoses]

        # Top-1: first predicted condition matches any acceptable
        top1_hit = False
        if predicted_conditions and is_match(predicted_conditions[0], acceptable):
            top1_correct += 1
            top1_hit = True

        # Top-3: any of first 3 predictions match
        top3_hit = False
        for pred in predicted_conditions[:3]:
            if is_match(pred, acceptable):
                top3_correct += 1
                top3_hit = True
                break

        # Top-5: any of first 5 predictions match
        top5_hit = False
        for pred in predicted_conditions[:5]:
            if is_match(pred, acceptable):
                top5_correct += 1
                top5_hit = True
                break

        # Severity match
        predicted_severity = result.get("severity", "unknown")
        severity_match = predicted_severity == severity

        # Store result
        case_result = {
            "case_id": case_id,
            "category": category,
            "severity": severity,
            "symptom_text": case["symptom_text"],
            "ground_truth": ground_truth["primary_condition"],
            "acceptable_conditions": acceptable,
            "predicted_conditions": predicted_conditions,
            "top1_match": top1_hit,
            "top3_match": top3_hit,
            "top5_match": top5_hit,
            "severity_match": severity_match,
            "predicted_severity": predicted_severity,
            "confidence": result.get("confidence_score", 0),
        }
        results.append(case_result)

        # Category stats
        if category not in category_stats:
            category_stats[category] = {"top1": 0, "top3": 0, "top5": 0, "total": 0, "severity_match": 0}
        category_stats[category]["total"] += 1
        if top1_hit:
            category_stats[category]["top1"] += 1
        if top3_hit:
            category_stats[category]["top3"] += 1
        if top5_hit:
            category_stats[category]["top5"] += 1
        if severity_match:
            category_stats[category]["severity_match"] += 1

        # Severity stats
        if severity not in severity_stats:
            severity_stats[severity] = {"top1": 0, "top3": 0, "top5": 0, "total": 0}
        severity_stats[severity]["total"] += 1
        if top1_hit:
            severity_stats[severity]["top1"] += 1
        if top3_hit:
            severity_stats[severity]["top3"] += 1
        if top5_hit:
            severity_stats[severity]["top5"] += 1

        # Progress
        if (i + 1) % 25 == 0 or (i + 1) == total:
            elapsed = time.time() - start_time
            print(f"  Processed {i+1}/{total} cases ({elapsed:.1f}s)")

    elapsed = time.time() - start_time

    # Compute overall metrics
    overall = {
        "top1_accuracy": top1_correct / total if total > 0 else 0,
        "top3_accuracy": top3_correct / total if total > 0 else 0,
        "top5_accuracy": top5_correct / total if total > 0 else 0,
        "total_cases": total,
        "top1_correct": top1_correct,
        "top3_correct": top3_correct,
        "top5_correct": top5_correct,
        "elapsed_seconds": round(elapsed, 2),
    }

    # Per-category accuracy
    for cat in category_stats:
        stats = category_stats[cat]
        stats["top1_accuracy"] = round(stats["top1"] / stats["total"], 4) if stats["total"] > 0 else 0
        stats["top3_accuracy"] = round(stats["top3"] / stats["total"], 4) if stats["total"] > 0 else 0
        stats["top5_accuracy"] = round(stats["top5"] / stats["total"], 4) if stats["total"] > 0 else 0
        stats["severity_accuracy"] = round(stats["severity_match"] / stats["total"], 4) if stats["total"] > 0 else 0

    # Per-severity accuracy
    for sev in severity_stats:
        stats = severity_stats[sev]
        stats["top1_accuracy"] = round(stats["top1"] / stats["total"], 4) if stats["total"] > 0 else 0
        stats["top3_accuracy"] = round(stats["top3"] / stats["total"], 4) if stats["total"] > 0 else 0
        stats["top5_accuracy"] = round(stats["top5"] / stats["total"], 4) if stats["total"] > 0 else 0

    return {
        "overall": overall,
        "category_stats": category_stats,
        "severity_stats": severity_stats,
        "case_results": results,
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "model": "Demo Mode (Rule-based Symptom Matching)",
            "total_cases": total,
        },
    }


def print_report(benchmark: dict):
    """Print a formatted benchmark report."""
    overall = benchmark["overall"]

    print("\n" + "=" * 60)
    print("BENCHMARK RESULTS — Multi-Agent AI Health Diagnostic System")
    print("=" * 60)

    print(f"\nOverall Accuracy ({overall['total_cases']} cases, {overall['elapsed_seconds']}s):")
    print(f"  Top-1 Accuracy: {overall['top1_accuracy']*100:.1f}% ({overall['top1_correct']}/{overall['total_cases']})")
    print(f"  Top-3 Accuracy: {overall['top3_accuracy']*100:.1f}% ({overall['top3_correct']}/{overall['total_cases']})")
    print(f"  Top-5 Accuracy: {overall['top5_accuracy']*100:.1f}% ({overall['top5_correct']}/{overall['total_cases']})")

    print("\n" + "-" * 60)
    print("Per-Category Accuracy:")
    print("-" * 60)
    print(f"{'Category':<20} {'Top-1':>8} {'Top-3':>8} {'Top-5':>8} {'Sev':>6} {'Cases':>6}")
    print("-" * 60)

    for cat in sorted(benchmark["category_stats"].keys()):
        stats = benchmark["category_stats"][cat]
        print(f"{cat:<20} {stats['top1_accuracy']*100:>7.1f}% {stats['top3_accuracy']*100:>7.1f}% {stats['top5_accuracy']*100:>7.1f}% {stats.get('severity_accuracy', 0)*100:>5.1f}% {stats['total']:>5}")

    print("\n" + "-" * 60)
    print("Per-Severity Accuracy:")
    print("-" * 60)
    print(f"{'Severity':<15} {'Top-1':>8} {'Top-3':>8} {'Top-5':>8} {'Cases':>6}")
    print("-" * 60)

    for sev in sorted(benchmark["severity_stats"].keys()):
        stats = benchmark["severity_stats"][sev]
        print(f"{sev:<15} {stats['top1_accuracy']*100:>7.1f}% {stats['top3_accuracy']*100:>7.1f}% {stats['top5_accuracy']*100:>7.1f}% {stats['total']:>5}")

    print("\n" + "=" * 60)

    # Show failed cases (Top-1 misses)
    misses = [r for r in benchmark["case_results"] if not r["top1_match"]]
    if misses:
        print(f"\nTop-1 Misses ({len(misses)} cases):")
        print("-" * 60)
        for m in misses[:15]:  # Show first 15
            print(f"  Case {m['case_id']} [{m['category']}]: '{m['symptom_text'][:60]}...'")
            print(f"    Expected: {m['ground_truth']}")
            print(f"    Got:      {m['predicted_conditions'][:3]}")
        if len(misses) > 15:
            print(f"  ... and {len(misses) - 15} more")

    print("=" * 60)


def save_report(benchmark: dict, output_path: str = "data/benchmark_results.json"):
    """Save full benchmark results to JSON."""
    with open(output_path, "w") as f:
        json.dump(benchmark, f, indent=2)

    print(f"\nFull results saved to: {output_path}")


if __name__ == "__main__":
    print("Running Phase 3 Benchmark...")
    benchmark = run_benchmark()
    print_report(benchmark)
    save_report(benchmark)
