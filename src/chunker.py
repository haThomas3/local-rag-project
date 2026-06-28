import re

from src.document_loader import LoadedDocument
from src.metadata import ChunkMetadata, TextChunk


def _safe_id_part(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", value.lower()).strip("_")
    return cleaned or "document"


def split_text_by_words(text: str, chunk_size_words: int = 200, overlap_words: int = 40) -> list[str]:
    if chunk_size_words <= 0:
        raise ValueError("chunk_size_words must be positive.")

    if overlap_words < 0:
        raise ValueError("overlap_words cannot be negative.")

    if overlap_words >= chunk_size_words:
        raise ValueError("overlap_words must be smaller than chunk_size_words.")

    words = text.split()

    if not words:
        return []

    chunks: list[str] = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size_words, len(words))
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))

        if end == len(words):
            break

        start = end - overlap_words

    return chunks


def chunk_document(document: LoadedDocument, chunk_size_words: int = 200, overlap_words: int = 40) -> list[TextChunk]:
    raw_chunks = split_text_by_words(
        document.text,
        chunk_size_words=chunk_size_words,
        overlap_words=overlap_words,
    )

    source_name = document.source_path.name
    source_id = _safe_id_part(document.source_path.name)
    total_chunks = len(raw_chunks)

    chunks: list[TextChunk] = []

    for index, text in enumerate(raw_chunks, start=1):
        metadata = ChunkMetadata(
            chunk_id=f"{source_id}_chunk_{index:03d}",
            source=source_name,
            source_path=str(document.source_path),
            page=None,
            chunk_index=index,
            total_chunks_for_document=total_chunks,
        )

        chunks.append(TextChunk(metadata=metadata, text=text))

    return chunks


def chunk_documents(
    documents: list[LoadedDocument],
    chunk_size_words: int = 200,
    overlap_words: int = 40,
) -> list[TextChunk]:
    chunks: list[TextChunk] = []

    for document in documents:
        chunks.extend(
            chunk_document(
                document,
                chunk_size_words=chunk_size_words,
                overlap_words=overlap_words,
            )
        )

    return chunks
