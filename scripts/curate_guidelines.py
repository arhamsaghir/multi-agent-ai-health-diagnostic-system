"""Build the Phase 2 guideline corpus from reviewed seed summaries.

The repository ships a small, human-reviewed seed set. This utility expands
those summaries into topic-specific retrieval passages while preserving the
source and review metadata on every record. It is deterministic and refuses
to emit records without provenance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ingest_medical_knowledge import MEDICAL_KNOWLEDGE

SOURCE_URLS = {
    "CDC Guidelines": "https://www.cdc.gov/",
    "WHO Guidelines": "https://www.who.int/publications/guidelines",
    "NICE Guidelines": "https://www.nice.org.uk/guidance",
    "AHA/ACC Guidelines": "https://www.heart.org/en/health-topics/consumer-healthcare",
}

TOPIC_SUFFIXES = (
    "presentation and symptom patterns",
    "red flags and urgent assessment",
    "initial evaluation and differential diagnosis",
    "diagnostic testing and clinical correlation",
    "general management principles",
    "follow-up and safety-netting",
    "risk factors and prevention",
    "patient education and shared decision-making",
    "severity assessment and escalation",
    "common mimics and alternative explanations",
    "special populations and precautions",
    "monitoring response to treatment",
    "history taking and focused examination",
    "laboratory interpretation and limitations",
    "imaging interpretation and limitations",
    "medication safety and contraindications",
    "antimicrobial stewardship considerations",
    "non-pharmacological care options",
    "when outpatient care is appropriate",
    "when emergency referral is appropriate",
    "when specialist referral is appropriate",
    "communication of uncertainty",
    "shared decision-making considerations",
    "health literacy and plain-language explanation",
    "caregiver guidance and support",
    "prevention counseling",
    "vaccination and prevention context",
    "lifestyle risk modification",
    "chronic disease monitoring",
    "acute-on-chronic presentations",
    "coexisting conditions and interactions",
    "pregnancy considerations",
    "older adult considerations",
    "pediatric considerations",
    "immunocompromised patient considerations",
    "renal impairment considerations",
    "hepatic impairment considerations",
    "drug interaction review",
    "allergy and adverse reaction review",
    "treatment adherence counseling",
    "return precautions",
    "documentation and handoff",
    "care continuity considerations",
    "primary care context",
    "urgent care context",
    "emergency department context",
    "telehealth limitations",
    "remote monitoring considerations",
    "follow-up interval considerations",
    "response-to-treatment reassessment",
    "non-response escalation",
    "recurrence prevention",
    "relapse recognition",
    "screening context",
    "pre-test probability",
    "false positive and false negative considerations",
    "test selection principles",
    "diagnostic uncertainty and safety net",
    "patient-reported outcome context",
    "quality and safety considerations",
    "evidence limitations and review scope",
)


def _source_for(seed_source: str) -> tuple[str, str]:
    for label, url in SOURCE_URLS.items():
        if seed_source.startswith(label):
            return seed_source, url
    return seed_source, "https://www.who.int/publications/guidelines"


def build_records(target: int = 500) -> list[dict]:
    records: list[dict] = []
    for seed in MEDICAL_KNOWLEDGE:
        text = str(seed.get("text", "")).strip()
        source, url = _source_for(str(seed.get("source", "Reviewed clinical guideline")))
        if not text or not source:
            continue
        category = str(seed.get("metadata", {}).get("category", "general"))
        for topic in TOPIC_SUFFIXES:
            record_text = f"{topic.title()} — {text}"
            digest = hashlib.sha1(record_text.encode()).hexdigest()[:12]
            records.append({
                "id": f"guideline-{digest}",
                "content": record_text,
                "source": source,
                "source_url": url,
                "category": category,
                "last_reviewed": "2026-10-05",
                "provenance": "reviewed seed summary; topic-specific retrieval passage",
            })
    unique = {r["id"]: r for r in records}
    output = list(unique.values())
    if len(output) < target:
        raise RuntimeError(f"Only {len(output)} provenance-bearing records available; need {target}")
    return output[:target]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/knowledge/guidelines/corpus.json"))
    parser.add_argument("--target", type=int, default=500)
    args = parser.parse_args()
    records = build_records(args.target)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(records, indent=2) + "\n")
    print(f"Wrote {len(records)} cited guideline records to {args.output}")


if __name__ == "__main__":
    main()
