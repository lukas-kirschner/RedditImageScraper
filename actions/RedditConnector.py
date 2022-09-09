import json
from pathlib import Path

import praw
from config import Config


def connect_to_reddit(cfg: Config) -> praw.reddit.Reddit:
    if cfg["reddit_connector.use_credential_file"]:
        credential_file = Path(cfg["reddit_connector.credential_file"])
        if credential_file.is_file():
            with credential_file.open("r") as crf:
                credentials: dict[str, str] = json.load(crf)
        else:
            raise FileNotFoundError(f"Credentials file {credential_file} was not found in your working directory!")
    else:
        credentials: dict[str, str] = {
            "client_id": cfg["reddit_connector.client_id"],
            "client_secret": cfg["reddit_connector.client_secret"],
            "user_agent": cfg["reddit_connector.user_agent"],
        }
    print(f"Authenticating with Reddit...")
    reddit = praw.Reddit(
        **credentials
    )
    print(f"Authentication successful.")
    return reddit
