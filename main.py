import logging
import os
from datetime import datetime

import pandas as pd

from ingest.notion import database_id, find_record_by_property, format_notion_database_record, notion_client
from ingest.reddit import get_saved_posts
from ingest.twitter import get_liked_tweets

logger = logging.getLogger()
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

start_date = datetime(2023, 3, 20)
end_date = datetime(2023, 3, 27)

if __name__ == "__main__":
    # 1. retrieve
    reddit_posts = get_saved_posts()
    twitter_posts = get_liked_tweets(start_date=start_date, end_date=end_date)
    # TODO: linkedin?

    # 2. format
    all_records = pd.concat([reddit_posts, twitter_posts]).to_dict(orient="records")
    logger.info(f"Found {len(all_records)} records to write to Notion")

    # 3. write
    for record in all_records:
        try:
            new_database_record = format_notion_database_record(record)
            if find_record_by_property("text", record["text"]):
                logger.warning(f"Record **{record['text']}** already exists, skipping")
            else:
                res = notion_client.pages.create(parent={"database_id": database_id}, properties=new_database_record)
        except Exception as e:
            logger.error(f"Record **{record['text']}** failed to write")
