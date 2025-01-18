from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# URL of the page containing the list of top 100 influencers
URL = "https://influencers.feedspot.com/celebrity_instagram_influencers/?utm_source=chatgpt.com"


def scrape_influencer_profiles():
    # Set up Selenium WebDriver
    options = Options()
    options.add_argument("--headless")  # Run browser in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    service = Service()  # Update this path to your Chromedriver
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Load the webpage
        driver.get(URL)
        time.sleep(5)  # Allow time for the page to fully load
        tabla = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "GridContainerDataV"))
        )
        print(tabla.get_attribute("value"))
        # Locate the influencer elements (list items)
        items = driver.find_elements(By.CLASS_NAME, "fs-list-item")
        if not items:
            print(
                "No influencers found. Check the structure of the webpage or locator."
            )
            return

        influencers = []
        for item in items:
            try:
                # Extract influencer name
                name_element = item.find_element(By.TAG_NAME, "h3")
                name = name_element.text.strip()

                # Extract Instagram profile link (if available)
                social_links = item.find_elements(By.TAG_NAME, "a")
                instagram_link = None
                for link in social_links:
                    href = link.get_attribute("href")
                    if "instagram.com" in href:
                        instagram_link = href
                        break

                # Append to the influencers list
                influencers.append(
                    {"Name": name, "Instagram Profile": instagram_link or "N/A"}
                )
            except Exception as e:
                print(f"Error processing an influencer: {e}")

        # Save data to a CSV file
        df = pd.DataFrame(influencers)
        df.to_csv("top_100_influencers_profiles.csv", index=False)
        print("Data saved to top_100_influencers_profiles.csv")
    finally:
        driver.quit()


if __name__ == "__main__":
    scrape_influencer_profiles()
