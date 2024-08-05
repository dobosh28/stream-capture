from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options

# Set up Chrome options (optional, useful for headless mode or other settings)
chrome_options = Options()
chrome_options.add_argument("--headless") # Run in headless mode (no browser UI)
chrome_options.add_argument("--disable-gpu")

# Specify the path to ChromeDriver
service = Service('/usr/local/bin/chromedriver') 

# Initialize the WebDriver
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get('https://www.earthcam.com/')

thumbnails = driver.find_elements(By.CLASS_NAME, 'thumbnailImage')

for thumbnail in thumbnails:
  print(thumbnail.get_attribute('src'))

driver.quit()