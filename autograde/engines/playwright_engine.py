from pathlib import Path

from playwright.sync_api import sync_playwright

from autograde.models import GradeResult, TestResult

class PlaywrightEngine:

    def __init__(self):
        self.handlers = {
            "fill": self.do_fill,
            "click": self.do_click,
            "wait": self.do_wait,
        }

        self.expectations = {
            "expect_console": self.do_expect_console,
            "expect_text": self.do_expect_text,
        }

    def resolve(self, value, inputs):

        if isinstance(value, str) and value.startswith("$"):
            return inputs[value[1:]]

        return value

    def do_fill(self, context, action):
        page = context["page"]
        inputs = context["inputs"]

        value = self.resolve(
            action["value"],
            inputs
        )

        page.fill(
            action["selector"],
            value
        )


    def do_click(self, context, action):

        page = context["page"]

        page.click(
            action["selector"]
        )

    def do_wait(self, page, action, inputs):

        page.wait_for_timeout(
            action["milliseconds"]
        )

    def do_expect_text(self, page, action, inputs):

        selector = action["selector"]
        expected = action["equals"]

        actual = page.locator(selector).text_content()

        return actual == expected

    def do_expect_console(self, page, action, messages):

        expected = action["equals"]

        actual = messages[-1]

        print(f"Expected: {expected}")
        print(f"Actual  : {actual}")

        return actual == expected

    def run_action(self, context, action):

        action_name = next(iter(action))

        self.handlers[action_name](
            context,
            action[action_name]
        )

    def execute_expectation(self, page, test, messages):

        expectation_name = next(
            key for key in test.keys()
            if key.startswith("expect_")
        )

        return self.expectations[expectation_name](
            page,
            test[expectation_name],
            messages
        )

    def grade(self, assignment, submission_folder):

        html_file = Path(submission_folder) / assignment["entry"]

        html = html_file.resolve().as_uri()

        results = []

        score = 0
        max_score = 0

        with sync_playwright() as p:

            browser_name = assignment.get("browser", "chromium")

            if browser_name == "chromium":
                browser = p.chromium.launch(
                    headless=assignment.get("headless", False)
                )
            elif browser_name == "firefox":
                browser = p.firefox.launch(
                    headless=assignment.get("headless", False)
                )
            elif browser_name == "webkit":
                browser = p.webkit.launch(
                    headless=assignment.get("headless", False)
                )
            else:
                raise ValueError(f"Unknown browser: {browser_name}")

            page = browser.new_page()

            messages = []

            page.on(
                "console",
                lambda msg: messages.append(msg.text)
            )

            page.goto(html)

            context = {
                "page": page,
                "messages": messages,
            }

            for test in assignment["testcases"]:

                messages.clear()

                context["inputs"] = test["inputs"]

                for action in assignment["actions"]:
                    self.run_action(
                        context,
                        action
                    )

                passed = self.execute_expectation(
                    page,
                    test,
                    messages
                )

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