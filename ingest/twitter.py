import os

import pandas as pd
import tweepy
from dotenv import load_dotenv

load_dotenv()

auth = tweepy.OAuthHandler(
    os.environ["TWITTER_API_KEY"], os.environ["TWITTER_API_SECRET_KEY"]
)
auth.set_access_token(
    os.environ["TWITTER_ACCESS_TOKEN"], os.environ["TWITTER_ACCESS_TOKEN_SECRET"]
)
twitter_client = tweepy.API(auth)


def parse_tweet(tweet):
    return {
        "user": tweet.user.screen_name,
        "url": f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id_str}",
        "date": tweet.created_at.isoformat(),
        "type": "tweet",
        "source_system": "reddit",
        "text": tweet.full_text,
    }


def get_liked_tweets(limit=100):
    twitter_client.get_favorites()
    tweets = tweepy.Cursor(
        twitter_client.get_favorites,
        user_id=os.environ["TWITTER_USERNAME"],
        tweet_mode="extended",
    ).items(limit)
    parsed_tweets = [parse_tweet(t) for t in tweets]
    return pd.DataFrame(parsed_tweets).drop_duplicates(subset=["id", "text"])
