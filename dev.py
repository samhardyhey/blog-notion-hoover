# if __name__ == "__main__":
#     from ingest.linkedin import get_liked_posts

#     posts = get_liked_posts()
#     print("hello world")

import pyperclip
from playwright.sync_api import TimeoutError, sync_playwright


def main():
    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("http://www.example.com")

        element = page.locator("[href]")
        element.click(button="right")
        copy_link_locator = page.locator("text=Copy Link Address")
        copy_link_locator.click()
        link = pyperclip.paste()

        print(f"Copied link address: {link}")
        browser.close()


if __name__ == "__main__":
    main()
