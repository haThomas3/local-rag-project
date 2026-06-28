from pathlib import Path
import os
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
SAMPLE_DOCUMENTS_DIR = DATA_DIR / "sample_documents"
VECTOR_DB_DIR = PROJECT_ROOT / "vector_db"

load_dotenv(PROJECT_ROOT / ".env")


def _has_real_value(value: str | None) -> bool:
    if value is None:
        return False

    cleaned = value.strip()

    if not cleaned:
        return False

    placeholder_values = {
        "your_openai_key_here",
        "your_gemini_key_here",
        "put_your_real_key_here",
    }

    return cleaned not in placeholder_values


LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").strip().lower()
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "local").strip().lower()

OPENAI_API_KEY_SET = _has_real_value(os.getenv("OPENAI_API_KEY"))
GEMINI_API_KEY_SET = _has_real_value(os.getenv("GEMINI_API_KEY"))


def print_config_summary() -> None:
    print("Project root:", PROJECT_ROOT)
    print("Sample documents dir:", SAMPLE_DOCUMENTS_DIR)
    print("Vector DB dir:", VECTOR_DB_DIR)
    print("LLM provider:", LLM_PROVIDER)
    print("Embedding provider:", EMBEDDING_PROVIDER)
    print("OpenAI API key set:", OPENAI_API_KEY_SET)
    print("Gemini API key set:", GEMINI_API_KEY_SET)
