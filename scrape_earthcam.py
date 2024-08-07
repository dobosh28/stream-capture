from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import concurrent.futures

# Function to initialize WebDriver
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-images")

    service = Service('/usr/local/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Function to ensure all camera blocks are loaded
def load_all_camera_blocks(driver):
    while True:
        try:
            print("Attempting to find 'Show More' button...")
            show_more_button = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, '//button[text()="Show More"]'))
            )

            if show_more_button.is_displayed() and show_more_button.is_enabled():
                print("Found 'Show More' button. Clicking...")
                driver.execute_script("arguments[0].scrollIntoView();", show_more_button)
                ActionChains(driver).move_to_element(show_more_button).click().perform()
                time.sleep(2)
            else:
                print("No more 'Show More' buttons found.")
                break

        except Exception as e:
            print("Error clicking 'Show More' button or no more buttons found:", e)
            break

# Function to scrape feed details from the main page
def scrape_main_page(driver):
    feeds_data = []
    camera_blocks = driver.find_elements(By.CLASS_NAME, 'camera_block')
    print(f"Total camera blocks found: {len(camera_blocks)}")  # Debugging: check number of blocks found

    for block in camera_blocks:
        try:
            feed_url = block.find_element(By.CSS_SELECTOR, 'a.noDec').get_attribute('href')
            # Skip YouTube cam_blocks entirely
            if "youtube.com" in feed_url:
                print(f"Skipping YouTube cam_block: {feed_url}")
                continue

            thumbnail_url = block.find_element(By.CSS_SELECTOR, 'img.thumbnailImage').get_attribute('src')
            feed_title = block.find_element(By.CSS_SELECTOR, 'img.thumbnailImage').get_attribute('title')
            location = block.find_element(By.CLASS_NAME, 'thumbnailMisc').text

            feeds_data.append({
                'feed_url': feed_url,
                'thumbnail_url': thumbnail_url,
                'feed_title': feed_title,
                'location': location,
                'views': "N/A",
                'likes': "N/A"
            })
        except Exception as e:
            print(f"Error collecting feed data: {e}")

    return feeds_data

def scrape_likes_and_views(feed):
    driver = init_driver()
    try:
        # Navigate to the feed's URL
        driver.get(feed['feed_url'])

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'totalLikes')))

        # Retrieve both likes and views using a single JavaScript execution
        script = """
            return {
                likes: document.querySelector('.totalLikes') ? document.querySelector('.totalLikes').textContent : '',
                views: document.querySelector('.totalViews') ? document.querySelector('.totalViews').textContent : ''
            };
        """
        result = driver.execute_script(script)

        # Extract and clean up the likes and views data
        feed['likes'] = result['likes'].replace(" Likes", "").replace(",", "").strip() if result['likes'] else "N/A"
        feed['views'] = result['views'].replace(" Views", "").replace(",", "").strip() if result['views'] else "N/A"

    except Exception as e:
        print(f"Error collecting likes and views for {feed['feed_url']}: {e}")
        feed['likes'] = "N/A"
        feed['views'] = "N/A"

    finally:
        driver.quit()

    return feed

def main():
    driver = init_driver()
    driver.get('https://www.earthcam.com/')
    load_all_camera_blocks(driver)
    feeds_data = scrape_main_page(driver)

    # Use ThreadPoolExecutor to parallelize the scraping of likes and views
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        feeds_data = list(executor.map(scrape_likes_and_views, feeds_data))
    
    for feed in feeds_data:
        print(feed)

    driver.quit()

if __name__ == "__main__":
    main()