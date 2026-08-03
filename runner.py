import argparse
import json

from autograde.parser import load_assignment
from autograde.engine_factory import EngineFactory


def grade_assignment(assignment_path, submission_path):
    """
    Load an assignment and grade a submission.

    Returns:
        GradeResult
    """

    assignment = load_assignment(
        f"{assignment_path}/assignment.yml"
    )

    engine = EngineFactory.create(
        assignment["engine"]
    )

    result = engine.grade(
        assignment,
        submission_path
    )

    return assignment, result


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("assignment")

    parser.add_argument("submission")

    parser.add_argument(
        "--output",
        default="grade.json",
        help="Output JSON file"
    )

    args = parser.parse_args()

    assignment, result = grade_assignment(
        args.assignment,
        args.submission
    )

    print("===================================")
    print(" AutoGrade Runner")
    print("===================================")

    print()
    print(f"Title  : {assignment['title']}")
    print(f"Engine : {assignment['engine']}")
    print()

    print("Results")
    print("-------")

    for test in result.tests:

        if test.passed:
            print(f"✓ {test.name} ({test.points} pts)")
        else:
            print(f"✗ {test.name} (0/{test.points} pts)")

    print()
    print(f"Total: {result.score}/{result.max_score}")

    with open(args.output, "w", encoding="utf-8") as file:
        json.dump(
            {
                "score": result.score,
                "max_score": result.max_score,
                "tests": [
                    {
                        "name": test.name,
                        "passed": test.passed,
                        "points": test.points
                    }
                    for test in result.tests
                ]
            },
            file,
            indent=4
        )

    print()
    print(f"{args.output} generated.")


if __name__ == "__main__":
    main()