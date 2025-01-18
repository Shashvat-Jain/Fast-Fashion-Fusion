import requests
from bs4 import BeautifulSoup


def extract_instagram_links(url):
    try:
        # Send a request to the Wikipedia page
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all links in the page
        links = soup.find_all("a", href=True)

        # Filter links that lead to Instagram profiles
        instagram_links = [
            link["href"] for link in links if "instagram.com" in link["href"]
        ]

        return instagram_links
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


# URL of the Wikipedia page
url = "https://en.m.wikipedia.org/wiki/List_of_most-followed_Instagram_accounts"

# Extract Instagram profile links
instagram_profile_links = extract_instagram_links(url)

# Print the results
print("Instagram Profile Links:")
for link in instagram_profile_links:
    print(link)
