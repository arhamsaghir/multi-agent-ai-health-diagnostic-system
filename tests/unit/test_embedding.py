"""Tests for the embedding module."""

import numpy as np
import pytest
from src.data.embedding import EmbeddingModel


@pytest.fixture
def embedder():
    return EmbeddingModel()


class TestEmbeddingModel:
    """Test suite for embedding generation."""

    def test_encode_single_text(self, embedder):
        embedding = embedder.encode("headache and fever")
        assert embedding.shape == (embedder.DIMENSION,)
        assert embedding.dtype == np.float32

    def test_encode_batch(self, embedder):
        texts = ["headache", "fever", "cough"]
        embeddings = embedder.encode_batch(texts)
        assert embeddings.shape == (3, embedder.DIMENSION)

    def test_similarity_same_text(self, embedder):
        emb1 = embedder.encode("headache and fever")
        emb2 = embedder.encode("headache and fever")
        sim = embedder.similarity(emb1, emb2)
        assert sim > 0.99  # Should be nearly 1.0

    def test_similarity_different_text(self, embedder):
        emb1 = embedder.encode("headache and fever")
        emb2 = embedder.encode("broken leg fracture")
        sim = embedder.similarity(emb1, emb2)
        assert 0 <= sim <= 1.0

    def test_similarity_related_text(self, embedder):
        emb1 = embedder.encode("headache and nausea")
        emb2 = embedder.encode("migraine and vomiting")
        sim = embedder.similarity(emb1, emb2)
        assert sim > 0.1  # Related concepts should have some similarity
