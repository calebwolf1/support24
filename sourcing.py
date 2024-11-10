import requests

def google_search(query, api_key, cx):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": query
    }
    response = requests.get(url, params=params)
    # Check if request was successful
    if response.status_code == 200:
        return response.json()  # Return JSON results
    else:
        response.raise_for_status()  # Raise an error if the request failed

    return sources

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
