# claim_scraper.py
from .sourcing import google_search
from .scrape import scrape_website
import asyncio

class ClaimScraper:
    def __init__(self, claim, api_key, cx):
        """
        Initializes the ClaimScraper with a claim, API key, and search engine ID.
        :param claim: String representing the claim to search for.
        :param api_key: Google Custom Search API key.
        :param cx: Google Custom Search Engine ID.
        """
        self.claim = claim
        self.api_key = api_key
        self.cx = cx
        self.sources = []  # To store links for the claim

    async def get_sources_and_scrape(self):
        """
        Get sources (links) for the claim and scrape content from each source.
        """
        self.sources = google_search(self.claim, self.api_key, self.cx)  # Perform the search
        scraped_data = []

        # Scrape each source (URL)
        for url in self.sources:
            await asyncio.sleep(0.1)
            try:
                print(f"Scraping content from: {url}")
                if ".pdf" not in url:
                    content = scrape_website(url)
                    scraped_data.append({'url': url, 'content': content})
            except Exception as e:
                print(f"Failed to scrape {url}: {e}")
                continue
        return scraped_data
