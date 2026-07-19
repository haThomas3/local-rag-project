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

- `db417f9 Add explicit remote LLM opt-in flag`

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

Status: In progress - safe provider scaffold complete; real provider implementation postponed

Goal: Connect the RAG prompt to an actual LLM provider.

Current checkpoint:

- 7A — Complete:
  - Cost-safe LLM provider scaffold exists.
  - Default provider is none.
  - Remote LLM calls are blocked by default.
  - CLI supports explicit per-run provider override.
  - CLI supports explicit remote opt-in using --allow-remote-llm.
  - Gemini/OpenAI/Ollama are not default dependencies for normal use.

- 7B — Still open:
  - Implement real Gemini provider for controlled development testing.
  - Later implement local provider through Ollama or LM Studio.
  - Keep OpenAI as an optional paid fallback only.
  - Verify that generated answers use only retrieved sources.
  - Test refusal behavior when the answer is not present in retrieved context.

Reason for postponing 7B:

- The local indexing workflow should be stabilized first.
- The project should not become dependent on Gemini before the local RAG pipeline is reliable.
- Gemini will be used later as a development helper, not as the project default.


Planned work:

- Add OpenAI provider support.
- Add Gemini provider support.
- Support provider selection through configuration.
- Optionally support comparison mode:
  - OpenAI answer
  - Gemini answer
  - same retrieved sources
- Keep all API keys in `.env`.
- Avoid sending questions to an LLM when retrieval confidence is too weak.

Done means:

- The system retrieves relevant sources.
- The system builds a grounded prompt.
- The selected LLM generates an answer.
- The answer includes source references.

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

Status: Planned

Goal: Add tests that verify whether the RAG system behaves correctly.

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

Status: Planned

Goal: Turn the local RAG logic into a backend service.

Planned work:

- Add FastAPI.
- Add an endpoint for asking questions.
- Add an endpoint for debug output.
- Add an endpoint for listing indexed documents.
- Later add upload/index endpoints.
- Keep the model and vector store loaded in memory while the server runs.

Done means:

- A local server can receive questions.
- The backend can return answers, sources, and optional debug information.
- PowerShell is no longer the main user interaction layer.

---

## Milestone 11 — Basic User Interface

Status: Planned

Goal: Build a user-facing interface for asking questions and reading sourced answers.

Planned work:

- Add a simple frontend.
- Add a question box.
- Display the answer.
- Display source file, location, relevance, and quote.
- Hide technical debug information by default.
- Add a developer/debug mode if useful.

Done means:

- A normal user can ask questions without using PowerShell.
- Answers and sources are displayed clearly.

---

## Milestone 12 — File Upload UI

Status: Planned

Goal: Add a user-friendly file upload flow.

Planned work:

- Add PDF upload.
- Add `.txt` upload.
- Add `.md` upload.
- Add drag-and-drop support if practical.
- Add an `Index documents` action.
- Show which files were uploaded and indexed.
- Allow asking questions about uploaded files.

This is the milestone where the project starts to feel closer to a local NotebookLM-style application.

Done means:

- The user can upload files through the interface.
- The system indexes them.
- The user can ask questions about those files.

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

1. Milestone 8 — Document Indexing Workflow
2. Milestone 7B — Real LLM Provider Implementation
3. Milestone 9 — Evaluation Suite
4. Milestone 10 — FastAPI Backend
5. Milestone 11 — Basic User Interface
6. Milestone 12 — File Upload UI
7. Milestone 13 — Cost Control and Provider Safety
8. Milestone 14 — Docker and Deployment Preparation
9. Milestone 15 — Portfolio Polish

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
