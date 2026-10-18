#import the necessary libraries
from playwright.sync_api import sync_playwright
from datetime import datetime
print("starting playwright automation script")
print(f"Script started at: {datetime.now()}")

#Daily Weather report bot
#chromium --> weather site --> Extract weather data --> screenshot --> final txt file --> close browser
with sync_playwright() as p:
    #launch the browser
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    #navigate to the weather site
    page.goto("https://www.accuweather.com/en/in/chennai/206671/weather-forecast/206671")
    
    # give time to load the page 
    page.wait_for_timeout(3000)  # wait for 3 seconds to ensure the page loads completely
    
    #extract weather data
    weather_data = page.inner_text("div.CurrentConditions--primary--2SVPh")
    print(f"Weather Data: {weather_data}")
    
    #take a screenshot of the weather page
    page.screenshot(path="weather_screenshot.png")
    
    #save the weather data to a text file
    with open("weather_report.txt", "w") as file:
        file.write(weather_data)
    
    #close the browser
    browser.close()