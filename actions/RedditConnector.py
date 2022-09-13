import json
from pathlib import Path

import praw
from config import Config


def connect_to_reddit(cfg: Config) -> praw.reddit.Reddit:
    credentials: dict[str, str] = _get_credentials(cfg)
    print(f"Authenticating with Reddit...")
    reddit = praw.Reddit(
        **credentials
    )
    print(f"Authentication successful.")
    return reddit


def _get_credentials(cfg: Config) -> dict[str, str]:
    """
    Get the credentials from the global config or the appropriate file.

    :param cfg: Global Config
    :return: the credentials
    """
    if cfg["reddit_connector.use_credential_file"]:
        credential_file = Path(cfg["reddit_connector.credential_file"])
        if credential_file.is_file():
            with credential_file.open("r") as crf:
                credentials: dict[str, str] = json.load(crf)
        else:
            raise FileNotFoundError(f"Credentials file {credential_file} was not found in the working directory!")
    else:
        credentials: dict[str, str] = {
            "client_id": cfg["reddit_connector.client_id"],
            "client_secret": cfg["reddit_connector.client_secret"],
            "user_agent": cfg["reddit_connector.user_agent"],
            "imgur_client_id": cfg["reddit_connector.imgur_client_id"],
        }
    return credentials


def get_imgur_client_id(cfg: Config) -> str:
    """
    Get the imgur client ID required to communicate to the API
    :param cfg: Global Config
    :return: the Client ID
    """
    credentials: dict[str, str] = _get_credentials(cfg)
    return credentials["imgur_client_id"]
