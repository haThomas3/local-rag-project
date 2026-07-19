from __future__ import annotations

import argparse

from src.config import VECTOR_STORE_DIR
from src.llm_provider import generate_answer_from_prompt, normalize_provider
from src.prompt_builder import (
    build_debug_report,
    build_rag_prompt,
    build_user_report,
    filter_reliable_results,
)
from src.retriever import LocalRetriever, build_retriever_from_store


EXIT_COMMANDS = {"exit", "quit", ":exit", ":quit"}
HELP_COMMANDS = {"help", ":help"}


def print_help() -> None:
    print()
    print("Available commands:")
    print("  :help      Show this help message.")
    print("  :debug     Toggle debug report on or off.")
    print("  :prompt    Toggle raw RAG prompt display on or off.")
    print("  :answer    Toggle LLM answer generation on or off.")
    print("  exit       Exit the CLI.")
    print()


def print_llm_result(question: str, results, llm_provider: str, allow_remote_llm: bool) -> None:
    reliable_results = filter_reliable_results(results)

    print()
    print("LLM ANSWER")
    print("==========")

    if not reliable_results:
        print("Skipped: no sufficiently relevant sources passed the retrieval gate.")
        print("Used remote API: False")
        return

    rag_prompt = build_rag_prompt(question, results)
    generation_result = generate_answer_from_prompt(
        prompt=rag_prompt,
        provider=llm_provider,
        allow_remote_api_calls=allow_remote_llm,
    )

    print(f"Provider: {generation_result.provider}")
    print(f"Status: {generation_result.status}")
    print(f"Used remote API: {generation_result.used_remote_api}")
    print()
    print(generation_result.answer)


def print_question_result(
    question: str,
    retriever: LocalRetriever,
    top_k: int,
    debug: bool,
    show_prompt: bool,
    generate_answer: bool,
    llm_provider: str,
    allow_remote_llm: bool,
) -> None:
    results = retriever.retrieve(question, top_k=top_k)

    print()
    print(build_user_report(question, results))

    if generate_answer:
        print_llm_result(
            question=question,
            results=results,
            llm_provider=llm_provider,
            allow_remote_llm=allow_remote_llm,
        )

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
    generate_answer: bool,
    llm_provider: str,
    allow_remote_llm: bool,
) -> None:
    print("Type a question, ':help', ':debug', ':prompt', ':answer', or 'exit'.")
    print()

    debug_enabled = debug
    prompt_enabled = show_prompt
    answer_enabled = generate_answer

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

        if normalized_question == ":answer":
            answer_enabled = not answer_enabled
            print(f"LLM answer generation: {'on' if answer_enabled else 'off'}")
            continue

        print_question_result(
            question=question,
            retriever=retriever,
            top_k=top_k,
            debug=debug_enabled,
            show_prompt=prompt_enabled,
            generate_answer=answer_enabled,
            llm_provider=llm_provider,
            allow_remote_llm=allow_remote_llm,
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
    parser.add_argument(
        "--generate-answer",
        action="store_true",
        help="Generate a final answer using the configured LLM provider.",
    )
    parser.add_argument(
        "--llm-provider",
        default=None,
        help="Override LLM provider for this run: none, local, gemini, or openai.",
    )
    parser.add_argument(
        "--allow-remote-llm",
        action="store_true",
        help="Allow a remote LLM provider for this run only.",
    )

    args = parser.parse_args()
    llm_provider = normalize_provider(args.llm_provider)

    print("Loading local RAG system...")
    retriever, chunks = build_retriever_from_store(VECTOR_STORE_DIR)
    print(f"Local RAG is ready. Indexed chunks: {len(chunks)}")
    print(f"LLM provider for this run: {llm_provider}")
    print(f"Remote LLM calls explicitly allowed: {args.allow_remote_llm}")

    if args.question:
        print_question_result(
            question=args.question,
            retriever=retriever,
            top_k=args.top_k,
            debug=args.debug,
            show_prompt=args.show_prompt,
            generate_answer=args.generate_answer,
            llm_provider=llm_provider,
            allow_remote_llm=args.allow_remote_llm,
        )
        return

    run_interactive_loop(
        retriever=retriever,
        top_k=args.top_k,
        debug=args.debug,
        show_prompt=args.show_prompt,
        generate_answer=args.generate_answer,
        llm_provider=llm_provider,
        allow_remote_llm=args.allow_remote_llm,
    )


if __name__ == "__main__":
    main()
