from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.lnw.com")
    print(page.title())
    page.screenshot(path="screenshot.png")
    browser.close()

    