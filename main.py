import pandas as pd

from ingest.github import get_starred_repos
from ingest.linkedin import get_liked_posts
from ingest.llm import chain
from ingest.notion import (
    database_id,
    find_record_by_property,
    format_notion_database_record,
    notion_client,
)
from ingest.reddit import get_saved_posts
from ingest.twitter import get_liked_tweets
from utils import logger

if __name__ == "__main__":
    # 1. retrieve
    reddit_posts = get_saved_posts()
    twitter_posts = get_liked_tweets()
    github_repos = get_starred_repos()
    linkedin_posts = get_liked_posts()

    # 2. format
    all_records = pd.concat([reddit_posts]).to_dict(orient="records")
    # all_records = pd.concat([reddit_posts, twitter_posts, github_repos, linkedin_posts]).to_dict(orient="records")
    logger.info(f"Found {len(all_records)} records to write to Notion")

    # 3. write
    for record in all_records:
        if find_record_by_property("text", record["text"]):
            logger.warning(f"Record **{record['text']}** already exists, skipping")
            continue
        else:
            # include a relevancy prediction
            record["is_ml_related"] = chain.run({"text": record["text"]}).strip()
            new_database_record = format_notion_database_record(record)
            res = notion_client.pages.create(
                parent={"database_id": database_id}, properties=new_database_record
            )
