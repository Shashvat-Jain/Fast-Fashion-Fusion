from selenium.webdriver import Chrome
from instascrape import Profile, scrape_posts

webdriver = Chrome()

headers = {
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.57",
    "cookie": "sessionid=45620276907%3ACliAzqmO2YudLu%3A9%3AAYd4Rt0Kddjrrf9DioLhz0DzUOQ9Xt_6gRWnt09n-w;",
}
joe = Profile("_arshdeep.singh__")
joe.scrape(headers=headers)

posts = joe.get_posts(webdriver=webdriver, amount=100, login_first=True, scrape=True)

print(posts)
