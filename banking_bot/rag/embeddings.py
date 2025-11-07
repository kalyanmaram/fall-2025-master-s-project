# banking_bot/rag/embeddings.py
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingProvider:
    """
    Single-responsibility: turn texts into normalized vectors.
    Wraps SentenceTransformer to allow easy swap later.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self._model = SentenceTransformer(model_name)

    def encode(self, texts: List[str]) -> np.ndarray:
        vecs = self._model.encode(texts, convert_to_numpy=True)
        norms = np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-9
        return vecs / norms
