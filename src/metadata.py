from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ChunkMetadata:
    chunk_id: str
    source: str
    source_path: str
    page: int | None
    chunk_index: int
    total_chunks_for_document: int


@dataclass(frozen=True)
class TextChunk:
    metadata: ChunkMetadata
    text: str

    def to_dict(self) -> dict[str, object]:
        data = asdict(self.metadata)
        data["text"] = self.text
        return data
