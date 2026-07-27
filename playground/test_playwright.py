from playwright.sync_api import sync_playwright
from pathlib import Path

html = Path("playground/wk1exercise3.html").resolve().as_uri()


def run_test(page, num1, num2, expected):

    messages = []

    page.on(
        "console",
        lambda msg: messages.append(msg.text)
    )

    page.goto(html)

    page.fill("#num1", str(num1))
    page.fill("#num2", str(num2))

    page.click("button")

    actual = messages[0]

    print("-----------------------")
    print(f"Input    : {num1}, {num2}")
    print(f"Expected : {expected}")
    print(f"Actual   : {actual}")

    if actual == expected:
        print("✓ PASS")
    else:
        print("✗ FAIL")


with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    page = browser.new_page()

    run_test(page, 2, 3, "5")

    run_test(page, 10, 20, "30")

    browser.close()