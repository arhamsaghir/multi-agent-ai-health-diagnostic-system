"""Golden assertion harness — the w0-assertion-nlp release gate.

Scores the resolver over the authored 200+-case set in
``tests/fixtures/assertion_golden.json``. A case is correct only if every
expected finding matches BOTH polarity and subject; a symptom missed
entirely counts as incorrect (absent when it should be present). Cases also
fail if the extractor reports an unexpected PRESENT self-reported finding —
the false-positive direction is the dangerous one for triage.

Gate (spec w0-assertion-nlp): >=95% overall, 100% on the no-negation
control category, 100% on the live probe case
("no fever, no cough, no chest pain").
"""

import json
from pathlib import Path

import pytest

from src.agents.nlp.agent import NLPAgent
from src.data.preprocessing.text_preprocessor import TextPreprocessor

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "assertion_golden.json"
LIVE_PROBE = "no fever, no cough, no chest pain"


@pytest.fixture(scope="module")
def agent():
    return NLPAgent()


@pytest.fixture(scope="module")
def preprocessor():
    return TextPreprocessor()


@pytest.fixture(scope="module")
def golden_cases():
    return json.loads(FIXTURE.read_text())["cases"]


def _extract(agent: NLPAgent, preprocessor: TextPreprocessor, text: str):
    """Run the exact production path: preprocess, then assert-resolve."""
    normalized = preprocessor.preprocess(text)["normalized"]
    return agent._extract_symptoms(normalized)


def _case_failures(agent, preprocessor, case) -> list:
    findings = _extract(agent, preprocessor, case["text"])
    by_symptom: dict = {}
    for f in findings:
        by_symptom.setdefault(f["symptom"], []).append(f)

    failures = []
    for exp in case["expected"]:
        candidates = by_symptom.get(exp["symptom"], [])
        if not candidates:
            failures.append(
                f"missed {exp['symptom']!r} entirely (expected "
                f"{exp['polarity']}/{exp['subject']})"
            )
            continue
        if not any(
            f["polarity"] == exp["polarity"] and f["subject"] == exp["subject"]
            for f in candidates
        ):
            actual = [(f["polarity"], f["subject"]) for f in candidates]
            failures.append(
                f"{exp['symptom']!r} expected {exp['polarity']}/{exp['subject']}, "
                f"got {actual}"
            )

    # Safety direction: nothing may be reported present + self unless the
    # case expects it.
    expected_present = {
        e["symptom"]
        for e in case["expected"]
        if e["polarity"] == "present" and e["subject"] == "self"
    }
    for f in findings:
        if (
            f["polarity"] == "present"
            and f["subject"] == "self"
            and f["symptom"] not in expected_present
        ):
            failures.append(f"false-present {f['symptom']!r} ({f['rule']})")
    return failures


def test_golden_harness_gate(agent, preprocessor, golden_cases):
    """>=95% polarity+subject across the whole authored set."""
    failures = {}
    for case in golden_cases:
        case_failures = _case_failures(agent, preprocessor, case)
        if case_failures:
            failures[case["id"]] = case_failures

    total = len(golden_cases)
    correct = total - len(failures)
    ratio = correct / total
    detail = "\n".join(
        f"  {cid}: {'; '.join(why)}" for cid, why in sorted(failures.items())
    )
    assert ratio >= 0.95, (
        f"Golden harness gate failed: {correct}/{total} = {ratio:.1%} (< 95%). "
        f"Failures:\n{detail}"
    )


def test_golden_control_set_perfect(agent, preprocessor, golden_cases):
    """Every plain affirmative case must resolve exactly — no exceptions."""
    failures = {}
    for case in golden_cases:
        if case["category"] != "no_negation_control":
            continue
        case_failures = _case_failures(agent, preprocessor, case)
        if case_failures:
            failures[case["id"]] = case_failures
    assert not failures, (
        f"Control set must be 100% correct. Failures:\n"
        + "\n".join(f"  {cid}: {'; '.join(why)}" for cid, why in sorted(failures.items()))
    )


def test_live_probe_case_flips(agent, preprocessor):
    """The case that motivated the module: all three symptoms absent."""
    findings = _extract(agent, preprocessor, LIVE_PROBE)
    present = [f for f in findings if f["polarity"] == "present"]
    by_symptom = {f["symptom"]: f["polarity"] for f in findings}
    assert not present, f"Live probe must yield zero present findings, got {present}"
    for symptom in ("fever", "cough", "chest pain"):
        assert by_symptom.get(symptom) == "absent", (
            f"{symptom} must be extracted as absent, got {by_symptom.get(symptom)!r}"
        )


def test_conjunction_scope(agent, preprocessor):
    """"no fever but I have a bad cough" — fever absent, cough present."""
    by_symptom = {
        f["symptom"]: f["polarity"]
        for f in _extract(agent, preprocessor, "no fever but I have a bad cough")
    }
    assert by_symptom.get("fever") == "absent"
    assert by_symptom.get("cough") == "present"


def test_family_mention_stays_out_of_triage_belief():
    """"my mother has diabetes" must not raise diabetes in the prior belief."""
    from src.core.demat import DEMATEngine

    engine = DEMATEngine()
    belief, _ = engine.compute_initial_belief("my mother has diabetes")
    uniform = 1.0 / len(belief)
    # With the family clause excluded, no symptom evidence scored: the
    # belief stays at the smoothed baseline for every disease.
    assert max(belief.values()) <= uniform * 1.05, (
        f"family mention leaked into triage belief: {belief}"
    )


def test_probe_belief_differs_from_unnegated():
    """compute_initial_belief reflects the filtered symptom set."""
    from src.core.demat import DEMATEngine

    engine = DEMATEngine()
    negated, _ = engine.compute_initial_belief(LIVE_PROBE)
    unnegated, _ = engine.compute_initial_belief("fever, cough, chest pain")
    max_delta = max(abs(negated[d] - unnegated[d]) for d in unnegated)
    assert max_delta > 0.01, (
        "belief for the negated probe must differ from the un-negated text "
        f"(max delta {max_delta:.4f})"
    )
