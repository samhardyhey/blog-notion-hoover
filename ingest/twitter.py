import os

import pandas as pd
import tweepy
from dateutil import parser
from dotenv import load_dotenv

from utils import logger

load_dotenv()

auth = tweepy.OAuthHandler(os.environ["TWITTER_KEY"], os.environ["TWITTER_SECRET_KEY"])
auth.set_access_token(
    os.environ["TWITTER_ACCESS_TOKEN"], os.environ["TWITTER_ACCESS_TOKEN_SECRET"]
)
twitter_client = tweepy.API(auth)
MAX_TWEETS = 200  # no need to paginate


def parse_tweet(tweet):
    return {
        "user": tweet.user.screen_name,
        "url": f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id_str}",
        "date_created": parser.parse(tweet.created_at.isoformat()),
        "type": "tweet",
        "source_system": "twitter",
        "text": tweet.full_text,
        "meta": {},
    }


def get_liked_tweets(limit=MAX_TWEETS):
    tweets_page = twitter_client.get_favorites(
        user_id=os.environ["TWITTER_USERNAME"], tweet_mode="extended", count=limit
    )
    parsed_tweets = [parse_tweet(t) for t in tweets_page]
    tweets = list(parsed_tweets)
    logger.info(f"Twitter: found {len(tweets)} saved tweets")
    return pd.DataFrame(tweets).drop_duplicates(subset=["user", "text"])


if __name__ == "__main__":
    get_liked_tweets()
