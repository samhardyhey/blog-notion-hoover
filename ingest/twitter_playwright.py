import os

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from utils import logger

N_URL_ATTEMPTS = 2
N_WAIT_TIME = 5
HEADLESS = False

load_dotenv()


def get_liked_posts():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        page = browser.new_page()

        logger.info("Logging into Twitter..")
        page.goto("https://twitter.com/login")
        page.fill("input[name='text']", os.environ["TWITTER_EMAIL"])
        page.click("//div[div/span/span[text()='Next']]")
        page.fill("input[name='password']", os.environ["TWITTER_PASSWORD"])
        page.click("//div[span/span[text()='Log in']]")

        # locate to liked tweets
        page.click("a[data-testid='AppTabBar_Profile_Link']")
        page.click("a[href='/samhardyhey/likes']")

        # get tweet elements
        # tweet_elements = page.query_selector_all("[data-testid='tweetText']")
        tweet_elements = page.query_selector_all('article[data-testid="tweet"]')

        tweets = []
        for element in tweet_elements:
            tweets.append({"text": element.inner_text()})

        # tweet_elements = page.query_selector_all("[data-testid='tweetText']")

        # collect and parse tweets?


if __name__ == "__main__":
    get_liked_posts()
