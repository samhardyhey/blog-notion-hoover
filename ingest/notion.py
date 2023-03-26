import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

if __name__ == "__main__":
    # Get the Notion API token
    notion = Client(auth=os.environ["NOTION_API_KEY"])

    # Define the database ID and create a new page
    database_id = os.environ["NOTION_DB_ID"]
    new_page = {
        "Name": {"title": [{"text": {"content": "test"}}]},
        "URL": {"url": "test"},
        "Date": {"date": {"start": datetime.now(timezone.utc).isoformat()}},
        "Type": {"select": {"name": "INSERT_PAGE_TYPE_HERE"}},
    }
    created_page = notion.pages.create(
        parent={"database_id": database_id}, properties=new_page
    )
