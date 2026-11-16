"""Structured escalation objects (w0-red-flag-engine R6).

The ``doctor_alert`` boolean collapsed structured safety risk into one bit.
These models carry the full picture: a tier level, every finding that fired
(each with its own tier, reason, evidence, and clinical source), ordered
action-first steps, and jurisdiction-correct emergency contacts.

The shape is bounded (a fixed vocabulary of tiers) but unbounded in count —
a response may carry any number of findings across any number of tiers.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field

EscalationLevel = Literal["none", "caution", "urgent", "emergency"]
EscalationTier = Literal["emergency", "urgent", "caution", "informational"]

# Higher number = more severe; used for max()/comparisons.
TIER_SEVERITY: dict[str, int] = {
    "informational": 0,
    "caution": 1,
    "urgent": 2,
    "emergency": 3,
}

LEVEL_SEVERITY: dict[str, int] = {
    "none": 0,
    "caution": 1,
    "urgent": 2,
    "emergency": 3,
}

TIER_TO_LEVEL: dict[str, str] = {
    "emergency": "emergency",
    "urgent": "urgent",
    "caution": "caution",
    "informational": "none",
}


class EscalationContact(BaseModel):
    """Jurisdiction-correct emergency contacts, sourced from configuration."""

    jurisdiction: str = "IN"
    emergency: str = "112"
    ambulance: str = "108"
    crisis: str = "14416"  # Tele-MANAS (India national tele-mental-health)

    def as_phone_map(self) -> dict[str, str]:
        return {
            "emergency": self.emergency,
            "ambulance": self.ambulance,
            "crisis": self.crisis,
        }


class EscalationFinding(BaseModel):
    """One fired red flag, with the reason it fired and the evidence."""

    flag_id: str
    tier: EscalationTier
    reason: str
    evidence: str
    source: str = ""


class Escalation(BaseModel):
    """The structured, authoritative escalation object.

    Computed by the deterministic engine before synthesis. The LLM may
    tighten wording but may not lower the level, remove a finding, or add
    one the engine did not produce (enforced in the synthesis step).
    """

    level: EscalationLevel = "none"
    findings: list[EscalationFinding] = Field(default_factory=list)
    rationale: str = ""
    actions: list[str] = Field(default_factory=list)
    contact: Optional[EscalationContact] = None

    def merge(self, other: "Escalation") -> "Escalation":
        """Combine two escalations, never lowering the level.

        Findings are unioned by flag_id (self wins on conflict); actions
        come from whichever side carried the higher level.
        """
        level = max((self.level, other.level), key=lambda lv: LEVEL_SEVERITY[lv])
        by_id = {f.flag_id: f for f in self.findings}
        for f in other.findings:
            by_id.setdefault(f.flag_id, f)
        ordered = sorted(
            by_id.values(), key=lambda f: TIER_SEVERITY[f.tier], reverse=True
        )
        actions = (
            self.actions if LEVEL_SEVERITY[self.level] >= LEVEL_SEVERITY[other.level]
            else other.actions
        )
        return Escalation(
            level=level,
            findings=ordered,
            rationale=self.rationale or other.rationale,
            actions=actions,
            contact=self.contact or other.contact,
        )


class OutOfScopeRefusal(BaseModel):
    """A first-class refusal to name a condition (w0-red-flag-engine R5).

    Never a dead end: still reports any red flags found, states what
    information would help, offers the clarifying-question path, and routes
    to a clinician. No condition name is permitted on a refusal.
    """

    reason: str
    escalation: Escalation
    information_needed: list[str] = Field(default_factory=list)
    offers: list[str] = Field(default_factory=list)
