# scrape.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def scrape_website(url):
    """
    Scrape content from the provided URL.
    :param url: The URL of the website to scrape.
    :return: A string containing the scraped text.
    """
    
    # Check if the URL is missing a scheme (e.g., "http://" or "https://")
    if not urlparse(url).scheme:
        # Prepend 'https://' if the URL is missing a scheme
        url = f"https://{url}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad HTTP status codes
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract text from paragraphs or other relevant tags
        paragraphs = soup.find_all('p')
        return ' '.join([p.get_text() for p in paragraphs])
    
    except requests.exceptions.RequestException as e:
        # Handle HTTP errors (e.g., 404, 500) or invalid URLs
        return f"Failed to retrieve {url}: {str(e)}"



# use if site is dynamic and we need to render the site before extracting
# pip install selenium webdriver-manager
# from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By

# def scrape_dynamic_content(url):
#     # Set up Selenium WebDriver
#     driver = webdriver.Chrome(ChromeDriverManager().install())
    
#     # Open the website
#     driver.get(url)

#     # Wait for the content to load (optional)
#     driver.implicitly_wait(10)

#     # Extract content (e.g., paragraphs)
#     paragraphs = driver.find_elements(By.TAG_NAME, 'p')
    
#     for paragraph in paragraphs:
#         print(paragraph.text)

#     # Close the browser
#     driver.quit()

# # Example URL to scrape
# url = "https://example.com"
# scrape_dynamic_content(url)

