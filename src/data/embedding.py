"""Embedding generation for medical text using sentence-transformers."""

from typing import Optional
import numpy as np
from loguru import logger


class EmbeddingModel:
    """Wraps sentence-transformers for generating text embeddings."""

    DEFAULT_MODEL = "all-MiniLM-L6-v2"
    DIMENSION = 384

    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the sentence-transformers model."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Embedding model loaded: {self.model_name} (dim={self.DIMENSION})")
        except ImportError:
            logger.warning("sentence-transformers not installed — embeddings will use random vectors")
            self.model = None

    def encode(self, text: str) -> np.ndarray:
        """Encode a single text string into an embedding vector.

        Args:
            text: Input text to embed.

        Returns:
            Numpy array of shape (dim,) with the embedding.
        """
        if self.model:
            embedding = self.model.encode([text])[0]
            return embedding.astype(np.float32)
        else:
            # Fallback: random embedding (for development)
            logger.warning("Using random fallback embedding")
            return np.random.randn(self.DIMENSION).astype(np.float32)

    def encode_batch(self, texts: list[str]) -> np.ndarray:
        """Encode multiple texts into embedding vectors.

        Args:
            texts: List of text strings.

        Returns:
            Numpy array of shape (n, dim).
        """
        if self.model:
            embeddings = self.model.encode(texts, show_progress_bar=len(texts) > 10)
            return embeddings.astype(np.float32)
        else:
            return np.random.randn(len(texts), self.DIMENSION).astype(np.float32)

    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Compute cosine similarity between two embeddings."""
        from numpy.linalg import norm
        dot_product = np.dot(embedding1, embedding2)
        norm1 = norm(embedding1)
        norm2 = norm(embedding2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(dot_product / (norm1 * norm2))
