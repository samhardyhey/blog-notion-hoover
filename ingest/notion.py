import json
import os
import secrets
from datetime import datetime, timezone

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
    notion_text_char_limit = 2000
    meta = json.dumps(record["meta"]) if record["meta"] != {} else "None"
    text = record["text"][:notion_text_char_limit]
    return {
        "id": {"title": [{"text": {"content": secrets.token_hex(4)}}]},
        "text": {"rich_text": [{"text": {"content": text}}]},
        # "text": {"text": [{"text": {"content": record['text']}}]},
        "user": {"rich_text": [{"text": {"content": record["user"]}}]},
        # "user": {"user": [{"text": {"content": record['user']}}]},
        "url": {"url": record["url"]},
        "date": {"date": {"start": record["date"]}},
        "type": {"select": {"name": record["type"]}},
        "source_system": {"select": {"name": record["source_system"]}},
        "meta": {"rich_text": [{"text": {"content": meta}}]},
    }
