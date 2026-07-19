import shutil
import unittest
from pathlib import Path

import numpy as np

from src.chunker import split_text_by_words
from src.metadata import ChunkMetadata, TextChunk
from src.vector_store import FaissVectorStore


class ChunkerTests(unittest.TestCase):
    def test_word_chunking_with_overlap(self) -> None:
        text = "one two three four five six seven eight"
        chunks = split_text_by_words(
            text,
            chunk_size_words=4,
            overlap_words=2,
        )

        self.assertEqual(
            chunks,
            [
                "one two three four",
                "three four five six",
                "five six seven eight",
            ],
        )


class VectorStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store_dir = Path("tests") / "_temp_vector_store"
        shutil.rmtree(self.store_dir, ignore_errors=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.store_dir, ignore_errors=True)

    def test_save_and_load_preserves_chunks(self) -> None:
        chunk = TextChunk(
            metadata=ChunkMetadata(
                chunk_id="test_chunk_001",
                source="test.md",
                source_path="data/sample_documents/test.md",
                page=None,
                chunk_index=1,
                total_chunks_for_document=1,
            ),
            text="Harry Potter is a wizard.",
        )

        embeddings = np.array([[1.0, 0.0, 0.0]], dtype="float32")

        store = FaissVectorStore(embedding_dimension=3)
        store.add(embeddings, [chunk])
        store.save(self.store_dir)

        loaded = FaissVectorStore.load(self.store_dir)

        self.assertEqual(loaded.index.ntotal, 1)
        self.assertEqual(len(loaded.chunks), 1)
        self.assertEqual(loaded.chunks[0].text, chunk.text)
        self.assertEqual(
            loaded.chunks[0].metadata.chunk_id,
            "test_chunk_001",
        )


if __name__ == "__main__":
    unittest.main()
