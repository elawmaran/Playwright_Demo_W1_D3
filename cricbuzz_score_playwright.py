
# Task 1: Capture Live Cricket Score with Playwright
# File: cricbuzz_score.py

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from datetime import datetime
from pathlib import Path
import re

START_URL = (
    "https://www.cricbuzz.com/cricket-series/"
    "12398/ranji-trophy-elite-2026-27/matches"
)

LIVE_SCORES_URL = (
    "https://www.cricbuzz.com/cricket-match/live-scores"
)

OUTPUT_DIR = Path.cwd()
SCREENSHOT_PATH = OUTPUT_DIR / "score.png"
REPORT_PATH = OUTPUT_DIR / "cricbuzz_score.txt"

print("Starting Cricbuzz Playwright automation...")
print(f"Started at: {datetime.now()}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page(
        viewport={"width": 1440, "height": 1000}
    )

    try:
        # STEP 1: Open the Ranji Trophy matches page
        response = page.goto(
            START_URL,
            wait_until="domcontentloaded",
            timeout=10000
        )

        if response:
            print(f"Page response: HTTP {response.status}")

        page.locator("body").wait_for(state="visible")

        # STEP 2: Navigate using the inspected Live Scores link
        live_link = page.locator(
            'a[title="Live Cricket Score"]'
        )

        if live_link.count() > 0:
            live_link.first.click()
            print("Clicked the Live Scores link.")

            try:
                page.wait_for_url(
                    "**/cricket-match/live-scores**",
                    timeout=10000
                )
            except PlaywrightTimeoutError:
                # If navigation did not complete, open the known URL.
                if "/cricket-match/live-scores" not in page.url:
                    page.goto(
                        LIVE_SCORES_URL,
                        wait_until="domcontentloaded",
                        timeout=10000   
                    )
        else:
            print("Link not found; opening Live Scores directly.")
            page.goto(
                LIVE_SCORES_URL,
                wait_until="domcontentloaded",
                timeout=10000
            )

        # STEP 3: Wait until cricket score-like content appears.
        # Common examples: 287/4, 123-5, 287-4.
        # This is a content check, not a fixed sleep.
        try:
            page.wait_for_function(
                """() => {
                    const text = document.body?.innerText || "";
                    return /\\b\\d{1,3}\\s*\\/\\s*\\d{1,2}\\b/.test(text)
                        || /\\b\\d{1,3}\\s*-\\s*\\d{1,2}\\b/.test(text);
                }""",
                timeout=10000
            )

            print("Score-like content detected.")

        except PlaywrightTimeoutError:
            print(
                "No score-like content appeared within 10 seconds. "
                "There may be no live match, or the page may not have loaded."
            )

        # STEP 4: Read the rendered page text
        page_text = page.locator("body").inner_text()

        # Keep lines containing likely score patterns and nearby context
        lines = [
            line.strip()
            for line in page_text.splitlines()
            if line.strip()
        ]

        score_pattern = re.compile(
            r"\b\d{1,3}\s*(?:/|-)\s*\d{1,2}\b"
        )

        score_indexes = [
            i for i, line in enumerate(lines)
            if score_pattern.search(line)
        ]

        if score_indexes:
            print("\n=== CRICBUZZ SCORE INFORMATION ===")

            # Include surrounding lines for team names and match status
            selected_lines = set()

            for index in score_indexes:
                for i in range(
                    max(0, index - 2),
                    min(len(lines), index + 3)
                ):
                    selected_lines.add(i)

            score_report = "\n".join(
                lines[i] for i in sorted(selected_lines)
            )

            print(score_report)

            status_message = "Score-like information found."
        else:
            score_report = (
                "No cricket score matching the expected patterns "
                "was detected.\n\n"
                "The page may contain scheduled matches, no live "
                "matches, or a different score format.\n\n"
                "Visible page text:\n\n" + page_text
            )

            print("\nNo matching score found.")
            print("Check the saved report for diagnostic information.")

            status_message = "No matching score detected."

        # STEP 5: Save the screenshot
        page.screenshot(
            path=str(SCREENSHOT_PATH),
            full_page=True,
            animations="disabled"
        )

        print(f"\nScreenshot saved: {SCREENSHOT_PATH}")

        # STEP 6: Save the report
        with open(REPORT_PATH, "w", encoding="utf-8") as file:
            file.write("CRICBUZZ SCORE REPORT\n")
            file.write(f"Collected: {datetime.now()}\n")
            file.write(f"Page: {page.url}\n")
            file.write(f"Status: {status_message}\n\n")
            file.write(score_report)

        print(f"Report saved: {REPORT_PATH}")
        print("Automation completed successfully.")

    except Exception as error:
        print(f"Automation error: {error}")

        page.screenshot(
            path=str(OUTPUT_DIR / "error.png"),
            full_page=True
        )

    finally:
        browser.close()
        print("Browser closed.")

