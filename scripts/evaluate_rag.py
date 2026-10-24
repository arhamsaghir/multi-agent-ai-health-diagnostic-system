"""Evaluate top-5 RAG retrieval against a fixed 25-query smoke set."""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.agents.rag.agent import RAGAgent

QUERIES = [
    ("cough fever dyspnea", "respiratory"), ("productive cough pneumonia", "respiratory"),
    ("wheezing asthma night", "respiratory"), ("runny nose sore throat", "respiratory"),
    ("pleuritic chest pain infection", "respiratory"), ("headache photophobia", "neurological"),
    ("tension headache bilateral", "neurological"), ("migraine nausea", "neurological"),
    ("sudden severe headache red flags", "neurological"), ("headache differential", "neurological"),
    ("diarrhea vomiting dehydration", "gastrointestinal"), ("acute gastroenteritis", "gastrointestinal"),
    ("abdominal pain nausea", "gastrointestinal"), ("oral rehydration", "gastrointestinal"),
    ("foodborne illness", "gastrointestinal"), ("polyuria polydipsia", "endocrine"),
    ("diabetes HbA1c", "endocrine"), ("diabetes lifestyle", "endocrine"),
    ("hyperglycemia fatigue", "endocrine"), ("metformin first line", "endocrine"),
    ("chest pressure troponin ECG", "cardiovascular"), ("acute coronary syndrome", "cardiovascular"),
    ("hypertension blood pressure", "cardiovascular"), ("cardiovascular risk factors", "cardiovascular"),
    ("heart disease prevention", "cardiovascular"),
]


def evaluate() -> dict:
    agent = RAGAgent()
    rows = []
    hits = 0
    for query, category in QUERIES:
        result = asyncio.run(agent.run({"query": query}))
        docs = result.get("relevant_docs", [])[:5]
        hit = any(doc.get("category") == category for doc in docs)
        hits += int(hit)
        rows.append({"query": query, "expected_category": category, "hit": hit, "sources": [d.get("source") for d in docs]})
    report = {"queries": len(QUERIES), "hits": hits, "top5_hit_rate": hits / len(QUERIES), "rows": rows}
    Path("data/knowledge/guidelines/rag_eval.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    report = evaluate()
    print(json.dumps({k: report[k] for k in ("queries", "hits", "top5_hit_rate")}))
