from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up Chrome options (optional, useful for headless mode or other settings)
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no browser UI)
chrome_options.add_argument("--disable-gpu")

# Specify the path to ChromeDriver
service = Service('/usr/local/bin/chromedriver')  # Adjust this path if needed

# Initialize the WebDriver
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open EarthCam website
driver.get('https://www.earthcam.com/')

# Wait for the page to load
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

# Loop to click "Show More" until no more buttons are found
while True:
  try:
    # Try to find the "Show More" button with a timeout
    show_more_button = WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.XPATH, '//button[text()="Show More"]')))
        
    # Check if the button is displayed and clickable
    if show_more_button.is_displayed() and show_more_button.is_enabled():
      driver.execute_script("arguments[0].scrollIntoView();", show_more_button)
      ActionChains(driver).move_to_element(show_more_button).click(show_more_button).perform()
      # Allow time for new content to load
      time.sleep(5)
    else:
      print("Show More button is not interactable or visible.")
      break
  except Exception as e:
    # Check if the clicks are already done
    print("No more 'Show More' buttons found or an error occurred.")
    break

# After clicking all "Show More" buttons, scrape the thumbnails
thumbnails = driver.find_elements(By.CLASS_NAME, 'thumbnailImage')

for thumbnail in thumbnails:
  print(thumbnail.get_attribute('src'))  # Get the URL of the thumbnail image

driver.quit()

