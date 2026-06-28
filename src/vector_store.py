from __future__ import annotations

from dataclasses import dataclass

import faiss
import numpy as np

from src.metadata import TextChunk


@dataclass(frozen=True)
class SearchResult:
    chunk: TextChunk
    score: float


class FaissVectorStore:
    def __init__(self, embedding_dimension: int) -> None:
        if embedding_dimension <= 0:
            raise ValueError("embedding_dimension must be positive.")

        self.embedding_dimension = embedding_dimension
        self.index = faiss.IndexFlatIP(embedding_dimension)
        self.chunks: list[TextChunk] = []

    def add(self, embeddings: np.ndarray, chunks: list[TextChunk]) -> None:
        if len(chunks) == 0:
            raise ValueError("chunks cannot be empty.")

        if embeddings.ndim != 2:
            raise ValueError("embeddings must be a 2D array.")

        if embeddings.shape[0] != len(chunks):
            raise ValueError("number of embeddings must match number of chunks.")

        if embeddings.shape[1] != self.embedding_dimension:
            raise ValueError("embedding dimension does not match this vector store.")

        matrix = np.ascontiguousarray(embeddings.astype("float32"))
        self.index.add(matrix)
        self.chunks.extend(chunks)

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> list[SearchResult]:
        if top_k <= 0:
            raise ValueError("top_k must be positive.")

        if self.index.ntotal == 0:
            return []

        query = np.asarray(query_embedding, dtype="float32")

        if query.ndim == 1:
            query = query.reshape(1, -1)

        if query.shape[1] != self.embedding_dimension:
            raise ValueError("query embedding dimension does not match this vector store.")

        effective_top_k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(np.ascontiguousarray(query), effective_top_k)

        results: list[SearchResult] = []

        for score, index in zip(scores[0], indices[0]):
            if index == -1:
                continue

            results.append(
                SearchResult(
                    chunk=self.chunks[int(index)],
                    score=float(score),
                )
            )

        return results
