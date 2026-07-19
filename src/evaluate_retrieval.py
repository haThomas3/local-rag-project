from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.config import PROJECT_ROOT, VECTOR_STORE_DIR
from src.prompt_builder import filter_reliable_results
from src.retriever import LocalRetriever, build_retriever_from_store


DEFAULT_CASES_PATH = (
    PROJECT_ROOT
    / "evaluation"
    / "harry_potter_retrieval_cases.json"
)


def load_cases(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Evaluation file not found: {path}")

    cases = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(cases, list) or not cases:
        raise ValueError("Evaluation file must contain a non-empty list.")

    return cases


def evaluate_case(
    retriever: LocalRetriever,
    case: dict,
    top_k: int,
) -> dict:
    results = retriever.retrieve(case["question"], top_k=top_k)
    case_type = case["case_type"]

    if case_type == "answerable":
        expected_source = case["expected_source"]

        matching_results = [
            result
            for result in results
            if result.chunk.metadata.source == expected_source
        ]

        matching_text = " ".join(
            result.chunk.text for result in matching_results
        ).lower()

        missing_terms = [
            term
            for term in case["expected_terms"]
            if term.lower() not in matching_text
        ]

        passed = bool(matching_results) and not missing_terms

        if not matching_results:
            reason = f"Expected source not found: {expected_source}"
        elif missing_terms:
            reason = f"Missing expected terms: {missing_terms}"
        else:
            reason = "Expected source and terms were retrieved."

    elif case_type == "unsupported_in_domain":
        expected_source = case["expected_source"]
        source_found = any(
            result.chunk.metadata.source == expected_source
            for result in results
        )

        passed = source_found

        if passed:
            reason = (
                "Related source was retrieved. "
                "Answer-level refusal must be evaluated separately."
            )
        else:
            reason = f"Related source not found: {expected_source}"

    elif case_type == "out_of_scope":
        reliable_results = filter_reliable_results(results)
        passed = len(reliable_results) == 0

        if passed:
            reason = "No retrieved result passed the relevance gate."
        else:
            sources = sorted(
                {
                    result.chunk.metadata.source
                    for result in reliable_results
                }
            )
            reason = f"Unexpected reliable results: {sources}"

    else:
        raise ValueError(f"Unsupported case type: {case_type}")

    return {
        "id": case["id"],
        "case_type": case_type,
        "question": case["question"],
        "passed": passed,
        "reason": reason,
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate local retrieval using saved test cases."
    )
    parser.add_argument(
        "--cases",
        type=Path,
        default=DEFAULT_CASES_PATH,
        help="Path to the evaluation JSON file.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of chunks retrieved for each question.",
    )
    args = parser.parse_args()

    cases = load_cases(args.cases)
    retriever, chunks = build_retriever_from_store(VECTOR_STORE_DIR)

    print("LOCAL RETRIEVAL EVALUATION")
    print("==========================")
    print(f"Cases: {len(cases)}")
    print(f"Indexed chunks: {len(chunks)}")
    print(f"Top K: {args.top_k}")
    print()

    passed_count = 0

    for case in cases:
        outcome = evaluate_case(retriever, case, args.top_k)
        status = "PASS" if outcome["passed"] else "FAIL"

        if outcome["passed"]:
            passed_count += 1

        print(f"[{status}] {outcome['id']} ({outcome['case_type']}): {outcome['question']}")
        print(f"Reason: {outcome['reason']}")

        if outcome["results"]:
            top_result = outcome["results"][0]
            print(
                "Top result: "
                f"{top_result.chunk.metadata.source} "
                f"(score={top_result.score:.4f})"
            )

        print()

    failed_count = len(cases) - passed_count

    print("SUMMARY")
    print("=======")
    print(f"Passed: {passed_count}/{len(cases)}")
    print(f"Failed: {failed_count}/{len(cases)}")

    raise SystemExit(0 if failed_count == 0 else 1)


if __name__ == "__main__":
    main()
