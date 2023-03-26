# currently broken..
import os
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from linkedin_api import Linkedin

load_dotenv()


def parse_post(post):
    """
    Parse a LinkedIn post into a dictionary.
    """
    return {
        "id": post["id"],
        "title": post["specificContent"]["com.linkedin.ugc.ShareContent"][
            "shareCommentary"
        ]["text"],
        "content": post["specificContent"]["com.linkedin.ugc.ShareContent"][
            "shareMediaCategory"
        ].lower(),
        "url": post["specificContent"]["com.linkedin.ugc.ShareContent"][
            "shareMediaCategory"
        ],
        "date": datetime.utcfromtimestamp(post["created"] / 1000).isoformat(),
        "type": "post",
    }


def get_liked_posts():
    """
    Retrieve liked posts for the current LinkedIn user.

    Returns:
        A pandas DataFrame containing the parsed posts.
    """
    api = Linkedin(
        os.environ["LINKEDIN_EMAIL"],
        os.environ["LINKEDIN_PASSWORD"],
        refresh_cookies=True,
    )
    shares = api.get_my_network_shares(share_type="LIKE", count=1000)
    posts = [parse_post(s) for s in shares]
    return pd.DataFrame(posts).drop_duplicates(subset=["id", "title"])
