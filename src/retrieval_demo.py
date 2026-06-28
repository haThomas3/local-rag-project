from __future__ import annotations

import argparse

from src.config import SAMPLE_DOCUMENTS_DIR
from src.retriever import build_retriever_from_dir


def run_demo(question: str, top_k: int) -> None:
    retriever, chunks = build_retriever_from_dir(SAMPLE_DOCUMENTS_DIR)

    print("Indexed chunks:", len(chunks))
    print("Question:", question)

    results = retriever.retrieve(question, top_k=top_k)

    print("Retrieved results:", len(results))

    for rank, result in enumerate(results, start=1):
        data = result.chunk.to_dict()

        print(f"{rank}. score={result.score:.4f}")
        print(f"   source={data['source']}")
        print(f"   chunk_id={data['chunk_id']}")
        print(f"   text={data['text']}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local semantic retrieval over sample documents.")
    parser.add_argument(
        "--question",
        default="What should the first local version avoid?",
        help="Question to retrieve relevant chunks for.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Maximum number of chunks to retrieve.",
    )

    args = parser.parse_args()
    run_demo(question=args.question, top_k=args.top_k)


if __name__ == "__main__":
    main()
