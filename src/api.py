from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from src.config import VECTOR_STORE_DIR
from src.llm_provider import generate_answer_from_prompt, normalize_provider
from src.prompt_builder import (
    build_debug_report,
    build_rag_prompt,
    filter_reliable_results,
)
from src.retriever import LocalRetriever, build_retriever_from_store
from src.source_formatter import _shorten_quote, score_to_relevance_label
from src.vector_store import SearchResult


logger = logging.getLogger(__name__)


class AppState:
    retriever: LocalRetriever | None = None
    chunk_count: int = 0


state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        state.retriever, chunks = build_retriever_from_store(VECTOR_STORE_DIR)
        state.chunk_count = len(chunks)
    except FileNotFoundError:
        logger.warning(
            "No vector store found at %s. Run `python -m src.index_documents` "
            "first, then restart the API. /ask and /documents will return 503 "
            "until then.",
            VECTOR_STORE_DIR,
        )

    yield


app = FastAPI(title="Local RAG API", lifespan=lifespan)

STATIC_DIR = Path(__file__).resolve().parent / "static"


@app.get("/", response_class=HTMLResponse)
def ui() -> str:
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")


def get_retriever() -> LocalRetriever:
    if state.retriever is None:
        raise HTTPException(
            status_code=503,
            detail="Vector store is not loaded. Run `python -m src.index_documents` first.",
        )

    return state.retriever


class AskRequest(BaseModel):
    question: str
    top_k: int = Field(default=3, gt=0)
    generate_answer: bool = False
    llm_provider: str | None = None
    allow_remote_llm: bool = False
    debug: bool = False
    show_prompt: bool = False


class SourceItem(BaseModel):
    source: str
    location: str
    relevance: str
    score: float
    quote: str


class LLMAnswer(BaseModel):
    provider: str
    status: str
    used_remote_api: bool
    answer: str


class AskResponse(BaseModel):
    question: str
    insufficient_context: bool
    sources: list[SourceItem]
    answer: LLMAnswer | None = None
    debug_report: str | None = None
    raw_prompt: str | None = None


class DocumentInfo(BaseModel):
    source: str
    chunk_count: int


class DocumentsResponse(BaseModel):
    documents: list[DocumentInfo]
    total_chunks: int


def _to_source_item(result: SearchResult) -> SourceItem:
    metadata = result.chunk.metadata

    if metadata.page is not None:
        location = f"page {metadata.page}"
    else:
        location = (
            f"document excerpt {metadata.chunk_index} "
            f"of {metadata.total_chunks_for_document}"
        )

    return SourceItem(
        source=metadata.source,
        location=location,
        relevance=score_to_relevance_label(result.score),
        score=result.score,
        quote=_shorten_quote(result.chunk.text),
    )


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "index_loaded": state.retriever is not None,
        "indexed_chunks": state.chunk_count,
    }


@app.get("/documents", response_model=DocumentsResponse)
def documents(retriever: LocalRetriever = Depends(get_retriever)) -> DocumentsResponse:
    counts: dict[str, int] = {}

    for chunk in retriever.vector_store.chunks:
        counts[chunk.metadata.source] = counts.get(chunk.metadata.source, 0) + 1

    return DocumentsResponse(
        documents=[
            DocumentInfo(source=source, chunk_count=count)
            for source, count in sorted(counts.items())
        ],
        total_chunks=sum(counts.values()),
    )


@app.post("/ask", response_model=AskResponse)
def ask(
    request: AskRequest,
    retriever: LocalRetriever = Depends(get_retriever),
) -> AskResponse:
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="question cannot be empty.")

    llm_provider = normalize_provider(request.llm_provider)
    results = retriever.retrieve(request.question, top_k=request.top_k)
    reliable_results = filter_reliable_results(results)

    response = AskResponse(
        question=request.question,
        insufficient_context=not reliable_results,
        sources=[_to_source_item(result) for result in reliable_results],
    )

    if request.generate_answer:
        if not reliable_results:
            response.answer = LLMAnswer(
                provider=llm_provider,
                status="skipped_insufficient_context",
                used_remote_api=False,
                answer=(
                    "Skipped: no sufficiently relevant sources passed the "
                    "retrieval gate."
                ),
            )
        else:
            rag_prompt = build_rag_prompt(request.question, results)
            generation_result = generate_answer_from_prompt(
                prompt=rag_prompt,
                provider=llm_provider,
                allow_remote_api_calls=request.allow_remote_llm,
            )
            response.answer = LLMAnswer(
                provider=generation_result.provider,
                status=generation_result.status,
                used_remote_api=generation_result.used_remote_api,
                answer=generation_result.answer,
            )

    if request.debug:
        response.debug_report = build_debug_report(request.question, results)

    if request.show_prompt:
        response.raw_prompt = build_rag_prompt(request.question, results)

    return response
