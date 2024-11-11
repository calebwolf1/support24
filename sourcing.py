import requests

def google_search(query, api_key, cx):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": "AIzaSyDYtszsTD4CL3EhikCHvMNeyyNgS7BWGS8",
        "cx": "42b3bf15b382f45c2",
        "q": query,
        "num": 5 # Number of results to return
    }
    print(params)
    try:
        response = requests.get(url, params=params)
        # Check if request was successful
        response.raise_for_status()  # Raise an error if the request failed
        return response.json()  # Return JSON results
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
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
