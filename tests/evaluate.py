import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from app.evaluator import evaluate_grounding
from app.llm_service import generate_ticket


def load_requirements():
    file_path = Path(__file__).parent / "test_requirements.json"

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_results(results):
    output_path = (
        Path(__file__).parent / "evaluation_results.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(f"\nResults saved to: {output_path}")


def evaluate():

    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set"
        )

    client = genai.Client(
        api_key=api_key
    )

    requirements = load_requirements()

    total = len(requirements)

    successful = 0
    issue_type_correct = 0

    grounding_successful = 0
    grounding_passed = 0

    results = []

    print("\n")
    print("=" * 60)
    print("LLM TICKET GENERATION EVALUATION")
    print("=" * 60)

    for item in requirements:

        requirement_id = item["id"]
        requirement = item["requirement"]
        expected_issue_type = item["expected_issue_type"]

        print(f"\n{requirement_id}")
        print("-" * 60)
        print(f"Requirement: {requirement}")

        result = {
            "id": requirement_id,
            "requirement": requirement,
            "expected_issue_type": expected_issue_type,
            "generation_success": False,
            "issue_type": None,
            "issue_type_correct": False,
            "priority": None,
            "summary": None,
            "acceptance_criteria": [],
            "labels": [],
            "grounded": None,
            "unsupported_items": [],
            "grounding_error": None,
        }

        try:

            ticket = generate_ticket(
                requirement
            )

            successful += 1

            result["generation_success"] = True
            result["issue_type"] = ticket.issue_type
            result["priority"] = ticket.priority
            result["summary"] = ticket.summary
            result["acceptance_criteria"] = (
                ticket.acceptance_criteria
            )
            result["labels"] = ticket.labels

            print(
                f"Summary: {ticket.summary}"
            )

            print(
                f"Issue Type: {ticket.issue_type}"
            )

            print(
                f"Expected: {expected_issue_type}"
            )

            if (
                ticket.issue_type
                == expected_issue_type
            ):

                issue_type_correct += 1

                result["issue_type_correct"] = True

                print(
                    "Issue Type: CORRECT"
                )

            else:

                print(
                    "Issue Type: INCORRECT"
                )

            print(
                f"Priority: {ticket.priority}"
            )

            print("Acceptance Criteria:")

            for criterion in (
                ticket.acceptance_criteria
            ):

                print(
                    f"  - {criterion}"
                )

            print(
                f"Labels: "
                f"{', '.join(ticket.labels)}"
            )

            # --------------------------------------------------
            # Grounding evaluation
            # --------------------------------------------------

            try:

                grounding = evaluate_grounding(
                    client,
                    requirement,
                    ticket
                )

                grounding_successful += 1

                result["grounded"] = (
                    grounding.grounded
                )

                result["unsupported_items"] = (
                    grounding.unsupported_items
                )

                if grounding.grounded:

                    grounding_passed += 1

                    print(
                        "Grounding: PASS"
                    )

                else:

                    print(
                        "Grounding: FAIL"
                    )

                    print(
                        "Unsupported items:"
                    )

                    for unsupported_item in (
                        grounding.unsupported_items
                    ):

                        print(
                            f"  - "
                            f"{unsupported_item}"
                        )

            except Exception as error:

                result["grounding_error"] = (
                    str(error)
                )

                print(
                    "Grounding: ERROR"
                )

                print(
                    f"Error: {error}"
                )

            print("Status: PASS")

        except Exception as error:

            print("Status: FAIL")

            print(
                f"Error: {error}"
            )

            result["generation_error"] = (
                str(error)
            )

        results.append(result)

    # ----------------------------------------------------------
    # Calculate metrics
    # ----------------------------------------------------------

    structured_output_success_rate = (
        successful / total * 100
        if total > 0
        else 0
    )

    issue_type_accuracy = (
        issue_type_correct / successful * 100
        if successful > 0
        else 0
    )

    grounding_accuracy = (
        grounding_passed
        / grounding_successful
        * 100
        if grounding_successful > 0
        else 0
    )

    # ----------------------------------------------------------
    # Summary
    # ----------------------------------------------------------

    evaluation_summary = {
        "total_requirements": total,
        "successful": successful,
        "failed": total - successful,
        "structured_output_success_rate": round(
            structured_output_success_rate,
            1
        ),
        "issue_type_accuracy": round(
            issue_type_accuracy,
            1
        ),
        "grounding_accuracy": round(
            grounding_accuracy,
            1
        ),
    }

    output = {
        "summary": evaluation_summary,
        "results": results,
    }

    print("\n")
    print("=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)

    print(
        f"Total requirements: "
        f"{total}"
    )

    print(
        f"Successful: "
        f"{successful}"
    )

    print(
        f"Failed: "
        f"{total - successful}"
    )

    print(
        f"Structured output success rate: "
        f"{structured_output_success_rate:.1f}%"
    )

    print(
        f"Issue type accuracy: "
        f"{issue_type_accuracy:.1f}%"
    )

    print(
        f"Grounding accuracy: "
        f"{grounding_accuracy:.1f}%"
    )

    save_results(output)


if __name__ == "__main__":
    evaluate()