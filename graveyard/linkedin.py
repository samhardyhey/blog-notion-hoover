import contextlib
import os
import re
import time
from datetime import datetime, timezone
from urllib import parse

import pandas as pd
import pyperclip
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchWindowException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from utils import logger

N_URL_ATTEMPTS = 2
N_WAIT_TIME = 5
HEADLESS = True

load_dotenv()


def create_driver():
    if not os.path.exists(ChromeDriverManager().install()):
        # download/install otherwise
        return webdriver.Chrome(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    return webdriver.Chrome(options=options) if HEADLESS else webdriver.Chrome()


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
            button = update_container.find_elements(
                By.CLASS_NAME, "feed-shared-control-menu__trigger"
            )[0]
            button.click()

            # wait for the elements to become available (save, copy link, report)
            wait = WebDriverWait(DRIVER, N_WAIT_TIME * 2)
            elements = wait.until(
                EC.visibility_of_all_elements_located(
                    (By.CLASS_NAME, "feed-shared-control-menu__item")
                )
            )

            # click the "save to clipboard"
            elements[1].click()  # TODO: more robust filtering
            time.sleep(N_WAIT_TIME / 2)

            # paste/check the link
            link = pyperclip.paste()
            links.append(link)
            if is_valid_url(link):
                break

        except Exception:
            continue

    if links := list(set(links)):
        return link if len(links) == 1 else links[0]

    logger.warning(f"Unable to find valid URL for post: {update_container.id}")
    return None


def get_post_description(container):
    show_more_text = container.find_elements(
        By.CLASS_NAME, "feed-shared-inline-show-more-text"
    )
    return " ".join([e.text for e in show_more_text])


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
    update_components_actor = container.find_elements(
        By.CLASS_NAME, "update-components-actor"
    )
    links = update_components_actor[0].find_elements(
        By.CLASS_NAME, "app-aware-link"
    )  # TODO: brittle indexing
    return extract_author_from_url(links[0].get_attribute("href"))


def parse_post(update_container):
    # TODO: meta: external links
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
    else:
        raise ValueError("No text found in post")


def get_liked_posts():
    # create driver
    DRIVER = create_driver()

    # login
    logger.info("Logging into linkedin..")
    DRIVER.get("https://www.linkedin.com/login")
    username = DRIVER.find_element(By.ID, "username")
    password = DRIVER.find_element(By.ID, "password")
    username.send_keys(os.environ["LINKEDIN_EMAIL"])
    password.send_keys(os.environ["LINKEDIN_PASSWORD"])
    password.send_keys(Keys.RETURN)
    time.sleep(N_WAIT_TIME * 1.5)

    # locate to reaction posts
    logger.info("Locating to reaction page..")
    DRIVER.get("https://www.linkedin.com/in/samhardyhey/recent-activity/reactions/")

    # refresh the page - unpredictable misc. page load errors
    DRIVER.refresh()

    # wait for the DM dialogue to appear, then close
    wait = WebDriverWait(DRIVER, N_WAIT_TIME * 3)
    dm_buttons = wait.until(
        EC.visibility_of_all_elements_located(
            (By.CLASS_NAME, "msg-overlay-bubble-header__control")
        )
    )
    dm_button = [e for e in dm_buttons if "minimize" in e.text][0]
    dm_button.click()

    # scroll a little > more posts
    DRIVER.execute_script("window.scrollBy(0, 10000);")
    time.sleep(N_WAIT_TIME * 2)

    # get/filter update containers (each liked post)
    logger.info("Retrieving update containers..")
    update_containers = DRIVER.find_elements(
        By.CLASS_NAME, "profile-creator-shared-feed-update__container"
    )
    update_containers = [
        e for e in update_containers if len(get_post_description(e)) > 2
    ]
    time.sleep(N_WAIT_TIME)

    posts = []
    logger.info("Parsing update containers..")
    for update_container in update_containers:
        parsed_post = parse_post(update_container)
        posts.append(parsed_post)
    logger.info(f"Linkedin: found {len(posts)} saved posts")

    with contextlib.suppress(NoSuchWindowException):
        DRIVER.quit()
    return pd.DataFrame(posts).drop_duplicates(subset=["user", "text"])
