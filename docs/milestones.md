# Local RAG Project Milestones

This document tracks the planned development path for the local RAG project.

The goal of the project is to build a local-first, NotebookLM-style RAG system that can load user documents, index them locally, retrieve relevant source text, and answer questions with grounded citations.

The project is designed to start as a local Python system and later evolve into a user-friendly application with a backend, frontend, file upload flow, and optional LLM provider comparison.

---

## Current Status

Completed baseline milestones:

- Milestone 1 — Project Foundation
- Milestone 2 — Security and Configuration
- Milestone 3 — Local Document Ingestion
- Milestone 4 — Local Embeddings and Vector Store
- Milestone 5 — RAG Prompt Builder
- Milestone 6 — Local RAG Runtime / Interactive CLI

Latest completed implementation checkpoint:

- `6e60f7b Add behavioral RAG evaluation tests`

---

## Milestone 1 — Project Foundation

Status: Complete

Goal: Create a clean project foundation with Git, GitHub, documentation, and a basic Python project structure.

Completed work:

- Created the local project directory.
- Initialized Git.
- Connected the project to GitHub.
- Added a basic README.
- Added a sample documents directory.
- Added the initial milestone document.
- Verified that the project can be developed safely through small commits.

Done means:

- The project exists locally.
- Git works.
- GitHub sync works.
- The repository has a basic structure for future RAG work.

---

## Milestone 2 — Security and Configuration

Status: Complete

Goal: Prepare the project for safe use of API keys and local configuration.

Completed work:

- Added `.env`.
- Added `.env.example`.
- Added `.gitignore`.
- Verified that `.env` is ignored by Git.
- Added configuration loading logic.
- Verified that API keys are not printed directly.
- Confirmed that secret files are not staged or tracked.

Done means:

- Local secrets can be used safely.
- `.env` does not enter Git.
- Future OpenAI, Gemini, or other provider keys can be added without exposing them.

Important rule:

- Never commit API keys, tokens, or private credentials.

---

## Milestone 3 — Local Document Ingestion

Status: Complete, basic version

Goal: Load local documents and split them into usable text chunks.

Completed work:

- Added local document loading.
- Added support for `.txt`.
- Added support for `.md`.
- Added basic PDF support through `pypdf`.
- Added metadata for loaded documents.
- Added chunking logic.
- Added stable chunk identifiers.
- Verified that sample documents are loaded and chunked correctly.

Current limitation:

- PDF support exists at a basic level.
- Source locations are still mostly based on document excerpts.
- More advanced page, paragraph, and section metadata will be improved later.

Done means:

- The system can load local documents from disk.
- The system can split documents into chunks.
- Each chunk has metadata that can be used later for retrieval and citation.

---

## Milestone 4 — Local Embeddings and Vector Store

Status: Complete

Goal: Convert chunks into embeddings and search them locally using a vector store.

Completed work:

- Added a local embedding model.
- Added FAISS-based vector search.
- Added retrieval by user question.
- Added top-k retrieval.
- Added vector store persistence.
- Added save/load flow for the local vector store.
- Verified retrieval on sample questions.

Important commits:

- `d9e7466 Add local embeddings and FAISS retrieval`
- `b2a36ac Persist local FAISS vector store`

Done means:

- The system can embed chunks.
- The system can embed questions.
- The system can retrieve relevant chunks.
- The vector store can be saved locally and loaded again.

Current limitation:

- Running one-off scripts reloads the model each time, which is slow.
- A later runtime milestone will keep the system active between questions.

---

## Milestone 5 — RAG Prompt Builder

Status: Complete

Goal: Build the prompt layer that turns retrieved chunks into a grounded RAG prompt.

Completed work:

- Added `build_rag_prompt`.
- Added `build_user_report`.
- Added `build_debug_report`.
- Added `--debug`.
- Added `--show-prompt`.
- Added user-friendly source formatting.
- Added relevance labels:
  - `VERY HIGH`
  - `HIGH`
  - `MEDIUM`
  - `LOW`
  - `VERY LOW`
- Added a retrieval relevance gate.
- Prevented weak retrieval results from being treated as valid sources.
- Added insufficient-context behavior.

Important commits:

- `7febd7c Add user-friendly source formatting`
- `d134310 Add grounded RAG prompt builder`
- `87dcb19 Add retrieval relevance gate`

Done means:

- Retrieved context is formatted into a prompt.
- The prompt tells the LLM to use only retrieved context.
- The system can detect when no sufficiently relevant sources were retrieved.
- User-facing reports are clean.
- Developer debug reports still include technical details.

---

## Milestone 6 — Local RAG Runtime / Interactive CLI

Status: Complete

Goal: Keep the RAG system running instead of restarting Python and reloading the model for every question.

Planned work:

- Add an interactive CLI.
- Load documents and vector store once.
- Load the embedding model once.
- Keep the process alive.
- Let the user ask multiple questions in one session.
- Add commands such as `exit`, `debug`, or `show prompt` if useful.

Why this matters:

- Current scripts are slow because each command starts Python again and reloads the embedding model.
- A persistent runtime will make the local system feel much faster.

Important commits:

- `d865629 Add interactive local RAG CLI`

Done means:

- The user can start the RAG system once.
- The system waits for questions.
- Multiple questions can be asked without reloading everything each time.

---

## Milestone 7 — LLM Provider Integration

Status: In progress - Gemini generation implemented and verified live; local/Ollama provider implemented in code, pending a locally downloaded model; OpenAI still a stub

Goal: Connect the RAG prompt to an actual LLM provider.

Current checkpoint:

- 7A — Complete:
  - Cost-safe LLM provider scaffold exists.
  - Default provider is none.
  - Remote LLM calls are blocked by default.
  - CLI supports explicit per-run provider override.
  - CLI supports explicit remote opt-in using --allow-remote-llm.
  - Gemini/OpenAI/Ollama are not default dependencies for normal use.

- 7B — In progress:
  - Real Gemini provider implemented using the `google-genai` SDK (the
    previous `google-generativeai` package is deprecated by Google and was
    replaced). Verified live end-to-end: retrieval, grounded prompt, and a
    real Gemini answer with correct source citations.
  - Real local provider implemented against the Ollama HTTP API
    (`OLLAMA_BASE_URL`, default `http://localhost:11434`) using only the
    Python standard library, so no extra dependency is required. Fails
    gracefully with a clear message (`ollama_unavailable`) when Ollama is
    not running or no model has been pulled yet. Not yet verified against a
    real running model because no local Ollama model has been downloaded
    yet due to local disk/RAM constraints. This is the intended default
    provider once a model is available, so the RAG assistant can run fully
    offline with no per-call cost.
  - OpenAI provider is still a stub (`not_implemented`). Not prioritized
    since Gemini (dev/testing) and Ollama (offline default) already cover
    the project's needs.
  - Verified that generated answers use only retrieved sources (Gemini
    live test returned citations matching the retrieved chunks).
  - LLM refusal test not needed as a separate case: the retrieval
    relevance gate already blocks the LLM call entirely when context is
    insufficient (see Milestone 5 and Milestone 9), so no provider ever
    sees a question it can't ground an answer to.

Cost-control note:

- `ALLOW_PAID_API_CALLS` stays `false` in `.env` by default. Real Gemini
  calls only happen when explicitly opted into per run with
  `--allow-remote-llm`, so the key sitting in `.env` cannot be used
  accidentally.

Done means:

- The system retrieves relevant sources.
- The system builds a grounded prompt.
- The selected LLM generates an answer.
- The answer includes source references.
- [x] Achieved for Gemini (opt-in, remote).
- [ ] Not yet achieved for local/Ollama (code ready, no model pulled yet).
- [ ] Not yet achieved for OpenAI (stub only).

---

## Milestone 8 — Document Indexing Workflow

Status: Complete, basic version

Goal: Create a cleaner workflow for adding and indexing documents.

Completed baseline:

- Added `python -m src.index_documents`.
- Loads `.txt`, `.md`, and `.pdf` files from `data/sample_documents`.
- Splits documents into chunks.
- Creates embeddings using the local embedding model.
- Rebuilds and saves the FAISS vector store in `data/vector_store`.
- CLI loads the saved index instead of rebuilding it on every run.
- Verified retrieval from a newly indexed document.
- Does not call Gemini, OpenAI, or another remote LLM API.

Future improvements:

- Track which files were indexed.
- Support incremental updates instead of full rebuilds.
- Improve PDF page-level handling.
- Improve source metadata and document location information.

Done means:

- The user can add documents into the project.
- The system can index those documents.
- The vector store is updated.
- The CLI can retrieve information from the indexed files.

---

## Milestone 9 — Evaluation Suite

Status: Complete - local evaluation suite

Goal: Add tests that verify whether the RAG system behaves correctly.

Completed local evaluation coverage:

- Core chunking behavior is tested.
- Vector store save/load behavior is tested.
- Supported RAG questions return relevant sources.
- Low-relevance context returns insufficient-context behavior.
- RAG prompts filter out unreliable retrieved context.
- Provider none is verified to avoid remote API usage.
- Local/Ollama provider is verified to fail gracefully (no crash, no
  remote fallback) when Ollama is not running.

Still deferred:

- Automated Gemini answer-generation test. Verified manually/live once
  (see Milestone 7B), but not added to the automated suite on purpose —
  running it automatically would call a paid API on every test run,
  which conflicts with the project's low-cost goal.
- Automated local/Ollama answer-generation test against a real running
  model. Blocked until a model is actually pulled locally.
- OpenAI answer-generation tests (blocked on OpenAI provider
  implementation, not currently prioritized).

Planned work:

- Add test questions.
- Add expected source behavior.
- Test retrieval quality.
- Test insufficient-context behavior.
- Test that weak sources are rejected.
- Test that supported file-type questions retrieve the right chunks.
- Add regression checks for known failure cases.

Done means:

- We can verify that retrieval and prompt construction still work after changes.
- Bugs like irrelevant Apple CEO retrieval can be caught automatically.

---

## Milestone 10 — FastAPI Backend

Status: Complete, basic version

Goal: Turn the local RAG logic into a backend service.

Completed work:

- Added `src/api.py` with a FastAPI app.
- `GET /health` — reports whether the vector store is loaded and how many
  chunks are indexed. Always responds even if the index isn't loaded yet.
- `GET /documents` — lists indexed source files and their chunk counts.
- `POST /ask` — retrieval + grounded prompt, with optional fields to
  generate a real answer (`generate_answer`, `llm_provider`,
  `allow_remote_llm`), and optional debug/raw-prompt output (`debug`,
  `show_prompt`), matching what the CLI already supports. Responses are
  structured JSON (source, location, relevance label, score, quote) rather
  than the CLI's printed text reports, so a future frontend can consume
  them directly.
- Vector store and embedding model are loaded once at startup via a
  FastAPI lifespan handler, not per-request — same reasoning as the CLI's
  persistent runtime (Milestone 6).
- If no index exists yet, the server still starts; `/ask` and
  `/documents` return `503` with a clear message instead of crashing.
- Verified live: started the server with `uvicorn`, and hit `/health`,
  `/documents`, and `/ask` over real HTTP against the actual indexed
  Harry Potter/sample documents — correct sources, correct relevance
  labels, correct citations.
- Added `tests/test_api.py` (7 tests) using FastAPI's `TestClient` with an
  injected in-memory retriever (via `Depends`/`dependency_overrides`), so
  API tests don't depend on the real `data/vector_store` being present or
  make any network/LLM calls.

Not yet done:

- Upload/index endpoints (planned for Milestone 12, alongside the file
  upload UI).
- No debug-output-only endpoint; `debug`/`show_prompt` are fields on the
  `/ask` request instead of separate endpoints, since they always need
  the same retrieval to already have happened.

Done means:

- A local server can receive questions. — Achieved.
- The backend can return answers, sources, and optional debug
  information. — Achieved.
- PowerShell is no longer the main user interaction layer. — Achieved for
  API access; a browser-based UI is still Milestone 11.

---

## Milestone 11 — Basic User Interface

Status: Complete, basic version

Goal: Build a user-facing interface for asking questions and reading sourced answers.

Completed work:

- Added `src/static/index.html`, a single self-contained page (inline CSS
  and JS, no external requests, no build step) served by FastAPI at `/`.
- Question box, Ask button, Enter-to-submit.
- Displays sources: file, location, relevance label (color-coded), score,
  quote.
- "Generate answer" checkbox with provider select (none/gemini/local) and
  an "allow remote LLM" checkbox, mirroring the CLI/API flags.
- Insufficient-context and error states shown clearly instead of failing
  silently.
- Footer shows live index status via `/health`.
- Added `src/desktop_app.py`: wraps the same page in a native window via
  `pywebview` instead of a browser tab, so the app can be launched like a
  normal desktop program (`python -m src.desktop_app`). Starts the FastAPI
  server in a background thread, waits for `/health` to respond, then
  opens the window. No Electron/Chromium bundling — reuses the OS's own
  web renderer.
- Verified live: loaded the page in Chrome, ran the full golden path
  (relevant question, unrelated/insufficient-context question, generate
  answer with `none` provider), confirmed correct sources/labels/citations
  and no console errors. Verified the desktop wrapper starts the server,
  waits for readiness, and creates a real OS-level window (confirmed via
  window handle, title, and on-screen bounds).

Not yet done:

- Debug/raw-prompt toggles exist in the API but aren't exposed in the UI
  yet (only `generate_answer`/`llm_provider`/`allow_remote_llm`).
- No packaging/installer for the desktop app yet (still run via
  `python -m src.desktop_app`, not a standalone .exe).

Done means:

- A normal user can ask questions without using PowerShell. — Achieved,
  via both the browser page and the desktop window.
- Answers and sources are displayed clearly. — Achieved.

---

## Milestone 12 — File Upload UI

Status: Complete, basic version

Goal: Add a user-friendly file upload flow.

Completed work:

- Added `POST /documents/upload` to `src/api.py`. Accepts one file
  (`.txt`, `.md`, `.pdf`), rejects anything else with a clear 400 error.
- Saved file goes into `data/sample_documents`, then the full document
  set is re-indexed (chosen over incremental indexing for simplicity —
  reuses the same chunking/embedding path as `index_documents.py`,
  reasoning trusted since Milestone 8/9). The already-loaded embedding
  model is reused instead of reloading it, consistent with the
  persistent-runtime pattern from Milestone 6.
- Upload UI added to `src/static/index.html`: a drag-and-drop zone that's
  also click-to-browse, upload status message, and a live chip list of
  indexed documents with per-file chunk counts.
- Endpoints made independently testable via dependency injection
  (`get_documents_dir`, `get_vector_store_dir`, `get_embedding_model`),
  matching the existing `get_retriever` pattern — tests never touch the
  real `data/sample_documents` or load the real embedding model.
- Added `python-multipart` (required by FastAPI for file uploads).
- Verified live in Chrome: uploaded a real `.txt` file via the file
  input, confirmed it appeared in the document chip list with the
  correct chunk count, confirmed the index total updated, then asked a
  question specific to the uploaded content and got it back as the top
  (HIGH relevance) source. Test artifact was removed afterward and the
  real index rebuilt back to its original 3 documents / 9 chunks.

Not yet done:

- No delete/remove-document action (not in original scope; would need
  its own milestone work if wanted later).
- Drag-and-drop was implemented but only click-to-browse was verified
  through actual OS-level automation (drag-and-drop was verified by
  code review of the same upload code path, not a simulated OS drag).

This is the milestone where the project starts to feel closer to a local NotebookLM-style application.

Done means:

- The user can upload files through the interface. — Achieved.
- The system indexes them. — Achieved.
- The user can ask questions about those files. — Achieved, verified live.

---

## Milestone 13 — Cost Control and Provider Safety

Status: Planned

Goal: Keep LLM usage controlled, safe, and predictable.

Planned work:

- Avoid calling paid APIs when no reliable sources were retrieved.
- Limit prompt size.
- Add provider configuration.
- Add optional token/cost visibility.
- Keep API keys out of Git.
- Prevent raw secrets from appearing in logs.

Done means:

- The system reduces unnecessary API calls.
- The user has better control over cost.
- Provider keys remain safe.

---

## Milestone 14 — Docker and Deployment Preparation

Status: Later

Goal: Prepare the project for easier setup and future deployment.

Planned work:

- Add Docker support.
- Document setup steps.
- Make the project easier to run on another machine.
- Decide whether deployment should remain local-first or support cloud hosting later.

Done means:

- The project can be started more consistently across environments.
- The setup is easier to reproduce.

---

## Milestone 15 — Portfolio Polish

Status: Later

Goal: Make the project presentable for a portfolio, employer, or client.

Planned work:

- Improve README.
- Add architecture diagram.
- Add screenshots.
- Add a short demo flow.
- Add limitations.
- Add future work.
- Explain local-first design.
- Explain retrieval, grounding, source display, and provider safety.

Done means:

- The project can be shown professionally.
- A reviewer can understand what was built, why it matters, and how it works.

---

## Recommended Development Order From Here

1. ~~Milestone 8 — Document Indexing Workflow~~ Done.
2. ~~Milestone 7B — Real LLM Provider Implementation~~ Done for
   Gemini and Ollama; OpenAI still a stub, not currently prioritized.
3. ~~Milestone 10 — FastAPI Backend~~ Done, basic version.
4. ~~Milestone 11 — Basic User Interface~~ Done, basic version (web
   page + desktop window wrapper).
5. ~~Milestone 12 — File Upload UI~~ Done, basic version.
6. Milestone 13 — Cost Control and Provider Safety
7. Milestone 14 — Docker and Deployment Preparation
8. Milestone 15 — Portfolio Polish

Ollama is intentionally on hold until local disk/RAM allows a model to be
pulled; work in the meantime should prefer items that don't depend on it
(as Milestones 10-12 mostly don't).

---

## Notes

The project is intentionally local-first.

The first product goal is not cloud deployment, accounts, payment, or a complex SaaS platform.

The first product goal is a reliable local RAG assistant that can:

- ingest local documents
- retrieve relevant source text
- reject insufficient context
- answer with grounded sources
- expose debug information for development
- later provide a simple user interface
