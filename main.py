import time

import pandas as pd

from ingest.github import get_starred_repos
from ingest.linkedin import get_liked_posts
from ingest.llm import chain
from ingest.notion import (
    database_id,
    format_notion_database_record,
    notion_client,
    notion_db_to_df,
    write_notion_page,
)
from ingest.reddit import get_saved_posts
from ingest.twitter import get_liked_tweets
from utils import logger

API_THROTTLE = 1
TOKEN_TRUNCATION = 2000


if __name__ == "__main__":
    # 1. retrieve
    reddit_posts = get_saved_posts()
    twitter_posts = get_liked_tweets()
    github_repos = get_starred_repos()
    linkedin_posts = get_liked_posts()

    # 2. format
    all_records = pd.concat(
        [reddit_posts, twitter_posts, github_repos, linkedin_posts]
    ).to_dict(orient="records")
    logger.info(f"Found {len(all_records)} records to write to Notion")

    # 3. write
    notion_db = notion_db_to_df(notion_client, database_id)
    existing_texts = notion_db.text.tolist()
    for record in all_records:
        if record["text"] in existing_texts:
            logger.warning(
                f"Record **{record['text'][:200]}** already exists, skipping"
            )
            continue
        else:
            # 3.1 include a relevancy prediction
            time.sleep(API_THROTTLE)  # ~60 requests a minute
            truncated_input = " ".join(
                record["text"].split(" ")[:TOKEN_TRUNCATION]
            )  # input limits
            record["is_tech_related"] = chain.run({"text": truncated_input}).strip()

            # 3.2 format/write to notion
            new_database_record = format_notion_database_record(record)
            write_notion_page(new_database_record, database_id)
