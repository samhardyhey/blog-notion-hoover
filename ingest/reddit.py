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


def parse_post(post):
    # faster than indexing into actual objects?
    post_type = "post" if isinstance(post, praw.models.Submission) else "comment"
    post_dict = post.__dict__

    return {
        "user": post_dict.get("author").__str__(),
        "url": post_dict.get("url"),
        "date": datetime.utcfromtimestamp(post_dict.get("created_utc")).isoformat(),
        "type": post_type,
        "source_system": "reddit",
        "text": post_dict.get("selftext") or post_dict.get("body"),
        "title": post_dict.get("title"),
        "subreddit": post_dict.get("subreddit").display_name,
    }


def get_saved_posts(limit=100):
    user = reddit_client.redditor(os.environ["REDDIT_USERNAME"])
    saved = user.saved(limit=limit)
    posts = [parse_post(p) for p in saved]
    return pd.DataFrame(posts).drop_duplicates(subset=["id", "title"])
