from __future__ import annotations

from src.config import print_config_summary
from src.llm_provider import generate_answer_from_prompt


def main() -> None:
    prompt = "Answer using only retrieved context."

    print_config_summary()
    print()

    for provider in ["none", "local", "gemini", "openai"]:
        result = generate_answer_from_prompt(prompt, provider=provider)

        print(f"Provider: {result.provider}")
        print(f"Status: {result.status}")
        print(f"Used remote API: {result.used_remote_api}")
        print(f"Answer: {result.answer}")
        print()


if __name__ == "__main__":
    main()
