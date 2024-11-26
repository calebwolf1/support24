from dotenv import load_dotenv
import os
from source_and_scrape import ClaimScraper

load_dotenv()

# Main function to run the claim scraper - TESTING PURPOSES ONLY
if __name__ == "__main__":
    # Your Google Custom Search API key and search engine ID
    api_key = os.getenv("GOOGLE_SEARCH_KEY")
    cx = os.getenv("SEARCH_ENGINE_ID")

    claim = "water has four states of matter"  # Example claim
    scraper = ClaimScraper(claim, api_key, cx)

    # Get sources and scrape them
    data = scraper.get_sources_and_scrape()

    # Print scraped data
    for entry in data:
        print(f"URL: {entry['url']}")
        print(f"Content: {entry['content'][:500]}...")  # Print first 500 characters
        print("-" * 50)
