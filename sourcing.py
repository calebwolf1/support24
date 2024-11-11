import requests

def google_search(query, api_key, cx):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": query,
        # set the number of results to 5
        "num": 5
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        results = response.json()
        
        # Extract URLs if items are present in results
        urls = [item["link"] for item in results.get("items", [])]
        return urls
    else:
        response.raise_for_status()

# source = results["items"][0]["link"]

# # Output the results
# if "items" in results:
#     for item in results["items"]:
#         print("Title:", item["title"])
#         print("Link:", item["link"])
#         print("Snippet:", item["snippet"])
#         print("\n")
# else:
#     print("No results found.")
