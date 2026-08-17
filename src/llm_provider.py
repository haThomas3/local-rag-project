from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from src.config import (
    ALLOW_PAID_API_CALLS,
    GEMINI_API_KEY,
    GEMINI_API_KEY_SET,
    GEMINI_MODEL,
    LLM_PROVIDER,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT_SECONDS,
    OPENAI_API_KEY_SET,
)


SUPPORTED_LLM_PROVIDERS = {"none", "local", "gemini", "openai"}


@dataclass(frozen=True)
class LLMGenerationResult:
    provider: str
    answer: str
    status: str
    used_remote_api: bool


def normalize_provider(provider: str | None = None) -> str:
    selected_provider = (provider or LLM_PROVIDER).strip().lower()

    if selected_provider not in SUPPORTED_LLM_PROVIDERS:
        supported = ", ".join(sorted(SUPPORTED_LLM_PROVIDERS))
        raise ValueError(
            f"Unsupported LLM provider: {selected_provider}. "
            f"Supported providers: {supported}"
        )

    return selected_provider


def generate_answer_from_prompt(
    prompt: str,
    provider: str | None = None,
    allow_remote_api_calls: bool | None = None,
) -> LLMGenerationResult:
    if not prompt.strip():
        raise ValueError("prompt cannot be empty.")

    selected_provider = normalize_provider(provider)
    remote_api_calls_allowed = (
        ALLOW_PAID_API_CALLS
        if allow_remote_api_calls is None
        else allow_remote_api_calls
    )

    if selected_provider == "none":
        return LLMGenerationResult(
            provider=selected_provider,
            answer=(
                "LLM generation is disabled. The system can still retrieve sources "
                "and build a grounded prompt without calling a paid API."
            ),
            status="disabled",
            used_remote_api=False,
        )

    if selected_provider == "local":
        request_body = json.dumps(
            {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
        ).encode("utf-8")
        request = urllib.request.Request(
            f"{OLLAMA_BASE_URL}/api/generate",
            data=request_body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request, timeout=OLLAMA_TIMEOUT_SECONDS
            ) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError:
            return LLMGenerationResult(
                provider=selected_provider,
                answer=(
                    f"Local Ollama server is not reachable at {OLLAMA_BASE_URL}. "
                    "Start it with `ollama serve` and make sure the model "
                    f"'{OLLAMA_MODEL}' is pulled with `ollama pull {OLLAMA_MODEL}`."
                ),
                status="ollama_unavailable",
                used_remote_api=False,
            )
        except Exception as exc:  # malformed response, bad model name, etc.
            return LLMGenerationResult(
                provider=selected_provider,
                answer=f"Local Ollama request failed: {exc}",
                status="error",
                used_remote_api=False,
            )

        answer_text = (payload.get("response") or "").strip()

        if not answer_text:
            return LLMGenerationResult(
                provider=selected_provider,
                answer="Ollama returned an empty response.",
                status="empty_response",
                used_remote_api=False,
            )

        return LLMGenerationResult(
            provider=selected_provider,
            answer=answer_text,
            status="ok",
            used_remote_api=False,
        )

    if selected_provider == "gemini":
        if not GEMINI_API_KEY_SET:
            return LLMGenerationResult(
                provider=selected_provider,
                answer="Gemini generation is unavailable because GEMINI_API_KEY is not set.",
                status="missing_api_key",
                used_remote_api=False,
            )

        if not remote_api_calls_allowed:
            return LLMGenerationResult(
                provider=selected_provider,
                answer=(
                    "Gemini generation is blocked because ALLOW_PAID_API_CALLS=false. "
                    "This prevents accidental paid API usage."
                ),
                status="blocked_by_cost_guard",
                used_remote_api=False,
            )

        try:
            from google import genai

            client = genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.generate_content(
                model=GEMINI_MODEL, contents=prompt
            )
            answer_text = (response.text or "").strip()
        except Exception as exc:
            return LLMGenerationResult(
                provider=selected_provider,
                answer=f"Gemini request failed: {exc}",
                status="error",
                used_remote_api=True,
            )

        if not answer_text:
            return LLMGenerationResult(
                provider=selected_provider,
                answer="Gemini returned an empty response.",
                status="empty_response",
                used_remote_api=True,
            )

        return LLMGenerationResult(
            provider=selected_provider,
            answer=answer_text,
            status="ok",
            used_remote_api=True,
        )

    if selected_provider == "openai":
        if not OPENAI_API_KEY_SET:
            return LLMGenerationResult(
                provider=selected_provider,
                answer="OpenAI generation is unavailable because OPENAI_API_KEY is not set.",
                status="missing_api_key",
                used_remote_api=False,
            )

        if not remote_api_calls_allowed:
            return LLMGenerationResult(
                provider=selected_provider,
                answer=(
                    "OpenAI generation is blocked because ALLOW_PAID_API_CALLS=false. "
                    "This prevents accidental paid API usage."
                ),
                status="blocked_by_cost_guard",
                used_remote_api=False,
            )

        return LLMGenerationResult(
            provider=selected_provider,
            answer="OpenAI provider is configured but API calling is not implemented yet.",
            status="not_implemented",
            used_remote_api=False,
        )

    raise AssertionError(f"Unhandled provider: {selected_provider}")
