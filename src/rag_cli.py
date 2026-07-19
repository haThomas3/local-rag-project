from __future__ import annotations

import argparse

from src.config import SAMPLE_DOCUMENTS_DIR
from src.prompt_builder import build_debug_report, build_rag_prompt, build_user_report
from src.retriever import LocalRetriever, build_retriever_from_dir


EXIT_COMMANDS = {"exit", "quit", ":exit", ":quit"}
HELP_COMMANDS = {"help", ":help"}


def print_help() -> None:
    print()
    print("Available commands:")
    print("  :help      Show this help message.")
    print("  :debug     Toggle debug report on or off.")
    print("  :prompt    Toggle raw RAG prompt display on or off.")
    print("  exit       Exit the CLI.")
    print()


def print_question_result(
    question: str,
    retriever: LocalRetriever,
    top_k: int,
    debug: bool,
    show_prompt: bool,
) -> None:
    results = retriever.retrieve(question, top_k=top_k)

    print()
    print(build_user_report(question, results))

    if debug:
        print()
        print(build_debug_report(question, results))

    if show_prompt:
        print()
        print("RAW RAG PROMPT")
        print("==============")
        print(build_rag_prompt(question, results))


def run_interactive_loop(
    retriever: LocalRetriever,
    top_k: int,
    debug: bool,
    show_prompt: bool,
) -> None:
    print("Type a question, ':help', ':debug', ':prompt', or 'exit'.")
    print()

    debug_enabled = debug
    prompt_enabled = show_prompt

    while True:
        question = input("Question> ").strip()

        if not question:
            continue

        normalized_question = question.lower()

        if normalized_question in EXIT_COMMANDS:
            print("Exiting local RAG CLI.")
            break

        if normalized_question in HELP_COMMANDS:
            print_help()
            continue

        if normalized_question == ":debug":
            debug_enabled = not debug_enabled
            print(f"Debug report: {'on' if debug_enabled else 'off'}")
            continue

        if normalized_question == ":prompt":
            prompt_enabled = not prompt_enabled
            print(f"Raw prompt display: {'on' if prompt_enabled else 'off'}")
            continue

        print_question_result(
            question=question,
            retriever=retriever,
            top_k=top_k,
            debug=debug_enabled,
            show_prompt=prompt_enabled,
        )
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local RAG CLI.")
    parser.add_argument(
        "--question",
        default=None,
        help="Run one question and exit. If omitted, starts interactive mode.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of retrieved chunks to request before relevance filtering.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show developer debug report.",
    )
    parser.add_argument(
        "--show-prompt",
        action="store_true",
        help="Show the raw RAG prompt.",
    )

    args = parser.parse_args()

    print("Loading local RAG system...")
    retriever, chunks = build_retriever_from_dir(SAMPLE_DOCUMENTS_DIR)
    print(f"Local RAG is ready. Indexed chunks: {len(chunks)}")

    if args.question:
        print_question_result(
            question=args.question,
            retriever=retriever,
            top_k=args.top_k,
            debug=args.debug,
            show_prompt=args.show_prompt,
        )
        return

    run_interactive_loop(
        retriever=retriever,
        top_k=args.top_k,
        debug=args.debug,
        show_prompt=args.show_prompt,
    )


if __name__ == "__main__":
    main()
