import praw


def connect_to_reddit() -> praw.reddit.Reddit:
    # TODO read from config, passed to the method?
    # connect to reddit
    reddit = praw.Reddit(
        client_id=ID,
        client_secret=SECRET,
        password=PASSWORD,
        user_agent=AGENT,
        username=USERNAME)
    return reddit
