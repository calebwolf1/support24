# claim_scraper.py
from sourcing import google_search
from scrape import scrape_website

class ClaimScraper:
    def __init__(self, claim, api_key, cx):
        self.claim = claim
        self.api_key = api_key
        self.cx = cx
        self.sources = []  # Store links for the claim

    def get_sources_and_scrape(self):
        # Perform the search and get a list of URLs
        self.sources = google_search(self.claim, self.api_key, self.cx)
        
        scraped_data = []
        
        # Check if sources were found
        if not self.sources:
            print("No sources found for this claim.")
            return scraped_data

        # Scrape each source (URL)
        for url in self.sources:
            print(f"Scraping content from: {url}")
            try:
                content = scrape_website(url)
                scraped_data.append({
                    'url': url,
                    'content': content
                })
            except Exception as e:
                # Handle scraping errors
                print(f"Failed to retrieve {url}: {e}")
        
        return scraped_data
