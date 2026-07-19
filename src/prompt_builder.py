from __future__ import annotations

from src.source_formatter import format_user_friendly_sources
from src.vector_store import SearchResult


INSUFFICIENT_CONTEXT_MESSAGE = (
    "The indexed documents do not contain enough information to answer this question."
)


GROUNDING_RULES = f"""You are a local RAG assistant.

Your task is to answer the user's question using only the retrieved context.

Rules:
1. Use only the information provided in the retrieved context.
2. Do not use outside knowledge.
3. Do not invent facts, sources, numbers, dates, or explanations.
4. If the retrieved context is insufficient, answer exactly:
"{INSUFFICIENT_CONTEXT_MESSAGE}"
5. Include user-friendly sources when the answer is supported by context.
6. Prefer source file, location, and relevant quote over technical chunk IDs.
7. Technical references are for debugging and should not be the main citation shown to the user.
"""


def format_context_for_prompt(results: list[SearchResult]) -> str:
    if not results:
        return "No retrieved context was provided."

    context_blocks: list[str] = []

    for index, result in enumerate(results, start=1):
        chunk = result.chunk
        metadata = chunk.metadata

        if metadata.page is not None:
            location = f"page {metadata.page}"
        else:
            location = (
                f"document excerpt {metadata.chunk_index} "
                f"of {metadata.total_chunks_for_document}"
            )

        context_blocks.append(
            "\n".join(
                [
                    f"[Context {index}]",
                    f"source_file: {metadata.source}",
                    f"location: {location}",
                    f"similarity_score: {result.score:.4f}",
                    f"technical_reference: {metadata.chunk_id}",
                    "text:",
                    chunk.text,
                ]
            )
        )

    return "\n\n".join(context_blocks)


def build_rag_prompt(question: str, results: list[SearchResult]) -> str:
    if not question.strip():
        raise ValueError("question cannot be empty.")

    retrieved_context = format_context_for_prompt(results)
    user_friendly_sources = format_user_friendly_sources(results)

    return "\n\n".join(
        [
            GROUNDING_RULES.strip(),
            "Retrieved context:",
            retrieved_context,
            "User-friendly source notes:",
            user_friendly_sources,
            "User question:",
            question.strip(),
            "Required answer format:",
            "Answer:",
            "<answer based only on retrieved context>",
            "",
            "Sources:",
            "<source file, location, and short supporting quote>",
        ]
    )


def build_user_report(question: str, results: list[SearchResult]) -> str:
    if not question.strip():
        raise ValueError("question cannot be empty.")

    return "\n".join(
        [
            "USER REPORT",
            "===========",
            f"Question: {question.strip()}",
            "",
            "Retrieved user-friendly sources:",
            format_user_friendly_sources(results),
            "",
            "Expected answer behavior:",
            "- Answer only if the retrieved sources contain enough information.",
            f'- Otherwise answer: "{INSUFFICIENT_CONTEXT_MESSAGE}"',
        ]
    )


def build_debug_report(question: str, results: list[SearchResult]) -> str:
    if not question.strip():
        raise ValueError("question cannot be empty.")

    lines: list[str] = [
        "BUG REPORT",
        "==========",
        f"Question: {question.strip()}",
        f"Retrieved result count: {len(results)}",
        "",
    ]

    if not results:
        lines.append("No retrieved results were returned.")
        return "\n".join(lines)

    for index, result in enumerate(results, start=1):
        chunk = result.chunk
        metadata = chunk.metadata

        lines.extend(
            [
                f"[Retrieved Result {index}]",
                f"score: {result.score:.4f}",
                f"source: {metadata.source}",
                f"source_path: {metadata.source_path}",
                f"page: {metadata.page}",
                f"chunk_index: {metadata.chunk_index}",
                f"total_chunks_for_document: {metadata.total_chunks_for_document}",
                f"technical_reference: {metadata.chunk_id}",
                "raw_text:",
                chunk.text,
                "",
            ]
        )

    return "\n".join(lines)
