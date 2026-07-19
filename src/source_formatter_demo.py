from __future__ import annotations

from src.config import SAMPLE_DOCUMENTS_DIR
from src.retriever import build_retriever_from_dir
from src.source_formatter import format_user_friendly_sources


def main() -> None:
    question = "What should the first local version avoid?"

    retriever, chunks = build_retriever_from_dir(SAMPLE_DOCUMENTS_DIR)
    results = retriever.retrieve(question, top_k=3)

    print("Indexed chunks:", len(chunks))
    print("Retrieved results:", len(results))
    print()
    print(format_user_friendly_sources(results))


if __name__ == "__main__":
    main()
