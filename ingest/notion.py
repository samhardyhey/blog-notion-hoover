import json
import os
import secrets
import time

import pandas as pd
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

notion_client = Client(auth=os.environ["NOTION_API_KEY"])
database_id = os.environ["NOTION_DB_ID"]


def find_record_by_property(prop_name, prop_value):
    if results := notion_client.databases.query(
        **{
            "database_id": database_id,
            "filter": {
                "property": prop_name,
                "title": {"equals": prop_value},
            },
        }
    ).get("results"):
        return results[0]
    else:
        return None


def format_notion_database_record(record):
    notion_text_char_limit = 1800  # slightly less than 2000
    meta = json.dumps(record["meta"]) if record["meta"] != {} else "None"
    text = record["text"][:notion_text_char_limit]
    date_created = (
        record["date_created"].to_pydatetime().isoformat()
        if type(record["date_created"]) == pd.Timestamp
        else record["date_created"]
    )
    return {
        "id": {"title": [{"text": {"content": secrets.token_hex(4)}}]},
        "text": {"rich_text": [{"text": {"content": text}}]},
        "user": {"rich_text": [{"text": {"content": record["user"]}}]},
        "url": {"url": record["url"]},
        "date_created": {"date": {"start": date_created}},
        "type": {"select": {"name": record["type"]}},
        "source_system": {"select": {"name": record["source_system"]}},
        "meta": {"rich_text": [{"text": {"content": meta}}]},
        "is_tech_related": {"select": {"name": record["is_tech_related"]}},
    }


def notion_db_to_df(notion_client, database_id):
    # Create an empty list to hold all pages
    data = []

    # Initialize start_cursor as None to get the first page of results
    start_cursor = None

    while True:
        time.sleep(0.2)
        # Get a page of results
        response = notion_client.databases.query(database_id, start_cursor=start_cursor)
        results = response.get("results")

        # Convert the pages to records and add them to data
        for page in results:
            record = {
                prop_name: get_property_value(page, prop_name)
                for prop_name in page["properties"].keys()
            }
            data.append(record)

        if next_cursor := response.get("next_cursor"):
            # Otherwise, set 'start_cursor' to 'next_cursor' to get the next page of results in the next iteration
            start_cursor = next_cursor

        else:
            break

    # Convert the data to a dataframe and return it
    return pd.DataFrame(data)


def get_property_value(page, property_name):
    # for a notion page/db record
    prop = page["properties"][property_name]
    if prop["type"] == "title":
        return prop["title"][0]["text"]["content"] if prop["title"] else None
    elif prop["type"] == "rich_text":
        return prop["rich_text"][0]["text"]["content"] if prop["rich_text"] else None
    elif prop["type"] == "number":
        return prop["number"]
    elif prop["type"] == "date":
        return prop["date"]["start"] if prop["date"] else None
    elif prop["type"] == "url":
        return prop["url"]
    elif prop["type"] == "email":
        return prop["email"]
    elif prop["type"] == "phone_number":
        return prop["phone_number"]
    elif prop["type"] == "select":
        return prop["select"]["name"] if prop["select"] else None
    elif prop["type"] == "multi_select":
        return (
            [option["name"] for option in prop["multi_select"]]
            if prop["multi_select"]
            else []
        )
    else:
        return None
