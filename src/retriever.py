from __future__ import annotations

from pathlib import Path

from src.chunker import chunk_documents
from src.document_loader import load_documents_from_dir
from src.embedding_model import LocalEmbeddingModel
from src.metadata import TextChunk
from src.vector_store import FaissVectorStore, SearchResult


class LocalRetriever:
    def __init__(self, embedding_model: LocalEmbeddingModel | None = None) -> None:
        self.embedding_model = embedding_model or LocalEmbeddingModel()
        self.vector_store: FaissVectorStore | None = None

    def index_chunks(self, chunks: list[TextChunk]) -> None:
        if not chunks:
            raise ValueError("chunks cannot be empty.")

        texts = [chunk.text for chunk in chunks]
        embeddings = self.embedding_model.embed_texts(texts)

        self.vector_store = FaissVectorStore(embedding_dimension=embeddings.shape[1])
        self.vector_store.add(embeddings, chunks)

    def retrieve(self, question: str, top_k: int = 5) -> list[SearchResult]:
        if self.vector_store is None:
            raise RuntimeError("No chunks have been indexed yet.")

        query_embedding = self.embedding_model.embed_query(question)
        return self.vector_store.search(query_embedding, top_k=top_k)


def build_retriever_from_dir(
    documents_dir: Path,
    chunk_size_words: int = 40,
    overlap_words: int = 10,
) -> tuple[LocalRetriever, list[TextChunk]]:
    documents = load_documents_from_dir(documents_dir)
    chunks = chunk_documents(
        documents,
        chunk_size_words=chunk_size_words,
        overlap_words=overlap_words,
    )

    retriever = LocalRetriever()
    retriever.index_chunks(chunks)

    return retriever, chunks
