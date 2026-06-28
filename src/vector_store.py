from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import faiss
import numpy as np

from src.metadata import ChunkMetadata, TextChunk


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

    def save(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)

        index_path = directory / "index.faiss"
        chunks_path = directory / "chunks.json"

        faiss.write_index(self.index, str(index_path))

        chunk_data = [chunk.to_dict() for chunk in self.chunks]
        chunks_path.write_text(
            json.dumps(chunk_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, directory: Path) -> "FaissVectorStore":
        index_path = directory / "index.faiss"
        chunks_path = directory / "chunks.json"

        if not index_path.exists():
            raise FileNotFoundError(f"Missing FAISS index file: {index_path}")

        if not chunks_path.exists():
            raise FileNotFoundError(f"Missing chunks metadata file: {chunks_path}")

        index = faiss.read_index(str(index_path))
        raw_chunks = json.loads(chunks_path.read_text(encoding="utf-8"))

        store = cls(embedding_dimension=index.d)
        store.index = index
        store.chunks = [
            TextChunk(
                metadata=ChunkMetadata(
                    chunk_id=item["chunk_id"],
                    source=item["source"],
                    source_path=item["source_path"],
                    page=item["page"],
                    chunk_index=item["chunk_index"],
                    total_chunks_for_document=item["total_chunks_for_document"],
                ),
                text=item["text"],
            )
            for item in raw_chunks
        ]

        if store.index.ntotal != len(store.chunks):
            raise ValueError("FAISS index size does not match chunks metadata size.")

        return store
