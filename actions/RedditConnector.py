import json
from pathlib import Path
from textwrap import dedent

import praw


def connect_to_reddit() -> praw.reddit.Reddit:
    # TODO read from config, passed to the method?
    # TODO Also support a credentials.json file in the cwd?

    credential_file = Path(__file__).absolute().parent.parent / "credentials.json"
    """Credentials File that overrides the global configuration"""
    if credential_file.is_file():
        with credential_file.open("r") as crf:
            credentials: dict[str, str] = json.load(crf)
    else:
        raise NotImplementedError(f"At the moment, only the credentials file is supported! Please create a credentials.json file"
                                  f" at {credential_file.as_posix()} with the following content:\n" +
                                  dedent("""
                                  {
                                    "client_id": "ID",
                                    "client_secret": "SECRET",
                                    "password": "PASSWORD",
                                    "user_agent": "AGENT",
                                    "username": "USERNAME"         
                                  }
                                  """))
    reddit = praw.Reddit(
        **credentials
    )
    return reddit
