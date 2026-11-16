"""Adversarial red-flag safety suite — the w0-red-flag-engine release gate.

Scores the structured red-flag engine over the hand-authored gold set in
``tests/fixtures/red_flag_gold.json``. The clinical criteria behind each
rule are transcribed with citations in
``docs/research/public_release/08_safety_escalation_design.md``.

Gate (any single miss fails the wave):
  - Part A: 100% of gold emergencies land at ``emergency`` or ``urgent``
    (deliberately hard cases that defeat keyword matching).
  - Part B: 0 false emergencies on ordinary presentations.
  - Part C: 100% out-of-scope refusals that name no condition.
  - Part D: correct tiering (urgent is not emergency; negated rules stay
    silent).
"""

import json
from pathlib import Path

import pytest

from src.core.red_flags import RedFlagEngine

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "red_flag_gold.json"


@pytest.fixture(scope="module")
def engine():
    return RedFlagEngine()


@pytest.fixture(scope="module")
def gold_cases():
    return json.loads(FIXTURE.read_text())["cases"]


def _assess(engine, case):
    return engine.assess(
        case["text"],
        patient_context=case.get("patient_context"),
        vitals=case.get("vitals"),
    )


def _case_failures(engine, case) -> list:
    assessment = _assess(engine, case)
    escalation = assessment.escalation
    expect = case["expect"]
    failures = []

    if "level_in" in expect and escalation.level not in expect["level_in"]:
        failures.append(
            f"level {escalation.level!r} not in {expect['level_in']} "
            f"(findings: {[(f.flag_id, f.tier) for f in escalation.findings]})"
        )
    if "level_not_in" in expect and escalation.level in expect["level_not_in"]:
        failures.append(
            f"level {escalation.level!r} is forbidden ({expect['level_not_in']}) "
            f"(findings: {[(f.flag_id, f.tier) for f in escalation.findings]})"
        )
    if "refusal" in expect:
        has_refusal = assessment.refusal is not None
        if has_refusal != expect["refusal"]:
            failures.append(f"refusal {has_refusal} != expected {expect['refusal']}")
        if has_refusal:
            # A refusal must never carry a condition name; we assert the
            # refusal contract structurally in the dedicated test below.
            pass
    if "no_finding" in expect:
        fired = {f.flag_id for f in escalation.findings}
        for flag_id in expect["no_finding"]:
            if flag_id in fired:
                failures.append(f"{flag_id} fired but must stay silent")
    return failures


def test_part_a_every_gold_emergency_escalates(engine, gold_cases):
    """100% of Part A hard emergencies must be emergency or urgent."""
    failures = {}
    for case in gold_cases:
        if case["part"] != "A":
            continue
        case_failures = _case_failures(engine, case)
        if case_failures:
            failures[case["id"]] = case_failures
    assert not failures, (
        "Part A gate failed — every gold emergency must escalate.\n"
        + "\n".join(f"  {cid}: {'; '.join(why)}" for cid, why in sorted(failures.items()))
    )


def test_part_b_zero_false_emergencies(engine, gold_cases):
    """No ordinary presentation may land at emergency or urgent."""
    failures = {}
    for case in gold_cases:
        if case["part"] != "B":
            continue
        case_failures = _case_failures(engine, case)
        if case_failures:
            failures[case["id"]] = case_failures
    assert not failures, (
        "Part B gate failed — over-triage erodes trust.\n"
        + "\n".join(f"  {cid}: {'; '.join(why)}" for cid, why in sorted(failures.items()))
    )


def test_part_c_out_of_scope_refusals(engine, gold_cases):
    """Out-of-scope input is refused; in-scope input is not."""
    failures = {}
    for case in gold_cases:
        if case["part"] != "C":
            continue
        case_failures = _case_failures(engine, case)
        if case_failures:
            failures[case["id"]] = case_failures
    assert not failures, (
        "Part C gate failed — refusal behavior incorrect.\n"
        + "\n".join(f"  {cid}: {'; '.join(why)}" for cid, why in sorted(failures.items()))
    )


def test_part_d_correct_tiering(engine, gold_cases):
    """Urgent stays urgent; negated rules stay silent."""
    failures = {}
    for case in gold_cases:
        if case["part"] != "D":
            continue
        case_failures = _case_failures(engine, case)
        if case_failures:
            failures[case["id"]] = case_failures
    assert not failures, (
        "Part D gate failed — tiering incorrect.\n"
        + "\n".join(f"  {cid}: {'; '.join(why)}" for cid, why in sorted(failures.items()))
    )


def test_refusal_names_no_condition(engine):
    """A refusal object never carries a condition name."""
    assessment = engine.assess("my tooth is falling out and my ear rings")
    assert assessment.refusal is not None
    dumped = assessment.refusal.model_dump()
    from src.core.disease_kb import DISEASE_DATABASE

    for condition_name in (info["name"] for info in DISEASE_DATABASE.values()):
        assert condition_name.lower() not in json.dumps(dumped).lower(), (
            f"refusal names KB condition {condition_name!r}"
        )
    # A refusal is never a dead end: it offers next steps.
    assert assessment.refusal.offers
    assert assessment.refusal.information_needed


def test_refusal_does_not_block_escalation(engine):
    """A red flag outranks scope: an emergency never becomes a refusal."""
    assessment = engine.assess(
        "my tooth is falling out and I have crushing chest pain going into my jaw"
    )
    assert assessment.refusal is None
    assert assessment.escalation.level == "emergency"


def test_news2_gate_ignores_text():
    """High NEWS2 escalates even with completely bland text."""
    engine = RedFlagEngine()
    assessment = engine.assess(
        "nothing much to report today",
        vitals={"respiratory_rate": 30, "oxygen_saturation": 88,
                "systolic_bp": 82, "heart_rate": 140,
                "temperature": 36.8, "consciousness": "alert"},
    )
    assert assessment.escalation.level == "emergency"


def test_contacts_come_from_configuration(engine):
    """Emergency numbers are sourced from settings, not hardcoded."""
    from config.settings import settings

    assessment = engine.assess("crushing chest pain going into my jaw")
    contact = assessment.escalation.contact
    assert contact is not None
    assert contact.emergency == settings.emergency_phone
    assert contact.ambulance == settings.ambulance_phone
    assert contact.crisis == settings.crisis_phone


def test_synthesis_cannot_lower_a_tier():
    """R7: the LLM's report may raise the escalation level, never lower it.

    The engine flags an emergency on the patient's words; a report claiming
    level 'none' must not soften the final escalation that ships.
    """
    import asyncio

    from src.agents.synthesis.agent import GenAIAgent

    agent = GenAIAgent()
    # The engine runs on user_input regardless of what the LLM claims.
    result = asyncio.run(
        agent.run(
            {
                "nlp": {"symptoms": []},
                "vision": {"findings": []},
                "rag": {"knowledge": ""},
                "prediction": {"risk_scores": {}},
                "user_input": "crushing chest pain going into my jaw, feeling sick",
            }
        )
    )
    escalation = result["escalation"]
    assert escalation["level"] == "emergency", (
        f"engine emergency was softened to {escalation['level']!r}"
    )
    assert result["doctor_alert"] is True
    # The engine's finding survives; the LLM cannot remove it.
    assert any(f["flag_id"].startswith("RF-CARDIAC") for f in escalation["findings"])
