from __future__ import annotations

from src.vector_store import SearchResult


MAX_QUOTE_LENGTH = 260


def _shorten_quote(text: str, max_length: int = MAX_QUOTE_LENGTH) -> str:
    cleaned = " ".join(text.split())

    if len(cleaned) <= max_length:
        return cleaned

    return cleaned[: max_length - 3].rstrip() + "..."


def score_to_relevance_label(score: float) -> str:
    if score >= 0.55:
        return "VERY HIGH"

    if score >= 0.35:
        return "HIGH"

    if score >= 0.20:
        return "MEDIUM"

    if score >= 0.10:
        return "LOW"

    return "VERY LOW"


def format_user_friendly_source(result: SearchResult) -> str:
    chunk = result.chunk
    metadata = chunk.metadata

    if metadata.page is not None:
        location = f"page {metadata.page}"
    else:
        location = (
            f"document excerpt {metadata.chunk_index} "
            f"of {metadata.total_chunks_for_document}"
        )

    quote = _shorten_quote(chunk.text)
    relevance = score_to_relevance_label(result.score)

    return "\n".join(
        [
            f"Source file: {metadata.source}",
            f"Location: {location}",
            f"Relevance: {relevance}",
            f'Relevant quote: "{quote}"',
        ]
    )


def format_user_friendly_sources(results: list[SearchResult]) -> str:
    if not results:
        return "No sources were retrieved."

    blocks: list[str] = []

    for index, result in enumerate(results, start=1):
        blocks.append(
            "\n".join(
                [
                    f"[Source {index}]",
                    format_user_friendly_source(result),
                ]
            )
        )

    return "\n\n".join(blocks)
