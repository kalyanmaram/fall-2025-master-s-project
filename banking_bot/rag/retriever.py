# banking_bot/rag/retriever.py
from typing import List
import numpy as np
from ..models import Snippet
from .embeddings import EmbeddingProvider


class Retriever:
    """
    Single-responsibility: given a query, return top-k relevant snippets using cosine similarity.
    """

    def __init__(self, snippets: List[Snippet], embedder: EmbeddingProvider) -> None:
        self._snippets = snippets
        self._embedder = embedder
        self._texts = [s.text for s in snippets]
        self._ids = [s.id for s in snippets]
        self._embeds = self._embedder.encode(self._texts)

    def retrieve(self, query: str, top_k: int = 3) -> List[Snippet]:
        q_vec = self._embedder.encode([query])[0]
        scores = self._embeds @ q_vec
        idx = np.argsort(-scores)[:top_k]
        results: List[Snippet] = []
        for i in idx:
            s = self._snippets[i]
            results.append(
                Snippet(
                    id=s.id,
                    text=s.text,
                    score=float(scores[i]),
                    source=s.source,
                )
            )
        return results
