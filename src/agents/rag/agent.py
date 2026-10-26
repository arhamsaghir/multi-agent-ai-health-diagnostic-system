"""RAG Agent — Retrieval-Augmented Generation for medical knowledge.

Uses FAISS + sentence-transformers to retrieve relevant medical literature,
guidelines, and disease information, then synthesizes the retrieved passages
with the configured LLM (OpenRouter/OmniRoute), falling back to the raw
retrieved text when no LLM is reachable.
"""

from typing import Any, Optional
import os
import json
import numpy as np

from src.agents.base import BaseAgent
from src.data.embedding import EmbeddingModel
from src.utils.redaction import safe_error, text_fingerprint
from config import settings


class RAGAgent(BaseAgent):
    """RAG-based medical knowledge retrieval agent."""

    name = "rag_agent"
    description = "FAISS + sentence-transformers — Medical knowledge retrieval and LLM synthesis"

    def __init__(self):
        super().__init__()
        self._embedder = None
        self.faiss_index = None
        self.documents = []
        self.metadata = []
        self.rag_client = None
        self._load_attempted = False
        # Don't load embedding model at init — lazy load on first use
        self._load_store_metadata()

    @property
    def embedder(self):
        """Lazy-load embedding model on first access."""
        if self._embedder is None:
            from src.data.embedding import EmbeddingModel
            self._embedder = EmbeddingModel()
        return self._embedder

    def _load_store_metadata(self):
        """Load FAISS metadata without loading the embedding model."""
        store_dir = settings.vector_store_dir
        os.makedirs(store_dir, exist_ok=True)

        meta_path = os.path.join(store_dir, "medical_knowledge_meta.json")

        try:
            import faiss
            faiss_path = os.path.join(store_dir, "medical_knowledge.faiss")
            if os.path.exists(faiss_path) and os.path.exists(meta_path):
                self.faiss_index = faiss.read_index(faiss_path)
                with open(meta_path, "r") as f:
                    loaded = json.load(f)
                    self.documents = loaded.get("documents", [])
                    self.metadata = loaded.get("metadata", [])
                self.log("info", f"Loaded FAISS index with {len(self.documents)} documents")
            else:
                self.log("info", "No FAISS store found — will use fallback knowledge")
        except Exception as e:
            self.log("error", f"Failed to load FAISS store: {e}")

    def _init_rag_client(self):
        """Initialize the LLM client used for knowledge synthesis."""
        if self.rag_client is not None:
            return
        try:
            from src.llm.openrouter_client import OpenRouterClient
            self.rag_client = OpenRouterClient()
            self.log("info", f"LLM client initialized for RAG synthesis ({self.rag_client.default_model})")
        except Exception as e:
            self.log("warning", f"LLM client not available, using fallback: {safe_error(e)}")
            self.rag_client = None

    async def run(self, input_data: dict) -> dict:
        """Retrieve medical knowledge relevant to the symptoms.

        Args:
            input_data: Dict with 'query' (symptom text) and optional 'symptoms' list.

        Returns:
            Dict with relevant medical documents, disease info, and treatment guidelines.
        """
        # Lazy init RAG client on first use
        self._init_rag_client()

        query = input_data.get("query", "")
        symptoms = input_data.get("symptoms", [])

        if not query and not symptoms:
            return {"error": "No query or symptoms provided", "relevant_docs": [], "knowledge": ""}

        search_query = query or " ".join(symptoms)
        self.log("info", f"RAG retrieval query {text_fingerprint(search_query)}")

        results = []
        knowledge = ""

        if self.faiss_index is not None and len(self.documents) > 0:
            results = self._search_faiss(search_query, top_k=5)
            knowledge = "\n\n".join([r["content"] for r in results[:3]])

        # Fallback: return structured disease knowledge from built-in knowledge base
        if not results:
            results = self._fallback_knowledge(search_query)
            knowledge = results[0].get("content", "") if results else ""

        # Synthesize knowledge with the configured LLM if one is reachable
        if self.rag_client and results:
            try:
                self.log("info", f"Synthesizing RAG results with {self.rag_client.default_model}")
                synthesized = self.rag_client.synthesize_knowledge(search_query, results)
                if synthesized and "Error" not in synthesized[:20]:
                    knowledge = synthesized
            except Exception as e:
                self.log("warning", f"LLM synthesis failed, using raw knowledge: {safe_error(e, search_query)}")

        return {
            "relevant_docs": results,
            "knowledge": knowledge,
            "num_sources": len(results),
            "query": search_query,
            "agent": self.name,
            "synthesis_method": self.rag_client.default_model if self.rag_client else "fallback",
        }

    def _search_faiss(self, query: str, top_k: int = 5) -> list[dict]:
        """Search the FAISS index for similar documents."""
        import faiss

        query_embedding = self.embedder.encode(query).reshape(1, -1).astype(np.float32)
        scores, indices = self.faiss_index.search(query_embedding, min(top_k, len(self.documents)))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.documents) and idx >= 0:
                # FAISS returns L2 distance; convert to similarity score
                similarity = max(0, 1.0 - score / 2.0)
                metadata = self.metadata[idx] if idx < len(self.metadata) else {}
                results.append({
                    "content": self.documents[idx],
                    "score": round(similarity, 3),
                    "source": metadata.get("source", "unknown"),
                    "source_url": metadata.get("source_url", ""),
                    "last_reviewed": metadata.get("last_reviewed", ""),
                    "category": metadata.get("category", "general"),
                })

        return results

    def _fallback_knowledge(self, query: str) -> list[dict]:
        """Return basic medical knowledge when vector store is empty."""
        disease_db = {
            "headache": {
                "conditions": ["Tension headache", "Migraine", "Cluster headache", "Sinusitis"],
                "description": "Headaches can range from tension-type (most common) to migraines and cluster headaches. Location, severity, and accompanying symptoms help differentiate.",
                "red_flags": "Sudden severe headache, headache with fever/neck stiffness, headache after head injury",
            },
            "fever": {
                "conditions": ["Viral infection", "Bacterial infection", "Inflammatory condition", "Malaria"],
                "description": "Fever is an elevated body temperature usually caused by infection. Temperature >38°C (100.4°F) indicates fever.",
                "red_flags": "Fever >40°C, fever lasting >3 days, fever with rash or confusion",
            },
            "cough": {
                "conditions": ["Upper respiratory infection", "Bronchitis", "Pneumonia", "Asthma", "COPD"],
                "description": "Cough can be acute (<3 weeks), subacute (3-8 weeks), or chronic (>8 weeks). Productive vs dry cough helps differentiate causes.",
                "red_flags": "Coughing blood, severe shortness of breath, chest pain",
            },
            "chest pain": {
                "conditions": ["Angina", "Myocardial infarction", "Pleurisy", "Costochondritis", "GERD"],
                "description": "Chest pain requires careful evaluation. Cardiac causes must be ruled out first. Characteristics (sharp, dull, radiating) guide diagnosis.",
                "red_flags": "Crushing chest pain, pain radiating to arm/jaw, with sweating or shortness of breath — call emergency",
            },
        }

        query_lower = query.lower()
        matched = []

        for symptom, info in disease_db.items():
            if symptom in query_lower:
                matched.append({
                    "content": f"{symptom.upper()}: {info['description']}\n\nPossible conditions: {', '.join(info['conditions'])}\n\nRed flags: {info['red_flags']}",
                    "score": 0.9,
                    "source": "built-in medical knowledge base",
                })

        if not matched:
            matched.append({
                "content": f"No specific knowledge base entry found for the query. General recommendation: consult a healthcare provider for proper evaluation.",
                "score": 0.1,
                "source": "general guidance",
            })

        return matched

    def ingest_documents(self, documents: list[dict]):
        """Add medical documents to the vector store.

        Args:
            documents: List of dicts with 'text', 'source', and optional 'metadata'.
        """
        if not documents:
            self.log("warning", "No documents provided for ingestion")
            return

        texts = [d["text"] for d in documents]
        meta_list = [d.get("metadata", {"source": d.get("source", "unknown")}) for d in documents]

        # Generate embeddings
        embeddings = self.embedder.encode_batch(texts)

        # Create or extend FAISS index
        import faiss
        store_dir = settings.vector_store_dir
        os.makedirs(store_dir, exist_ok=True)

        faiss_path = os.path.join(store_dir, "medical_knowledge.faiss")
        meta_path = os.path.join(store_dir, "medical_knowledge_meta.json")

        if self.faiss_index is not None:
            existing_count = self.faiss_index.ntotal
            if existing_count > 0:
                # Re-encode existing documents before rebuilding; zero-padding
                # old vectors would silently destroy retrieval quality.
                existing_embeddings = self.embedder.encode_batch(self.documents)
                combined = np.vstack([
                    existing_embeddings.astype(np.float32),
                    embeddings.astype(np.float32),
                ])
                self.faiss_index = faiss.IndexFlatL2(self.embedder.DIMENSION)
                self.faiss_index.add(combined)
                self.documents.extend(texts)
                self.metadata.extend(meta_list)
            else:
                self.faiss_index.add(embeddings.astype(np.float32))
                self.documents.extend(texts)
                self.metadata.extend(meta_list)
        else:
            self.faiss_index = faiss.IndexFlatL2(self.embedder.DIMENSION)
            self.faiss_index.add(embeddings.astype(np.float32))
            self.documents = texts
            self.metadata = meta_list

        # Save to disk
        faiss.write_index(self.faiss_index, faiss_path)
        with open(meta_path, "w") as f:
            json.dump({"documents": self.documents, "metadata": self.metadata}, f)

        self.log("info", f"Ingested {len(documents)} documents — total: {len(self.documents)}")
