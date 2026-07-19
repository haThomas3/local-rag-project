from __future__ import annotations

from src.vector_store import SearchResult


MAX_QUOTE_LENGTH = 260


def _shorten_quote(text: str, max_length: int = MAX_QUOTE_LENGTH) -> str:
    cleaned = " ".join(text.split())

    if len(cleaned) <= max_length:
        return cleaned

    return cleaned[: max_length - 3].rstrip() + "..."


def format_user_friendly_source(result: SearchResult) -> str:
    chunk = result.chunk
    metadata = chunk.metadata

    location_parts: list[str] = []

    if metadata.page is not None:
        location_parts.append(f"page {metadata.page}")
    else:
        location_parts.append(
            f"document excerpt {metadata.chunk_index} of {metadata.total_chunks_for_document}"
        )

    location = ", ".join(location_parts)
    quote = _shorten_quote(chunk.text)

    return "\n".join(
        [
            f"Source file: {metadata.source}",
            f"Location: {location}",
            f'Relevant quote: "{quote}"',
            f"Similarity score: {result.score:.4f}",
            f"Technical reference: {metadata.chunk_id}",
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
