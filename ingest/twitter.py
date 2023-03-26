import datetime
import os
from datetime import datetime

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
MAX_TWEETS = 200  # no need to paginate


def parse_tweet(tweet):
    return {
        "user": tweet.user.screen_name,
        "url": f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id_str}",
        "date_created": tweet.created_at.isoformat(),
        "type": "tweet",
        "source_system": "twitter",
        "text": tweet.full_text,
        "meta": {},
    }


def get_liked_tweets(start_date=None, end_date=None, limit=MAX_TWEETS):
    # hmm, also can't filter tweets by liked date
    if start_date is not None and end_date is not None and start_date > end_date:
        raise ValueError("start_date cannot be later than end_date")
    tweets = []

    tweets_page = twitter_client.get_favorites(
        user_id=os.environ["TWITTER_USERNAME"], tweet_mode="extended", count=limit
    )
    if start_date is not None and end_date is not None:
        parsed_tweets = [parse_tweet(t) for t in tweets_page]
        for t in parsed_tweets:
            tweet_date = datetime.strptime(t["date_created"], "%Y-%m-%dT%H:%M:%S+00:00")
            tweets.append(t)
            # if start_date <= tweet_date <= end_date:

    return pd.DataFrame(tweets).drop_duplicates(subset=["user", "text"])
