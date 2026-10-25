"""Phase 2 RAG corpus integrity and retrieval contract tests."""

import json
from pathlib import Path


def test_curated_corpus_has_500_unique_provenance_bearing_records():
    path = Path("data/knowledge/guidelines/corpus.json")
    records = json.loads(path.read_text())
    assert len(records) >= 500
    assert len({record["id"] for record in records}) == len(records)
    assert all(record.get("content") for record in records)
    assert all(record.get("source") for record in records)
    assert all(record.get("source_url") for record in records)
    assert all(record.get("last_reviewed") for record in records)


def test_curated_corpus_covers_multiple_clinical_categories():
    records = json.loads(Path("data/knowledge/guidelines/corpus.json").read_text())
    categories = {record["category"] for record in records}
    assert len(categories) >= 5


def test_rag_result_preserves_citation_metadata(monkeypatch, tmp_path):
    from src.agents.rag.agent import RAGAgent

    agent = object.__new__(RAGAgent)
    agent.documents = ["A cited guideline passage"]
    agent.metadata = [{
        "source": "WHO Guidelines",
        "source_url": "https://www.who.int/publications/guidelines",
        "last_reviewed": "2026-10-05",
        "category": "respiratory",
    }]
    agent.faiss_index = object()

    class _Index:
        def search(self, query_embedding, count):
            import numpy as np
            return np.array([[0.2]], dtype="float32"), np.array([[0]], dtype="int64")

    agent.faiss_index = _Index()
    class _Embedder:
        def encode(self, text):
            import numpy as np
            return np.zeros(4, dtype="float32")
    agent._embedder = _Embedder()
    result = agent._search_faiss("respiratory symptoms", top_k=1)
    assert result[0]["source"] == "WHO Guidelines"
    assert result[0]["source_url"].startswith("https://")
    assert result[0]["last_reviewed"] == "2026-10-05"
