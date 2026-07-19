from __future__ import annotations

from dataclasses import dataclass

from src.config import (
    ALLOW_PAID_API_CALLS,
    GEMINI_API_KEY_SET,
    LLM_PROVIDER,
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
) -> LLMGenerationResult:
    if not prompt.strip():
        raise ValueError("prompt cannot be empty.")

    selected_provider = normalize_provider(provider)

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
        return LLMGenerationResult(
            provider=selected_provider,
            answer=(
                "Local LLM generation is not connected yet. This mode is reserved "
                "for a future local provider such as LM Studio or Ollama."
            ),
            status="not_implemented",
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

        if not ALLOW_PAID_API_CALLS:
            return LLMGenerationResult(
                provider=selected_provider,
                answer=(
                    "Gemini generation is blocked because ALLOW_PAID_API_CALLS=false. "
                    "This prevents accidental paid API usage."
                ),
                status="blocked_by_cost_guard",
                used_remote_api=False,
            )

        return LLMGenerationResult(
            provider=selected_provider,
            answer="Gemini provider is configured but API calling is not implemented yet.",
            status="not_implemented",
            used_remote_api=False,
        )

    if selected_provider == "openai":
        if not OPENAI_API_KEY_SET:
            return LLMGenerationResult(
                provider=selected_provider,
                answer="OpenAI generation is unavailable because OPENAI_API_KEY is not set.",
                status="missing_api_key",
                used_remote_api=False,
            )

        if not ALLOW_PAID_API_CALLS:
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
