# Local RAG Project

Local RAG Project is a Python-based Retrieval-Augmented Generation system for asking questions over local documents.

The project is designed as a local-first system. Early development focuses on running everything on a personal machine before moving to paid infrastructure or cloud deployment.

## Project Goal

The goal is to build a system that can:

- Load local documents
- Split documents into searchable chunks
- Create embeddings
- Store document chunks in a local vector database
- Retrieve relevant context for a user question
- Generate an answer using an LLM
- Show the sources used for the answer

## Local-First Development

The project is intentionally built locally first to reduce cost and complexity.

Future versions may include server deployment, user accounts, a web interface, cloud storage, and paid infrastructure.

## LLM Providers

The system supports configurable LLM providers, selected with `LLM_PROVIDER`
in `.env` or with `--llm-provider` per run.

- `none` (default) — no generation, retrieval and grounded prompt only.
- `gemini` — real, working. Remote and paid, so it is blocked unless you
  explicitly pass `--allow-remote-llm` for that run, even if
  `GEMINI_API_KEY` is set in `.env`.
- `local` — real, working, talks to a locally running
  [Ollama](https://ollama.com) server (`OLLAMA_BASE_URL`, default
  `http://localhost:11434`). This is the intended default for normal use:
  free, fully offline, no API key needed. Requires `ollama serve` running
  and a model pulled (`ollama pull <model>`, matching `OLLAMA_MODEL` in
  `.env`, default `llama3.1`). If Ollama isn't running or no model has
  been pulled, it fails with a clear message instead of crashing.
- `openai` — not implemented yet, returns a stub response.

A future comparison mode may return answers from more than one provider
side by side.

API keys must be stored locally in a `.env` file, never committed.

## Security

Never commit API keys or private data.

The .env file is ignored by Git and should stay local.

Use .env.example as a template for required environment variables.

## Project Structure

- src: Python source code
- docs: Project documentation
- data/sample_documents: Sample documents for local testing
- notebooks: Experiments and exploration

## Current Development Focus

The current focus is building a minimal local RAG pipeline before adding product features or cloud infrastructure.

## Index local documents

Place supported `.txt`, `.md`, or `.pdf` files in `data/sample_documents`.

Build or rebuild the local index:

```powershell
python -m src.index_documents
```

Query the saved local index (retrieval and grounded prompt only, no LLM call):

```powershell
python -m src.rag_cli
```

Query and generate a real answer with Gemini for one run only:

```powershell
python -m src.rag_cli --generate-answer --llm-provider gemini --allow-remote-llm
```

Query and generate a real answer fully offline with a local Ollama model
(requires `ollama serve` running and a model pulled):

```powershell
python -m src.rag_cli --generate-answer --llm-provider local
```

Generated FAISS files are stored in `data/vector_store` and are ignored by Git.

Document indexing uses local embeddings and does not call Gemini, OpenAI, or another remote LLM provider.
