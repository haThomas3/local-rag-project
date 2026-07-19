from __future__ import annotations

import argparse

from src.config import SAMPLE_DOCUMENTS_DIR
from src.prompt_builder import build_debug_report, build_rag_prompt, build_user_report
from src.retriever import build_retriever_from_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a grounded RAG prompt from retrieved chunks.")
    parser.add_argument(
        "--question",
        default="What should the first local version avoid?",
        help="Question to retrieve context for.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of retrieved chunks to include.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print the developer bug report after the user report.",
    )
    parser.add_argument(
        "--show-prompt",
        action="store_true",
        help="Print the raw RAG prompt that will be sent to the LLM.",
    )

    args = parser.parse_args()

    retriever, chunks = build_retriever_from_dir(SAMPLE_DOCUMENTS_DIR)
    results = retriever.retrieve(args.question, top_k=args.top_k)

    print("Indexed chunks:", len(chunks))
    print("Retrieved results:", len(results))
    print()

    print(build_user_report(args.question, results))

    if args.debug:
        print()
        print(build_debug_report(args.question, results))

    if args.show_prompt:
        print()
        print("RAW RAG PROMPT")
        print("==============")
        print(build_rag_prompt(args.question, results))


if __name__ == "__main__":
    main()
