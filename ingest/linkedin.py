import contextlib
import os
import re
import time

import pandas as pd
import pyperclip
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchWindowException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from utils import logger

N_URL_ATTEMPTS = 2
N_WAIT_TIME = 5

load_dotenv()

# linkedin_client = Linkedin(
#     os.environ["LINKEDIN_EMAIL"],
#     os.environ["LINKEDIN_PASSWORD"],
#     refresh_cookies=True,
# )

# check if the ChromeDriver executable already exists
if os.path.exists(ChromeDriverManager().install()):
    # if it exists, use it to create the driver instance
    DRIVER = webdriver.Chrome()
else:
    # if it does not exist, download it and use it to create the driver instance
    DRIVER = webdriver.Chrome(ChromeDriverManager().install())


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
            # time.sleep(N_WAIT_TIME * 1.5)
            # elements = DRIVER.find_elements(By.CLASS_NAME, "feed-shared-control-menu__item")

            # wait for the elements to become available (save, copy link, report)
            wait = WebDriverWait(DRIVER, N_WAIT_TIME * 1)
            elements = wait.until(
                EC.visibility_of_all_elements_located(
                    (By.CLASS_NAME, "feed-shared-control-menu__item")
                )
            )

            # click the "save to clipboard"
            elements[1].click()  # TODO: more robust filtering

            # simulate Ctrl+C keyboard shortcut to copy the link to the clipboard
            action_chains = ActionChains(DRIVER)
            action_chains.key_down(Keys.CONTROL).send_keys("c").key_up(
                Keys.CONTROL
            ).perform()

            link = pyperclip.paste()
            links.append(link)
        except Exception:
            continue

    if links := list(set(links)):
        return link if len(links) == 1 else links[0]
    else:
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
    # TODO: date created, meta: external links
    if text := get_post_description(update_container):
        return {
            "user": get_post_author(update_container),
            "url": get_post_url(update_container),
            "text": get_post_description(update_container),
        }
    else:
        raise ValueError("No text found in post")


def get_liked_posts():
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

    # refresh the page
    DRIVER.refresh()
    time.sleep(N_WAIT_TIME * 1.5)

    # TODO: scroll a little > min 20 update containers?

    # get/filter update containers
    logger.info("Retrieving update containers..")
    update_containers = DRIVER.find_elements(
        By.CLASS_NAME, "profile-creator-shared-feed-update__container"
    )
    update_containers = [
        e for e in update_containers if len(get_post_description(e)) > 2
    ]

    posts = []
    logger.info("Parsing update containers..")
    for update_container in update_containers:
        parsed_post = parse_post(update_container)
        posts.append(parsed_post)
    logger.info(f"Linkedin: found {len(posts)} saved posts")

    with contextlib.suppress(NoSuchWindowException):
        DRIVER.quit()
    return pd.DataFrame(posts).drop_duplicates(subset=["user", "text"])
