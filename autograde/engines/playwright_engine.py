from pathlib import Path

from playwright.sync_api import (
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError,
    sync_playwright,
)
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
            "expect_request": self.do_expect_request,
        }


    # =========================
    # ACTIONS
    # =========================

    def do_fill(self, page, action, inputs):

        value = action["value"]

        if isinstance(value, str) and value.startswith("$"):
            variable = value[1:]
            value = inputs[variable]

        page.fill(
            action["selector"],
            str(value)
        )


    def do_click(self, page, action, inputs):

        page.click(
            action["selector"]
        )


    def do_wait(self, page, action, inputs):

        page.wait_for_timeout(
            action["milliseconds"]
        )


    # =========================
    # EXPECTATIONS
    # =========================

    def do_expect_text(self, context, action):

        page = context["page"]

        selector = action["selector"]
        expected = action["equals"]

        actual = page.locator(selector).text_content()

        print(f"Expected: {expected}")
        print(f"Actual  : {actual}")

        return actual == expected


    def do_expect_console(self, context, action):

        messages = context["messages"]

        expected = action["equals"]

        if not messages:
            print(f"Expected: {expected}")
            print("Actual  : <no console messages>")

            return False

        actual = messages[-1]

        print(f"Expected: {expected}")
        print(f"Actual  : {actual}")

        return actual == expected


    def do_expect_request(self, context, action):

        requests = context["requests"]

        expected_method = action["method"]
        expected_url = action["url_contains"]

        print("=== Requests ===")

        for request in requests:
            print(
                request.method,
                request.url
            )

        print(
            f"Expected method: '{expected_method}'"
        )

        print(
            f"Expected URL   : '{expected_url}'"
        )

        for request in requests:

            method_match = (
                request.method == expected_method
            )

            url_match = (
                expected_url in request.url
            )

            print(
                f"Actual method  : '{request.method}'"
            )

            print(
                f"Actual URL     : '{request.url}'"
            )

            print(
                f"Method match   : {method_match}"
            )

            print(
                f"URL match      : {url_match}"
            )

            if method_match and url_match:

                print("MATCH!")

                return True

        print("NO MATCH")

        return False


    # =========================
    # ACTION EXECUTION
    # =========================

    def run_action(self, context, action):

        page = context["page"]
        inputs = context["inputs"]

        action_name = next(iter(action))

        self.handlers[action_name](
            page,
            action[action_name],
            inputs
        )


    # =========================
    # EXPECTATION EXECUTION
    # =========================

    def execute_expectation(self, context, test):

        expectation_name = next(
            key
            for key in test.keys()
            if key.startswith("expect_")
        )

        return self.expectations[expectation_name](
            context,
            test[expectation_name]
        )


    # =========================
    # GRADING
    # =========================

    def grade(self, assignment, submission_folder):

        html_file = (
            Path(submission_folder)
            / assignment["entry"]
        )

        html = html_file.resolve().as_uri()

        results = []

        score = 0
        max_score = 0

        with sync_playwright() as p:

            browser_name = assignment.get(
                "browser",
                "chromium"
            )

            if browser_name == "chromium":

                browser = p.chromium.launch(
                    headless=assignment.get(
                        "headless",
                        False
                    )
                )

            elif browser_name == "firefox":

                browser = p.firefox.launch(
                    headless=assignment.get(
                        "headless",
                        False
                    )
                )

            elif browser_name == "webkit":

                browser = p.webkit.launch(
                    headless=assignment.get(
                        "headless",
                        False
                    )
                )

            else:

                raise ValueError(
                    f"Unknown browser: {browser_name}"
                )


            # =========================
            # EACH TEST GETS A NEW PAGE
            # =========================

            for test in assignment["testcases"]:

                page = browser.new_page()

                # Student exercises are local HTML files. If an expected
                # element is missing, fail quickly rather than waiting 30s.
                page.set_default_timeout(5000)

                messages = []
                requests = []

                page.on(
                    "console",
                    lambda msg: messages.append(
                        msg.text
                    )
                )

                page.on(
                    "pageerror",
                    lambda err: print(
                        f"JavaScript Error: {err}"
                    )
                )

                page.on(
                    "request",
                    lambda request: requests.append(
                        request
                    )
                )

                passed = False

                try:

                    print(
                        f"GET {html}"
                    )

                    page.goto(
                        html,
                        timeout=5000,
                    )

                    context = {
                        "page": page,
                        "messages": messages,
                        "requests": requests,
                        "inputs": test.get(
                            "inputs",
                            {}
                        )
                    }

                    # =========================
                    # RUN TEST ACTIONS
                    # =========================

                    for action in test["actions"]:

                        self.run_action(
                            context,
                            action
                        )

                    # =========================
                    # CHECK EXPECTATION
                    # =========================

                    passed = self.execute_expectation(
                        context,
                        test
                    )

                except PlaywrightTimeoutError as error:

                    print(
                        f"Test failed: Playwright timeout: {error}"
                    )

                    passed = False

                except PlaywrightError as error:

                    print(
                        f"Test failed: Playwright error: {error}"
                    )

                    passed = False

                finally:

                    # =========================
                    # SCORE
                    # =========================

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

                    page.close()


            # =========================
            # KEEP BROWSER OPEN
            # =========================

            if not assignment.get(
                "headless",
                False
            ):

                input(
                    "Press ENTER..."
                )


            browser.close()


        # =========================
        # RETURN RESULT
        # =========================

        return GradeResult(
            score=score,
            max_score=max_score,
            tests=results
        )