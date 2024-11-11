from dotenv import load_dotenv
import os
from claim_scraper import ClaimScraper

load_dotenv()

if __name__ == "__main__":
    # Load environment variables from .env file

    # Your Google Custom Search API key and search engine ID
    api_key = os.getenv("GOOGLE_SEARCH_KEY")
    cx = os.getenv("SEARCH_ENGINE_ID")
    # api_key = "AIzaSyDYtszsTD4CL3EhikCHvMNeyyNgS7BWGS8"
    # cx = "42b3bf15b382f45c2"

    claim = "water has four states of matter"  # Example claim
    scraper = ClaimScraper(claim, api_key, cx)

    # Get sources and scrape them
    data = scraper.get_sources_and_scrape()

    # Print scraped data
    for entry in data:
        print(f"URL: {entry['url']}")
        print(f"Content: {entry['content'][:500]}...")  # Print first 500 characters
        print("-" * 50)
