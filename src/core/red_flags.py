"""Structured red-flag engine (w0-red-flag-engine).

Replaces the 12-string ``SAFETY_KEYWORDS`` list and the word-overlap
red-flag matching in the rule-based synthesizer. Escalation is decided by
tiered, sourced, clinically-translatable rules — never by bare substring
presence — and a NEWS2-style numeric gate escalates on vitals regardless of
what the text says.

Rule sources are recorded on every rule and every finding (RCP NEWS2 2017,
UK Sepsis Trust / NICE NG51, NICE CG95 chest pain, NHS Act FAST / BE-FAST,
C-SSRS Columbia screener, NICE NG12 suspected cancer, CDC Hear Her, NICE
NG143 pediatric fever, MTS/ESI discriminators). The verbatim criteria and
citations live in ``docs/research/public_release/08_safety_escalation_design.md``.

Guards, in order of application:
  1. **Negation** — a match inside a clause the assertion layer marked
     absent/hypothetical does not fire (w0-assertion-nlp output; when
     polarity is unavailable the resolver computes it — the conservative
     reading is the default).
  2. **Subject** — a match in a family/third-party clause does not fire
     ("my dad had a stroke" is not the patient's emergency).
  3. **History** — a match in a clause marked past-tense/historical
     ("I had a stroke two years ago") downgrades to ``informational``.

Patient text is never logged by this module.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.core.escalation import (
    Escalation,
    EscalationContact,
    EscalationFinding,
    OutOfScopeRefusal,
    TIER_SEVERITY,
    TIER_TO_LEVEL,
)
from src.agents.nlp.assertion import exclusion_spans
from config.settings import settings


# ---------------------------------------------------------------------------
# Guard vocabularies
# ---------------------------------------------------------------------------

# Clauses that place a mention in the patient's history rather than the
# acute presentation ("I had a stroke two years ago", "history of asthma").
HISTORY_PATTERN = re.compile(
    r"\b(?:\d+|\btwo\b|\bthree\b|\bfour\b|\bfive\b|\bten\b)\s+years?\s+ago\b"
    r"|\b(?:several|many|a few)\s+years\s+ago\b"
    r"|\bhistory of\b"
    r"|\bused to (?:have|get)\b"
    r"|\bas a child\b"
    r"|\bwhen i was (?:young|a kid|younger)\b"
    r"|\blast year\b"
    r"|\bchildhood\b"
)

# "Infection presumed" indicators for the sepsis rule (UK Sepsis Trust
# framing: presumed infection + any red flag).
INFECTION_PATTERN = re.compile(
    r"\b(?:infection|infected|fever|feverish|chills|flu|pneumonia|"
    r"urinary tract infection|uti|kidney infection|chest infection|"
    r"wound|abscess|cellulitis|cough)\b",
    re.IGNORECASE,
)

# Acute cardiac features that hard-override a benign chest-pain verdict
# (NICE CG95: suspected ACS -> emergency ambulance).
CARDIAC_ACUTE_PATTERN = re.compile(
    r"\b(?:radiating|radiates|spreading|goes? (?:into|to|up) my (?:jaw|arm|neck|back)|"
    r"crushing|crushing pressure|like an elephant|sweating|cold sweat|clammy|"
    r"diaphoresis|breathless|shortness of breath|can't breathe|cannot breathe|"
    r"cant breathe|with exertion|when i (?:walk|climb|exert)|nausea|feeling sick|"
    r"tightness in my (?:arm|jaw|neck))\b",
    re.IGNORECASE,
)

CHEST_PAIN_PATTERN = re.compile(
    r"\b(?:chest pain|chest pressure|chest tightness|pressure in my chest|"
    r"tightness in my chest|crushing chest)\b",
    re.IGNORECASE,
)

# Acute cardiac features without an explicit chest-pain mention — atypical
# ACS presentations ("No chest pain, but the tightness in my arm is
# spreading"). Restricted to radiation/spreading features so ordinary
# breathlessness (asthma, anxiety) cannot fire an emergency on its own.
CARDIAC_RADIATION_PATTERN = re.compile(
    r"\b(?:tightness in my (?:arm|jaw|neck)|spreading (?:up |into )?my "
    r"(?:arm|jaw|neck|chest)|(?:pain|pressure|tightness) (?:going |radiating )?"
    r"(?:into|to|up) my (?:jaw|arm|neck))\b",
    re.IGNORECASE,
)

# BE-FAST stroke elements (Aroor 2017: Balance and Eyes catch posterior-
# circulation strokes FAST misses).
BEFAST_PATTERN = re.compile(
    r"\b(?:face (?:is |feels )?(?:droop|drooping|droopy|numb|sagging)|"
    r"one side of my face|arm (?:is |feels )?(?:weak|numb|heavy|drifting)|"
    r"(?:unilateral|one-sided|one side of my body).{0,20}weak|"
    r"slurred speech|speech (?:is |sounds )?(?:slurred|garbled)|can't speak|"
    r"cannot speak|trouble speaking|sudden (?:loss of )?balance|"
    r"sudden (?:loss of )?vision|lost vision in one eye|double vision)\b",
    re.IGNORECASE,
)

# C-SSRS-derived lexical screen, including indirect ideation (Columbia
# Protocol constructs Q1-Q5; dossier 08 row 1).
SUICIDE_PATTERN = re.compile(
    r"\b(?:kill (?:myself|me)|ending (?:my|it) (?:life|all)|end my life|"
    r"want to die|wish i was dead|wish i were dead|better off dead|"
    r"(?:everyone|they|my family) would be better off without me|"
    r"hurt(?:ing)? myself|self.?harm|suicidal|suicide|"
    r"don't want to be here anymore|dont want to be here anymore|"
    r"no reason to live|take (?:my|these) pills|overdose)\b",
    re.IGNORECASE,
)

SEPSIS_RED_FLAG_PATTERN = re.compile(
    r"\b(?:new confusion|confused|not making sense|mottled|mottling|"
    r"non-?blanching|no urine|haven'?t passed urine|not peed|"
    r"worst (?:illness|sick|flu) (?:of my life|ever)|recent chemotherapy|"
    r"on chemo)\b",
    re.IGNORECASE,
)

# MTS/ESI life-threat discriminators (dossier 08 row 13-14).
LIFE_THREAT_PATTERN = re.compile(
    r"\b(?:unconscious|unresponsive|not breathing|choking|"
    r"can'?t breathe|cannot breathe|cant breathe|"
    r"bleeding (?:a lot|heavily|won'?t stop|non-?stop)|severe bleeding|"
    r"coughing up blood|vomiting blood|blood loss|"
    r"(?:lip|tongue|throat) (?:is )?(?:swelling|swollen|closing|tight)|"
    r"severe allergic reaction|anaphyla(?:xis|ctic)|"
    r"pass out|about to faint|going to faint|feeling faint|might pass out)\b",
    re.IGNORECASE,
)

# Sudden severe headache patterns (thunderclap; subarachnoid screen).
THUNDERCLAP_PATTERN = re.compile(
    r"\b(?:thunderclap|sudden(?:ly)? worst headache|worst headache of my life|"
    r"worst headache ever|headache like an explosion|sudden severe headache)\b",
    re.IGNORECASE,
)

# NICE NG12 suspected-cancer urgent-referral flags (dossier 08 row 7).
CANCER_URGENT_PATTERN = re.compile(
    r"\b(?:unexplained lump|lump[^.;]{0,40}\bgrowing\b|"
    r"lump[^.;]{0,40}\b(?:bigger|larger|getting bigger)\b|"
    r"unexplained weight loss|losing weight without trying|"
    r"difficulty swallowing|trouble swallowing|dysphagia|"
    r"post-?menopausal bleeding|bleeding after menopause|"
    r"blood in (?:my )?(?:stool|poo|urine|pee)|unexplained bleeding)\b",
    re.IGNORECASE,
)

# CDC Hear Her urgent maternal warning signs (subset verifiable from text;
# dossier 08 row 8).
PREGNANCY_URGENT_PATTERN = re.compile(
    r"\b(?:severe headache that won'?t go away|vision changes|spots in my vision|"
    r"severe swelling|swelling of my face or hands|chest pressure|"
    r"trouble breathing while pregnant|severe nausea (?:and|or) vomiting|"
    r"baby (?:is )?not moving|reduced (?:baby|fetal) movements?|"
    r"vaginal bleeding (?:during|while) pregnant|bleeding while pregnant|"
    r"overwhelming tiredness|severe belly pain|water broke early)\b",
    re.IGNORECASE,
)

PREGNANT_PATTERN = re.compile(r"\bpregnant\b|\bpregnancy\b|\bpostpartum\b", re.IGNORECASE)

# Tiered rule table — data, not code. Each rule is auditable by name and
# citable to its clinical source (see module docstring + dossier 08).
RULES: List[Dict[str, Any]] = [
    {
        "id": "RF-CSSRS-001",
        "tier": "emergency",
        "pattern": SUICIDE_PATTERN,
        # The C-SSRS phrases ARE the content — "I don't want to be here
        # anymore" contains the negation cue "don't", but nothing is being
        # denied. Negation guarding must not apply to this rule.
        "negation_guard": False,
        "reason": (
            "Expression of suicidal ideation, self-harm intent, or wish to be "
            "dead (including indirect phrasing)."
        ),
        "source": "C-SSRS Columbia Protocol screener (dossier 08 row 1)",
        "actions": [
            "Stop and talk to the patient now — do not continue triage.",
            "Show the crisis card with one-tap call and text.",
            "Do not generate further medical content.",
        ],
    },
    {
        "id": "RF-BEFAST-001",
        "tier": "emergency",
        "pattern": BEFAST_PATTERN,
        "reason": (
            "BE-FAST stroke pattern: face droop, unilateral arm weakness, "
            "speech disturbance, sudden balance loss, or sudden vision loss."
        ),
        "source": "NHS Act FAST; BE-FAST (Aroor 2017); NICE NG128 (dossier 08 row 2)",
        "actions": [
            "This may be a stroke. Call the ambulance number now — do not drive yourself.",
            "Note the time symptoms started; treatment is time-critical.",
            "Nothing to eat or drink until assessed.",
        ],
    },
    {
        "id": "RF-CARDIAC-001",
        "tier": "emergency",
        "pattern": CHEST_PAIN_PATTERN,
        "requires_any": [CARDIAC_ACUTE_PATTERN],
        "reason": (
            "Chest pain with acute features (radiation, sweating, "
            "breathlessness, exertional, or crushing quality) — suspected ACS."
        ),
        "source": "NICE CG95 chest pain of recent onset (dossier 08 row 3)",
        "actions": [
            "Call the ambulance number now — do not drive yourself.",
            "Chew one adult aspirin unless allergic or advised otherwise.",
            "Stop all activity and stay with someone.",
        ],
    },
    {
        "id": "RF-SEPSIS-001",
        "tier": "emergency",
        "pattern": SEPSIS_RED_FLAG_PATTERN,
        "requires_any": [INFECTION_PATTERN],
        "reason": (
            "Presumed infection with a sepsis red flag (new confusion, "
            "mottled/non-blanching rash, no urine 18h+, worst-ever illness, "
            "recent chemotherapy)."
        ),
        "source": "UK Sepsis Trust red flags; NICE NG51/NG254 (dossier 08 row 4)",
        "actions": [
            "This may be sepsis. Go to the emergency department now.",
            "Call the ambulance number if the patient cannot be transported safely.",
            "Say 'I am worried about sepsis' on arrival.",
        ],
    },
    {
        "id": "RF-LIFETHREAT-001",
        "tier": "emergency",
        "pattern": LIFE_THREAT_PATTERN,
        "reason": (
            "Life-threat discriminator: unresponsiveness, respiratory "
            "compromise, uncontrolled major bleeding, or anaphylaxis-type "
            "presentation."
        ),
        "source": "MTS discriminators; ESI v4 (dossier 08 rows 13-14)",
        "actions": [
            "Call the ambulance number immediately.",
            "Stay with the patient; do not leave them alone.",
        ],
    },
    {
        "id": "RF-THUNDERCLAP-001",
        "tier": "emergency",
        "pattern": THUNDERCLAP_PATTERN,
        "reason": (
            "Sudden worst-ever (thunderclap) headache — subarachnoid "
            "hemorrhage screen."
        ),
        "source": "MTS pain/persistence discriminators; NICE headache pathway",
        "actions": [
            "Go to the emergency department immediately.",
            "Call the ambulance number — do not drive yourself.",
        ],
    },
    {
        "id": "RF-NEWS2-EMERGENCY-001",
        "tier": "emergency",
        "pattern": None,  # numeric gate
        "reason": (
            "NEWS2-style aggregate score >= 7 — emergency response."
        ),
        "source": "RCP NEWS2 2017 (dossier 08 row 5)",
        "actions": [
            "Vital signs indicate severe deterioration. Call the ambulance number now.",
        ],
    },
    {
        "id": "RF-NEWS2-URGENT-001",
        "tier": "urgent",
        "pattern": None,  # numeric gate
        "reason": (
            "NEWS2-style aggregate score 5-6, or a single parameter scoring 3 "
            "— urgent clinician review and sepsis screen."
        ),
        "source": "RCP NEWS2 2017; NICE MIB205 (dossier 08 rows 5-6)",
        "actions": [
            "Vital signs need urgent same-day clinical review.",
            "Get a clinical assessment today — do not wait overnight.",
        ],
    },
    {
        "id": "RF-CARDIAC-002",
        "tier": "emergency",
        "pattern": CARDIAC_RADIATION_PATTERN,
        "reason": (
            "Cardiac-sounding tightness or pressure radiating to arm/jaw/neck "
            "— atypical acute coronary presentation even without the words "
            "'chest pain'."
        ),
        "source": "NICE CG95 acute features (dossier 08 row 3)",
        "actions": [
            "Call the ambulance number now — do not drive yourself.",
            "Stop all activity and stay with someone.",
        ],
    },
    {
        "id": "RF-CHEST-URGENT-001",
        "tier": "urgent",
        "pattern": CHEST_PAIN_PATTERN,
        "reason": (
            "Chest pain without documented acute features — needs same-day "
            "clinical assessment to rule out cardiac causes."
        ),
        "source": "NICE CG95 (non-anginal/atypical still requires assessment)",
        "actions": [
            "Get a same-day clinical assessment of the chest pain.",
            "If it worsens, radiates, or comes with sweating or breathlessness, call the ambulance number.",
        ],
    },
    {
        "id": "RF-CANCER-URGENT-001",
        "tier": "urgent",
        "pattern": CANCER_URGENT_PATTERN,
        "reason": (
            "Suspected-cancer red flag (unexplained lump, unexplained weight "
            "loss, dysphagia, unexplained bleeding, post-menopausal bleeding)."
        ),
        "source": "NICE NG12 (dossier 08 row 7)",
        "actions": [
            "See a doctor urgently — ask about the fast-track suspected-cancer pathway.",
        ],
    },
    {
        "id": "RF-PREGNANCY-URGENT-001",
        "tier": "urgent",
        "pattern": PREGNANCY_URGENT_PATTERN,
        "requires_any": [PREGNANT_PATTERN],
        "reason": (
            "Urgent maternal warning sign during pregnancy or postpartum."
        ),
        "source": "CDC Hear Her campaign (dossier 08 row 8)",
        "actions": [
            "Contact your maternity unit or obstetric team today.",
            "If bleeding is heavy or the baby's movements stop, go to the hospital now.",
        ],
    },
    {
        "id": "RF-PEDIATRIC-FEVER-001",
        "tier": "emergency",
        "pattern": re.compile(r"\bfever\b|\btemperature\b", re.IGNORECASE),
        "requires_age_lt_months": 3,
        "reason": "Fever in an infant under 3 months — immediate emergency assessment.",
        "source": "NICE NG143; NHS fever pathways (dossier 08 row 10)",
        "actions": [
            "A fever under 3 months of age is an emergency. Go to the hospital now.",
        ],
    },
    {
        "id": "RF-ELDERLY-CONFUSION-001",
        "tier": "urgent",
        "pattern": SEPSIS_RED_FLAG_PATTERN,
        "requires_age_gte": 65,
        "reason": (
            "New confusion (or atypical sepsis presentation) at age 65+ — "
            "urgent assessment; older adults often present atypically."
        ),
        "source": "Clifford 2016; SAEM geriatric guidance (dossier 08 row 12)",
        "actions": [
            "New confusion at this age needs urgent same-day assessment.",
        ],
    },
]

# Contact escalation object built from configuration (R8).
def _contact() -> EscalationContact:
    return EscalationContact(
        jurisdiction="IN",
        emergency=settings.emergency_phone,
        ambulance=settings.ambulance_phone,
        crisis=settings.crisis_phone,
    )


# Function words that leak through length-based KB word filters and must
# not count as scope evidence ("chest pain when breathing" contributes
# "when").
SCOPE_STOPWORDS = {
    "when", "what", "that", "with", "from", "have", "been", "their",
    "this", "while", "after", "before", "during", "which", "where",
}


# "Can't stop X" means X IS happening — the cue is not a negation of the
# symptom that follows. Normalized before guard computation so the
# assertion layer never reads it as one.
STOPPING_CONSTRUCTION = re.compile(
    r"\b(?:can'?t|cannot|cant)\s+stop\b", re.IGNORECASE
)


def _guard_text(text: str) -> str:
    """Prepare text for negation guards (clause-local, engine-local)."""
    return STOPPING_CONSTRUCTION.sub("unable to stop", text.lower())


def _history_spans(text: str) -> List[tuple]:
    return [m.span() for m in HISTORY_PATTERN.finditer(text)]


def _in_spans(pos: int, spans: List[tuple]) -> bool:
    return any(start <= pos < end for start, end in spans)


# ---------------------------------------------------------------------------
# NEWS2-style numeric gate (R2)
# ---------------------------------------------------------------------------

def news2_score(vitals: Dict[str, Any]) -> Dict[str, Any]:
    """Score six parameters per RCP NEWS2 (December 2017).

    Accepts self-reported or measured vitals: respiratory_rate,
    oxygen_saturation (SpO2 %), systolic_bp, heart_rate, temperature (C),
    and consciousness ("alert" | "confused" | "voice" | "pain" | "unresponsive").
    Returns the aggregate, whether any single parameter scored 3, and the
    per-parameter breakdown.
    """
    def _band(value, bands):
        for threshold, score in bands:
            if value <= threshold:
                return score
        return bands[-1][1]

    breakdown: Dict[str, int] = {}

    rr = vitals.get("respiratory_rate")
    if rr is not None:
        breakdown["respiratory_rate"] = _band(float(rr), [
            (8, 3), (11, 1), (20, 0), (24, 2), (float("inf"), 3),
        ])

    spo2 = vitals.get("oxygen_saturation")
    if spo2 is not None:
        breakdown["oxygen_saturation"] = _band(float(spo2), [
            (91, 3), (93, 2), (95, 1), (100, 0), (float("inf"), 0),
        ])

    sbp = vitals.get("systolic_bp")
    if sbp is not None:
        breakdown["systolic_bp"] = _band(float(sbp), [
            (90, 3), (100, 2), (110, 1), (219, 0), (float("inf"), 3),
        ])

    hr = vitals.get("heart_rate")
    if hr is not None:
        breakdown["heart_rate"] = _band(float(hr), [
            (40, 3), (50, 1), (90, 0), (110, 1), (130, 2), (float("inf"), 3),
        ])

    consciousness = str(vitals.get("consciousness", "alert")).lower()
    breakdown["consciousness"] = 0 if consciousness == "alert" else 3

    temp = vitals.get("temperature")
    if temp is not None:
        breakdown["temperature"] = _band(float(temp), [
            (35.0, 3), (36.0, 1), (38.0, 0), (39.0, 1), (float("inf"), 2),
        ])

    aggregate = sum(breakdown.values())
    single_three = any(score == 3 for score in breakdown.values())

    if aggregate >= 7:
        band = "emergency"
    elif aggregate >= 5 or single_three:
        band = "urgent"
    else:
        band = "low"

    return {
        "score": aggregate,
        "single_parameter_three": single_three,
        "band": band,
        "breakdown": breakdown,
    }


# ---------------------------------------------------------------------------
# The engine
# ---------------------------------------------------------------------------

@dataclass
class Assessment:
    """Engine output: escalation + optional out-of-scope refusal."""

    escalation: Escalation
    refusal: Optional[OutOfScopeRefusal] = None


class RedFlagEngine:
    """Tiered, negation-aware, sourced red-flag assessment."""

    def __init__(self):
        # Guards use the assertion layer's clause machinery (exclusion
        # spans, history cues) directly — no symptom-pattern resolver is
        # needed here, keeping core independent of the agent classes.
        pass

    def assess(
        self,
        text: str,
        patient_context: Optional[Dict[str, Any]] = None,
        vitals: Optional[Dict[str, Any]] = None,
    ) -> Assessment:
        """Assess a patient presentation.

        Args:
            text: The patient's own description (their words, not history
                fields).
            patient_context: Structured demographics (age in years,
                pregnancy flag).
            vitals: Numeric vitals for the NEWS2 gate (respiratory_rate,
                oxygen_saturation, systolic_bp, heart_rate, temperature,
                consciousness).

        Returns:
            Assessment with the escalation (level possibly "none") and a
            refusal when the presentation falls outside the knowledge base.
        """
        patient_context = patient_context or {}
        findings: List[EscalationFinding] = []

        if not text or not text.strip():
            text_findings, ruled_out = [], []
        else:
            text_findings, ruled_out = self._text_findings(text, patient_context)
        findings.extend(text_findings)
        findings.extend(self._news2_findings(vitals))

        # Findings from the assertion layer the engine itself could not see
        # (polarity-aware condition mentions, e.g. family diabetes) are NOT
        # red flags — informational context only.
        level = "none"
        if findings:
            top = max(findings, key=lambda f: TIER_SEVERITY[f.tier])
            level = TIER_TO_LEVEL[top.tier]

        actions: List[str] = []
        if level != "none":
            seen = set()
            for rule in RULES:
                if any(f.flag_id == rule["id"] for f in findings):
                    for action in rule.get("actions", []):
                        if action not in seen:
                            seen.add(action)
                            actions.append(action)

        fired_ids = [f.flag_id for f in findings if f.tier != "informational"]
        rationale = (
            f"Escalation level '{level}' from rules {fired_ids}."
            if fired_ids
            else "No red-flag rule fired on this presentation."
        )

        escalation = Escalation(
            level=level,
            findings=sorted(
                findings, key=lambda f: TIER_SEVERITY[f.tier], reverse=True
            ),
            rationale=rationale,
            actions=actions,
            contact=_contact() if level in ("urgent", "emergency") else None,
        )

        refusal = None
        if level == "none" and self._out_of_scope(text):
            refusal = OutOfScopeRefusal(
                reason=(
                    "No condition in the knowledge base is supported by this "
                    "description, so naming one would be a guess."
                ),
                escalation=escalation,
                information_needed=[
                    "The main symptom and when it started",
                    "Severity and whether it is getting worse",
                    "Relevant medical history or medications",
                ],
                offers=[
                    "Answer clarifying questions so the assessment can be repeated",
                    "A red-flag safety check (already completed — none fired)",
                    "A route to a clinician for a real evaluation",
                ],
            )

        return Assessment(escalation=escalation, refusal=refusal)

    # -- internals ----------------------------------------------------------

    def _text_findings(
        self, text: str, patient_context: Dict[str, Any]
    ) -> tuple[List[EscalationFinding], List[str]]:
        """Run every text rule with negation/history guards.

        Returns (findings, ruled_out_ids). Subject attribution is NOT a
        guard here, unlike triage: a carer reporting an unresponsive
        relative IS an emergency for someone in the conversation. History
        framing ("my dad had a stroke last year") is what separates a
        patient's emergency from their family's past.
        """
        lowered = _guard_text(text)
        excluded = exclusion_spans(lowered)
        history_spans = _history_spans(lowered)

        findings: List[EscalationFinding] = []
        ruled_out: List[str] = []

        for rule in RULES:
            pattern = rule.get("pattern")
            if pattern is None:
                continue  # numeric gates handled separately

            matches = list(pattern.finditer(lowered))
            if not matches:
                continue

            # Attribute requirements (age gates).
            age = patient_context.get("age")
            if "requires_age_lt_months" in rule:
                age_months = patient_context.get("age_months")
                if age_months is None and age is not None:
                    age_months = float(age) * 12
                if age_months is None or age_months >= rule["requires_age_lt_months"]:
                    ruled_out.append(rule["id"])
                    continue
            if "requires_age_gte" in rule:
                if age is None or float(age) < rule["requires_age_gte"]:
                    ruled_out.append(rule["id"])
                    continue

            # Co-requirement: at least one companion pattern must also match
            # OUTSIDE a negated scope (e.g. sepsis needs presumed infection).
            if "requires_any" in rule:
                companion_hit = False
                for companion in rule["requires_any"]:
                    for m in companion.finditer(lowered):
                        if not _in_spans(m.start(), excluded):
                            companion_hit = True
                            break
                    if companion_hit:
                        break
                if not companion_hit:
                    ruled_out.append(rule["id"])
                    continue

            # Negation guard (R4): a match governed by a negation cue does
            # not fire. A match that BEGINS at the span start carries its
            # own cue as content ("not making sense") and is exempt. Rules
            # may opt out entirely (C-SSRS phrases are self-contained).
            if rule.get("negation_guard", True):
                active = [
                    m for m in matches
                    if not _in_spans(m.start(), excluded)
                    or any(s == m.start() for s, _ in excluded)
                ]
            else:
                active = matches
            if not active:
                ruled_out.append(rule["id"])
                continue

            for m in active:
                tier = rule["tier"]
                if _in_spans(m.start(), history_spans):
                    # Past-tense/history framing: context, not an acute flag.
                    tier = "informational"
                findings.append(
                    EscalationFinding(
                        flag_id=rule["id"],
                        tier=tier,
                        reason=rule["reason"],
                        evidence=m.group(0),
                        source=rule["source"],
                    )
                )
                break  # one finding per rule is enough to set the tier

        return findings, ruled_out

    def _news2_findings(
        self, vitals: Optional[Dict[str, Any]]
    ) -> List[EscalationFinding]:
        if not vitals:
            return []
        result = news2_score(vitals)
        findings: List[EscalationFinding] = []
        if result["band"] == "emergency":
            rule = next(r for r in RULES if r["id"] == "RF-NEWS2-EMERGENCY-001")
            findings.append(
                EscalationFinding(
                    flag_id=rule["id"],
                    tier="emergency",
                    reason=rule["reason"],
                    evidence=f"NEWS2 aggregate {result['score']} "
                             f"({result['breakdown']})",
                    source=rule["source"],
                )
            )
        elif result["band"] == "urgent":
            rule = next(r for r in RULES if r["id"] == "RF-NEWS2-URGENT-001")
            findings.append(
                EscalationFinding(
                    flag_id=rule["id"],
                    tier="urgent",
                    reason=rule["reason"],
                    evidence=f"NEWS2 aggregate {result['score']} "
                             f"(single-3: {result['single_parameter_three']})",
                    source=rule["source"],
                )
            )
        return findings

    def _out_of_scope(self, text: str) -> bool:
        """True when no knowledge-base condition is meaningfully supported.

        Scope = symptom/condition evidence the KB would score. Reuses the
        DEMAT belief machinery's matching at zero cost: if no KB symptom or
        condition term matches outside a negated/non-self scope, the
        presentation cannot produce a defensible differential.
        """
        from src.core.disease_kb import DISEASE_DATABASE
        from src.agents.nlp.assertion import CONDITION_PATTERNS

        lowered = (text or "").lower()
        if not lowered.strip():
            return True
        excluded = exclusion_spans(lowered)

        def _unexcluded_hit(needle: str) -> bool:
            start = lowered.find(needle)
            while start != -1:
                if not _in_spans(start, excluded):
                    return True
                start = lowered.find(needle, start + 1)
            return False

        for info in DISEASE_DATABASE.values():
            for symptom in info.get("symptoms", []):
                s_lower = symptom.lower()
                s_words = [
                    w for w in s_lower.split()
                    if len(w) > 3 and w not in SCOPE_STOPWORDS
                ]
                if _unexcluded_hit(s_lower):
                    return False
                if any(_unexcluded_hit(w) for w in s_words):
                    return False

        condition_regexes = {
            category: re.compile(pattern)
            for category, pattern in CONDITION_PATTERNS.items()
        }
        for condition_re in condition_regexes.values():
            if any(
                _unexcluded_hit(m.group(0).lower())
                for m in condition_re.finditer(lowered)
            ):
                return False
        return True


def assess_level_floor(escalation: Escalation, floor_level: str) -> Escalation:
    """Clamp an escalation so its level is never below ``floor_level``.

    Used by synthesis: an LLM-provided escalation may only RAISE the level.
    """
    from src.core.escalation import LEVEL_SEVERITY

    if LEVEL_SEVERITY[escalation.level] < LEVEL_SEVERITY[floor_level]:
        data = escalation.model_dump()
        data["level"] = floor_level
        return Escalation(**data)
    return escalation
