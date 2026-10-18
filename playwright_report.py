
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from datetime import datetime
from pathlib import Path
import time

print("Starting AccuWeather automation...")
print(f"Started at: {datetime.now()}")

# Output folder
output_dir = Path("weather_output")
output_dir.mkdir(exist_ok=True)

url = (
    "https://www.accuweather.com/en/in/chennai/"
    "206671/weather-forecast/206671"
)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    page = browser.new_page(
        viewport={"width": 1440, "height": 1000},
        device_scale_factor=1
    )

    try:
        # STEP 1: Open website
        print("Opening AccuWeather...")

        response = page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=15000
        )

        if response:
            print(f"HTTP status: {response.status}")

        # STEP 2: Wait for the page to initialize
        page.locator("body").wait_for(state="visible")
        page.wait_for_timeout(10000)

        # STEP 3: Wait for forecast content to render
        # Network-idle is not always reliable on ad-heavy websites.
        # Use a real forecast selector and a longer timeout instead.
        forecast_heading = page.get_by_text(
            "10-Day Forecast",
            exact=False
        ).first

        try:
            forecast_heading.wait_for(
                state="visible",
                timeout=15000
            )
            print("Forecast heading found.")
        except PlaywrightTimeoutError:
            print("Forecast heading not found yet.")

        # STEP 4: Scroll gradually to trigger lazy loading
        for _ in range(8):
            page.mouse.wheel(0, 700)
            page.wait_for_timeout(1000)

        # Give newly visible content extra time
        page.wait_for_timeout(10000)

        # STEP 5: Capture a diagnostic screenshot
        page.screenshot(
            path=str(output_dir / "debug_full_page.png"),
            full_page=True,
            animations="disabled"
        )

        # STEP 6: Try to locate the 10-day forecast section
        heading = page.get_by_text(
            "10-Day Forecast",
            exact=False
        ).first

        forecast_data = ""

        if heading.count() > 0:
            heading.scroll_into_view_if_needed()
            page.wait_for_timeout(3000)

            # Inspect parent containers until useful forecast text is found.
            # AccuWeather's HTML structure can change.
            for level in range(1, 7):
                section = heading.locator(
                    f"xpath=ancestor::*[{level}]"
                )

                try:
                    text = section.inner_text(timeout=5000)

                    if (
                        len(text.strip()) > 150
                        and (
                            "Mon" in text
                            or "Tue" in text
                            or "°" in text
                        )
                    ):
                        forecast_data = text
                        print(
                            f"Found candidate forecast container "
                            f"at ancestor level {level}."
                        )
                        break

                except Exception:
                    continue

        # STEP 7: Save report if useful data was found
        if forecast_data:
            report_path = (
                output_dir / "10_day_weather_report.txt"
            )

            with open(
                report_path, "w", encoding="utf-8"
            ) as file:
                file.write("CHENNAI - 10-DAY WEATHER FORECAST\n")
                file.write(f"Collected: {datetime.now()}\n")
                file.write(f"Source: {page.url}\n\n")
                file.write(forecast_data)

            print(f"Weather data saved: {report_path.resolve()}")

            # Screenshot of the selected forecast container
            section.screenshot(
                path=str(output_dir / "10_day_forecast.png")
            )

            print("Forecast screenshot saved.")

        else:
            print(
                "Forecast data was not detected. "
                "Saving diagnostic information."
            )

            # Save visible page text for selector troubleshooting
            page_text = page.locator("body").inner_text()

            (output_dir / "debug_page_text.txt").write_text(
                page_text,
                encoding="utf-8"
            )

            print("Saved debug_page_text.txt")

        # STEP 8: Save final full-page screenshot
        page.screenshot(
            path=str(output_dir / "full_weather_page.png"),
            full_page=True,
            animations="disabled"
        )

        print(f"Finished at: {datetime.now()}")

    except Exception as error:
        print(f"Automation error: {error}")

        page.screenshot(
            path=str(output_dir / "error_screenshot.png"),
            full_page=True
        )

    finally:
        browser.close()
        print("Browser closed.")
