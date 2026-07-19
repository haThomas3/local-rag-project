import unittest

from src.llm_provider import generate_answer_from_prompt
from src.metadata import ChunkMetadata, TextChunk
from src.prompt_builder import (
    INSUFFICIENT_CONTEXT_MESSAGE,
    build_rag_prompt,
    build_user_report,
)
from src.vector_store import SearchResult


def make_search_result(text: str, score: float) -> SearchResult:
    chunk = TextChunk(
        metadata=ChunkMetadata(
            chunk_id="behavior_test_chunk_001",
            source="harry_potter_basics.md",
            source_path="data/sample_documents/harry_potter_basics.md",
            page=None,
            chunk_index=1,
            total_chunks_for_document=1,
        ),
        text=text,
    )

    return SearchResult(chunk=chunk, score=score)


class RagBehaviorTests(unittest.TestCase):
    def test_supported_question_includes_relevant_source(self) -> None:
        result = make_search_result(
            "On Harry's eleventh birthday, Rubeus Hagrid tells Harry that he is a wizard.",
            score=0.75,
        )

        report = build_user_report(
            "Who tells Harry that he is a wizard?",
            [result],
        )

        self.assertIn("Retrieved user-friendly sources:", report)
        self.assertIn("harry_potter_basics.md", report)
        self.assertIn("Rubeus Hagrid", report)
        self.assertNotIn("No sufficiently relevant sources were retrieved.", report)

    def test_low_relevance_question_returns_insufficient_context(self) -> None:
        result = make_search_result(
            "Harry becomes close friends with Ron Weasley and Hermione Granger.",
            score=0.05,
        )

        report = build_user_report(
            "What is the name of Harry Potter's owl?",
            [result],
        )

        self.assertIn(INSUFFICIENT_CONTEXT_MESSAGE, report)
        self.assertIn("No sufficiently relevant sources were retrieved.", report)

    def test_rag_prompt_filters_out_low_relevance_context(self) -> None:
        result = make_search_result(
            "Hedwig is Harry Potter's owl.",
            score=0.05,
        )

        prompt = build_rag_prompt(
            "What is the name of Harry Potter's owl?",
            [result],
        )

        self.assertIn("Reliable retrieved source count: 0", prompt)
        self.assertIn("No sufficiently relevant retrieved context was provided.", prompt)
        self.assertNotIn("Hedwig is Harry Potter's owl.", prompt)

    def test_provider_none_never_uses_remote_api(self) -> None:
        result = generate_answer_from_prompt(
            "Answer using only retrieved context.",
            provider="none",
        )

        self.assertEqual(result.provider, "none")
        self.assertEqual(result.status, "disabled")
        self.assertFalse(result.used_remote_api)


if __name__ == "__main__":
    unittest.main()
