import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def scrape_website(url, timeout=3):
    """
    Scrape content from the provided URL.
    :param url: The URL of the website to scrape.
    :return: A string containing the scraped text.
    """
    
    # Check if the URL is missing a scheme (e.g., "http://" or "https://")
    if not urlparse(url).scheme:
        # Prepend 'https://' if the URL is missing a scheme
        url = f"https://{url}"

    # Set a custom User-Agent header to avoid being blocked by some websites for scraping
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    try:
        # response = requests.get(url)
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()  # Raise an exception for bad HTTP status codes

        if response.apparent_encoding == None:
            print(f"{url} not readable")
            return ""
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract text from paragraphs or other relevant tags
        paragraphs = soup.find_all('p')
        return ' '.join([p.get_text() for p in paragraphs])
    
    except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
        # Handle errors or timeouts by returning an empty string or logging the issue
        print(f"Error scraping {url}: {e}")
        return ""  # Return empty string if the scraping fails or times out
    