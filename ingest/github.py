import base64
import os
import time

import pandas as pd
import requests
from dateutil import parser
from dotenv import load_dotenv

from utils import logger

load_dotenv()
MAX_REPOS = 10

# MAX_REPOS = 25


def get_readme_sample(repo_url):
    time.sleep(0.5)  # sleep to avoid rate limiting
    # Extract the repository owner and name from the URL
    owner, repo_name = repo_url.split("/")[-2:]

    # Build the API URL for the repository README
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}/readme"

    # Send a GET request to the Github API with an accept header to receive the response in base64 encoded format
    headers = {"Accept": "application/vnd.github.v3+json"}
    response = requests.get(api_url, headers=headers)

    # Decode the base64 encoded content of the README file and print it to the console
    if response.status_code == 200:
        readme_content = response.json().get("content")
        readme_text = base64.b64decode(readme_content).decode("utf-8")
        lines = readme_text.split("\n")
        sample = round(len(lines) / 2)
        return "\n".join(lines[:sample])
    else:
        logger.error(f"Error {response.status_code}: {response.reason}")
        return None


def parse_repo(repo):
    name = repo.get("name") or ""
    body = get_readme_sample(repo.get("html_url"))
    body = body or ""
    combined_text = f"{name} {body}".strip()

    return {
        "user": repo.get("owner").get("login"),
        "url": repo.get("html_url"),
        "date_created": parser.parse(repo.get("created_at")),
        "type": "repo",
        "source_system": "github",
        "text": combined_text,
        "meta": {
            "stars": repo.get("stargazers_count"),
            "language": repo.get("language"),
        },
    }


def get_starred_repos(limit=MAX_REPOS):
    headers = {
        "Authorization": f'Bearer {os.environ["GITHUB_TOKEN"]}',
    }
    params = {"per_page": limit}
    response = requests.get(
        "https://api.github.com/user/starred", headers=headers, params=params
    )

    if response.status_code == 200:
        starred_repos = response.json()
        repos = [parse_repo(repo) for repo in starred_repos]
        logger.info(f"Github: found {len(repos)} starred repos")
        return pd.DataFrame(repos)

    else:
        logger.error(f"Error {response.status_code}: {response.reason}")
