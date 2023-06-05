import os
import re
import time
from datetime import datetime, timezone
from urllib import parse

import pandas as pd
import pyperclip
from dotenv import load_dotenv
from playwright.sync_api import TimeoutError, sync_playwright

from utils import logger

N_URL_ATTEMPTS = 2
N_WAIT_TIME = 5
HEADLESS = False

load_dotenv()


def is_valid_url(url):
    try:
        result = parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def get_post_url(update_container):
    links = []
    for _ in range(N_URL_ATTEMPTS):
        try:
            # find elipses next to post, click
            button = update_container.wait_for_selector(
                ".feed-shared-control-menu__trigger"
            )
            button.click()

            # wait for the elements to become available (save, copy link, report)
            copy_url = update_container.wait_for_selector(
                ".feed-shared-control-menu__item:nth-child(2)"
            )
            copy_url.click()

            # paste/check the link
            link = pyperclip.paste()
            links.append(link)
            if is_valid_url(link):
                break

        except TimeoutError:
            continue

    if links := list(set(links)):
        return link if len(links) == 1 else links[0]

    logger.warning(f"Unable to find valid URL for post: {update_container.id}")
    return None


def get_post_description(container):
    show_more_text = container.query_selector_all(".feed-shared-inline-show-more-text")
    return " ".join([e.text_content().strip() for e in show_more_text]).strip()


def extract_author_from_url(url):
    match = re.search(r"\/in\/([\w-]+)|\/company\/([\w-]+)", url)
    if match is None:
        raise ValueError("Invalid LinkedIn URL")
    entity_name = match[1] or match[2]
    if "/in/" in url:
        entity_type = "user"
    elif "/company/" in url:
        entity_type = "company"
    else:
        raise ValueError("Invalid LinkedIn URL")
    if entity_type in ["user", "company"]:
        return entity_name


def get_post_author(container):
    # container > "update-components-actor"
    update_components_actor = container.query_selector(".update-components-actor")
    links = update_components_actor.query_selector_all(
        ".app-aware-link"
    )  # TODO: brittle indexing
    return extract_author_from_url(links[0].get_attribute("href"))


def parse_post(update_container):
    if text := get_post_description(update_container):
        return {
            "user": get_post_author(update_container),
            "url": get_post_url(update_container),
            "date_created": datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            "type": "post",  # TODO: post taxonomy?
            "source_system": "linkedin",
            "text": get_post_description(update_container),
            "meta": {},
        }
    logger.warning("Unable to retrieve text for post")
    return None


def get_liked_posts():
    # Start Playwright with a headless Chromium browser
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        page = browser.new_page()

        # Login to LinkedIn
        logger.info("Logging into LinkedIn..")
        page.goto("https://www.linkedin.com/login")
        page.fill("#username", os.environ["LINKEDIN_EMAIL"])
        page.fill("#password", os.environ["LINKEDIN_PASSWORD"])
        page.press("#password", "Enter")
        page.wait_for_selector("input.search-global-typeahead__input")

        # Go to reaction posts
        logger.info("Navigating to reaction page..")
        page.goto("https://www.linkedin.com/in/samhardyhey/recent-activity/reactions/")

        # Prevent against weird page failures?
        page.reload()

        # Scroll down a bit to load more posts
        page.evaluate("window.scrollBy(0, 10000)")
        time.sleep(N_WAIT_TIME)

        # Wait for any DM dialog to appear, then close it
        button_selector = "button.msg-overlay-bubble-header__control"
        button_elements = page.query_selector_all(button_selector)
        dm_button = button_elements[1]
        dm_button.click()

        # Get the update containers for each liked post
        logger.info("Retrieving update containers..")
        update_containers = page.query_selector_all(
            ".profile-creator-shared-feed-update__container"
        )
        update_containers = [c for c in update_containers if len(c.text_content()) > 2]

        # Parse each post and collect the results
        posts = []
        logger.info("Parsing update containers..")
        for update_container in update_containers:
            parsed_post = parse_post(update_container)
            posts.append(parsed_post)
        logger.info(f"LinkedIn: found {len(posts)} saved posts")

        # Clean up the browser
        browser.close()

    # Return the parsed posts as a Pandas DataFrame
    posts = [e for e in posts if e]  # filter None
    return pd.DataFrame(posts).drop_duplicates(subset=["user", "text"])
