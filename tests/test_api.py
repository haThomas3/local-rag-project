import unittest

import numpy as np
from fastapi.testclient import TestClient

from src.api import app, get_retriever
from src.metadata import ChunkMetadata, TextChunk
from src.retriever import LocalRetriever
from src.vector_store import FaissVectorStore


class _StubEmbeddingModel:
    def embed_query(self, question: str) -> np.ndarray:
        if "wizard" in question.lower():
            return np.array([1.0, 0.0], dtype="float32")

        return np.array([0.0, 1.0], dtype="float32")


def _build_test_retriever() -> LocalRetriever:
    chunk = TextChunk(
        metadata=ChunkMetadata(
            chunk_id="api_test_chunk_001",
            source="harry_potter_basics.md",
            source_path="data/sample_documents/harry_potter_basics.md",
            page=None,
            chunk_index=1,
            total_chunks_for_document=1,
        ),
        text="On Harry's eleventh birthday, Rubeus Hagrid tells Harry that he is a wizard.",
    )

    store = FaissVectorStore(embedding_dimension=2)
    store.add(np.array([[1.0, 0.0]], dtype="float32"), [chunk])

    retriever = LocalRetriever(embedding_model=_StubEmbeddingModel())
    retriever.vector_store = store
    return retriever


class ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        app.dependency_overrides[get_retriever] = _build_test_retriever
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_health_reports_ok_without_requiring_index(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_documents_lists_indexed_sources(self) -> None:
        response = self.client.get("/documents")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["total_chunks"], 1)
        self.assertEqual(body["documents"][0]["source"], "harry_potter_basics.md")

    def test_ask_returns_relevant_source_without_generating_answer(self) -> None:
        response = self.client.post(
            "/ask",
            json={"question": "Who tells Harry that he is a wizard?"},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertFalse(body["insufficient_context"])
        self.assertEqual(len(body["sources"]), 1)
        self.assertIn("Hagrid", body["sources"][0]["quote"])
        self.assertIsNone(body["answer"])

    def test_ask_returns_insufficient_context_for_unrelated_question(self) -> None:
        response = self.client.post(
            "/ask",
            json={"question": "What is the capital of France?"},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["insufficient_context"])
        self.assertEqual(body["sources"], [])

    def test_ask_with_generate_answer_uses_none_provider_by_default(self) -> None:
        response = self.client.post(
            "/ask",
            json={
                "question": "Who tells Harry that he is a wizard?",
                "generate_answer": True,
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["answer"]["provider"], "none")
        self.assertEqual(body["answer"]["status"], "disabled")
        self.assertFalse(body["answer"]["used_remote_api"])

    def test_ask_rejects_empty_question(self) -> None:
        response = self.client.post("/ask", json={"question": "   "})

        self.assertEqual(response.status_code, 400)

    def test_endpoints_return_503_without_loaded_index(self) -> None:
        app.dependency_overrides.clear()

        response = self.client.get("/documents")

        self.assertEqual(response.status_code, 503)


if __name__ == "__main__":
    unittest.main()
