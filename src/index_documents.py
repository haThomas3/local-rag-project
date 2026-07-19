from __future__ import annotations

from src.chunker import chunk_documents
from src.config import SAMPLE_DOCUMENTS_DIR, VECTOR_STORE_DIR
from src.document_loader import load_documents_from_dir
from src.embedding_model import LocalEmbeddingModel
from src.vector_store import FaissVectorStore


CHUNK_SIZE_WORDS = 40
OVERLAP_WORDS = 10


def index_documents() -> None:
    documents = load_documents_from_dir(SAMPLE_DOCUMENTS_DIR)

    if not documents:
        raise RuntimeError(f"No supported documents found in: {SAMPLE_DOCUMENTS_DIR}")

    chunks = chunk_documents(
        documents,
        chunk_size_words=CHUNK_SIZE_WORDS,
        overlap_words=OVERLAP_WORDS,
    )

    if not chunks:
        raise RuntimeError("Documents were loaded, but no text chunks were created.")

    embedding_model = LocalEmbeddingModel()
    embeddings = embedding_model.embed_texts([chunk.text for chunk in chunks])

    vector_store = FaissVectorStore(embedding_dimension=embeddings.shape[1])
    vector_store.add(embeddings, chunks)
    vector_store.save(VECTOR_STORE_DIR)

    print("Document indexing completed.")
    print(f"Documents indexed: {len(documents)}")
    print(f"Chunks created: {len(chunks)}")
    print(f"Embedding dimension: {embeddings.shape[1]}")
    print(f"Vector store directory: {VECTOR_STORE_DIR}")


def main() -> None:
    index_documents()


if __name__ == "__main__":
    main()
