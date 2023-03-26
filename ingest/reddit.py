import os
from datetime import datetime

import pandas as pd
import praw
from dotenv import load_dotenv

load_dotenv()

reddit_client = praw.Reddit(
    client_id=os.environ["REDDIT_CLIENT_ID"],
    client_secret=os.environ["REDDIT_CLIENT_SECRET"],
    username=os.environ["REDDIT_USERNAME"],
    password=os.environ["REDDIT_PASSWORD"],
    user_agent=os.environ["REDDIT_USER_AGENT"],
)
MAX_POSTS = 200  # no need to paginate


def parse_post(post):
    # faster than indexing into actual objects?
    post_type = "post" if isinstance(post, praw.models.Submission) else "comment"
    post_dict = post.__dict__

    # bit hacky; add title/body together when they exist
    title = post_dict.get("title") or ""
    body = post_dict.get("selftext") or post_dict.get("body")
    body = body or ""
    combined_text = f"{title} {body}".strip()

    return {
        "user": post_dict.get("author").__str__(),
        "url": post_dict.get("url"),
        "date_created": datetime.utcfromtimestamp(
            post_dict.get("created_utc")
        ).isoformat(),
        "type": post_type,
        "source_system": "reddit",
        "text": combined_text,
        "meta": {"subreddit": post_dict.get("subreddit").display_name},
    }


def get_saved_posts(start_date=None, end_date=None, limit=MAX_POSTS):
    # no way to filter posts based upon save date; only get creation date
    if start_date is not None and end_date is not None and start_date > end_date:
        raise ValueError("start_date cannot be later than end_date")
    posts = []
    user = reddit_client.redditor(os.environ["REDDIT_USERNAME"])
    saved = user.saved(limit=limit)
    for post in saved:
        datetime.utcfromtimestamp(post.created_utc)
        # if start_date <= post_date <= end_date:
        parsed_post = parse_post(post)
        posts.append(parsed_post)
    return pd.DataFrame(posts).drop_duplicates(subset=["user", "text"])
