from __future__ import annotations

from pathlib import Path

from src.config import SAMPLE_DOCUMENTS_DIR
from src.retriever import build_retriever_from_dir
from src.vector_store import FaissVectorStore


VECTOR_STORE_DIR = Path("data/vector_store")


def main() -> None:
    retriever, chunks = build_retriever_from_dir(SAMPLE_DOCUMENTS_DIR)

    if retriever.vector_store is None:
        raise RuntimeError("Vector store was not created.")

    retriever.vector_store.save(VECTOR_STORE_DIR)
    loaded_store = FaissVectorStore.load(VECTOR_STORE_DIR)

    query_embedding = retriever.embedding_model.embed_query("What should the first local version avoid?")
    results = loaded_store.search(query_embedding, top_k=3)

    print("Saved vector store:", VECTOR_STORE_DIR)
    print("Indexed chunks:", len(chunks))
    print("Loaded chunks:", len(loaded_store.chunks))
    print("Loaded FAISS vectors:", loaded_store.index.ntotal)
    print("Retrieved results:", len(results))

    for rank, result in enumerate(results, start=1):
        data = result.chunk.to_dict()
        print(f"{rank}. score={result.score:.4f} source={data['source']} chunk_id={data['chunk_id']}")


if __name__ == "__main__":
    main()
