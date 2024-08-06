from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

# Initialize the WebDriver
service = Service('/usr/local/bin/chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open EarthCam website
driver.get('https://www.earthcam.com/')

# Wait for the page to load
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

# Click "Show More" buttons until no more are found
while True:
    try:
        print("Attempting to find 'Show More' button...")
        show_more_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//button[text()="Show More"]'))
        )
        if show_more_button.is_displayed() and show_more_button.is_enabled():
            print("Found 'Show More' button. Clicking...")
            driver.execute_script("arguments[0].scrollIntoView();", show_more_button)
            ActionChains(driver).move_to_element(show_more_button).click(show_more_button).perform()
            time.sleep(5)  # Allow time for new content to load
        else:
            print("Show More button is not interactable or visible. Exiting loop.")
            break
    except Exception as e:
        print("No more 'Show More' buttons found or an error occurred:", e)
        break

# Scrape feed details
feeds_data = []

print("Scraping feed data...")
camera_blocks = driver.find_elements(By.CLASS_NAME, 'camera_block')
print(f"Found {len(camera_blocks)} camera blocks.")

for block in camera_blocks:
    try:
        # Scrape the feed URL
        feed_url = block.find_element(By.CSS_SELECTOR, 'a.noDec').get_attribute('href')

        # Scrape the thumbnail URL
        thumbnail_url = block.find_element(By.CSS_SELECTOR, 'img.thumbnailImage').get_attribute('src')

        # Scrape the feed title
        feed_title = block.find_element(By.CSS_SELECTOR, 'img.thumbnailImage').get_attribute('title')

        # Scrape the location
        location = block.find_element(By.CLASS_NAME, 'thumbnailMisc').text

        # Scrape the views and likes (if available)
        views = block.find_element(By.CLASS_NAME, 'thumbnailViews').text if block.find_elements(By.CLASS_NAME, 'thumbnailViews') else "N/A"
        likes = block.find_element(By.CLASS_NAME, 'thumbnailLikes').text if block.find_elements(By.CLASS_NAME, 'thumbnailLikes') else "N/A"

        feeds_data.append({
            'feed_url': feed_url,
            'thumbnail_url': thumbnail_url,
            'feed_title': feed_title,
            'location': location,
            'views': views,
            'likes': likes
        })

    except Exception as e:
        print(f"Error scraping feed: {e}")

# Print the results
for feed in feeds_data:
    print(feed)

driver.quit()