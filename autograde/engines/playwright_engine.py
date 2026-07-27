from pathlib import Path

from playwright.sync_api import sync_playwright

from autograde.models import GradeResult, TestResult

class PlaywrightEngine:

    def grade(self, assignment, submission_folder):

        html_file = Path(submission_folder) / assignment["entry"]

        html = html_file.resolve().as_uri()

        results = []

        score = 0
        max_score = 0

        with sync_playwright() as p:

            browser = p.chromium.launch(headless=False)

            page = browser.new_page()

            messages = []

            page.on(
                "console",
                lambda msg: messages.append(msg.text)
            )

            page.goto(html)

            for test in assignment["tests"]:

                for action in test["actions"]:

                    if "fill" in action:

                        selector = action["fill"]["selector"]
                        value = action["fill"]["value"]

                        page.fill(selector, value)

                    if "click" in action:

                        selector = action["click"]["selector"]

                        page.click(selector)

            expected = test["expect_console"]

            actual = messages[-1]

            print(f"Expected: {expected}")
            print(f"Actual  : {actual}")

            passed = (actual == expected)

            print("PASS" if passed else "FAIL")

            max_score += test["points"]

            if passed:
                score += test["points"]

            results.append(
                TestResult(
                    name=test["name"],
                    passed=passed,
                    points=test["points"]
                )
            )

            input("Press ENTER...")

            browser.close()

        return GradeResult(
            score=score,
            max_score=max_score,
            tests=results
        )