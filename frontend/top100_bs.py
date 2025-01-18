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


def top100():
    url = "https://en.m.wikipedia.org/wiki/List_of_most-followed_Instagram_accounts"
    instagram_profile_links = extract_instagram_links(url)

    for i in range(len(instagram_profile_links)):
        instagram_profile_links[i] = instagram_profile_links[i][26:]

    print("Instagram Profile Links:")
    for link in instagram_profile_links:
        print(link)
        break

    return instagram_profile_links


# top100()
