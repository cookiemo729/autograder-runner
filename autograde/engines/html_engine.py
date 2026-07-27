from bs4 import BeautifulSoup
from pathlib import Path

from autograde.models import TestResult, GradeResult


class HtmlEngine:

    def grade(self, assignment, submission_folder):

        html_file = Path(submission_folder) / assignment["entry"]
        
        with open(html_file, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "lxml")

        results = []

        score = 0
        max_score = 0

        for test in assignment["tests"]:

            passed = False

            action = test["action"]

            if "exists" in action:

                selector = action["exists"]["selector"]

                passed = soup.select_one(selector) is not None

            if "attribute" in action:

                selector = action["attribute"]["selector"]
                attribute = action["attribute"]["name"]

                element = soup.select_one(selector)

                passed = (
                    element is not None
                    and element.has_attr(attribute)
                )

            if passed:
                score += test["points"]

            max_score += test["points"]

            results.append(
                TestResult(
                    name=test["name"],
                    passed=passed,
                    points=test["points"]
                )
            )

        return GradeResult(
            score=score,
            max_score=max_score,
            tests=results
        )