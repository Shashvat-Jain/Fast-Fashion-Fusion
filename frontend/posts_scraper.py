import httpx
import json
from typing import Dict
from urllib.parse import quote
import wget
from profile_scraper import profiles_scraper, extract_instagram_post_urls_for_profile
import time

INSTAGRAM_DOCUMENT_ID = "8845758582119845"


def scrape_post(url_or_shortcode: str) -> Dict:
    if "http" in url_or_shortcode:
        shortcode = url_or_shortcode.split("/p/")[-1].split("/")[0]
    else:
        shortcode = url_or_shortcode
    print(f"scraping instagram post: {shortcode}")

    variables = quote(
        json.dumps(
            {
                "shortcode": shortcode,
                "fetch_tagged_user_count": None,
                "hoisted_comment_id": None,
                "hoisted_reply_id": None,
            },
            separators=(",", ":"),
        )
    )
    body = f"variables={variables}&doc_id={INSTAGRAM_DOCUMENT_ID}"
    url = "https://www.instagram.com/graphql/query"

    result = httpx.post(
        url=url,
        headers={"content-type": "application/x-www-form-urlencoded"},
        data=body,
    )
    data = json.loads(result.content)
    return data["data"]["xdt_shortcode_media"]


def all_posts_info():
    all_posts_urls = profiles_scraper()
    print(all_posts_urls)
    posts_image_urls = []
    for post in all_posts_urls:
        posts = scrape_post(post)
        # posts = scrape_post("https://www.instagram.com/p/DD7oBI2RtAR/")
        link = posts["display_url"]
        posts_image_urls.append(link)
        # if posts["is_video"] == True:
        #     link = posts["video_url"]
        # response = requests.get(link, stream=True)
        # file = open("video.mp4", "wb")
        # for chunk in response.iter_content(chunk_size=1024):
        #   if chunk:
        #     file.write(chunk)
        # response = wget.download(link, "video.mp4")
        # else:
        #     link = posts["display_url"]
        #     posts_image_urls.append(link)
        # response = wget.download(link, "image.jpg")

        # caption = posts["edge_media_to_caption"]["edges"][0]["node"]["text"]
        # comments_count = posts["edge_media_to_parent_comment"]["count"]
        # likes_count = posts["edge_media_preview_like"]["count"]
        # comments_list = []
        # for p in posts["edge_media_to_parent_comment"]["edges"]:
        #     comments_list.append(
        #         {
        #             "comment": p["node"]["text"],
        #             "username": p["node"]["owner"]["username"],
        #             "likes": p["node"]["edge_liked_by"]["count"],
        #         }
        #     )
        time.sleep(15)
    print(posts_image_urls)
    return posts_image_urls


# all_posts_info()
