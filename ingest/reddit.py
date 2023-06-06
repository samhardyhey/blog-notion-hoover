import os
from datetime import datetime

import pandas as pd
import praw
from dotenv import load_dotenv

from utils import logger

load_dotenv()

reddit_client = praw.Reddit(
    client_id=os.environ["REDDIT_CLIENT_ID"],
    client_secret=os.environ["REDDIT_CLIENT_SECRET"],
    username=os.environ["REDDIT_USERNAME"],
    password=os.environ["REDDIT_PASSWORD"],
    user_agent=os.environ["REDDIT_USER_AGENT"],
)
MAX_POSTS = 200  # just below pagination limit


def parse_post(post):
    # faster than indexing into actual objects?
    post_type = "post" if isinstance(post, praw.models.Submission) else "comment"
    post_dict = post.__dict__

    # bit hacky; add title/body together when they exist
    title = post_dict.get("title") or ""
    body = post_dict.get("selftext") or post_dict.get("body")
    body = body or ""
    combined_text = f"{title} {body}".strip()
    url = post_dict.get("url") or post_dict.get("link_permalink")

    return {
        "user": post_dict.get("author").__str__(),
        "url": url,
        "date_created": datetime.utcfromtimestamp(
            post_dict.get("created_utc")
        ).isoformat(),
        "type": post_type,
        "source_system": "reddit",
        "text": combined_text,
        "meta": {"subreddit": post_dict.get("subreddit").display_name},
    }


def get_saved_posts(limit=MAX_POSTS):
    # no way to filter posts based upon save date; only get creation date
    posts = []
    user = reddit_client.redditor(os.environ["REDDIT_USERNAME"])
    saved = user.saved(limit=limit)
    for post in saved:
        datetime.utcfromtimestamp(post.created_utc)
        parsed_post = parse_post(post)
        posts.append(parsed_post)
    logger.info(f"Reddit: found {len(posts)} saved posts")
    return pd.DataFrame(posts).drop_duplicates(subset=["user", "text"])
