from actions.RedditConnector import connect_to_reddit, get_imgur_client_id
from actions.ScrapeSubreddits import scrape_subreddit
from actions.WriteMetadata import MetadataModel, get_model_from_submission, write_metadata, set_time_created, set_post_title, set_keywords, \
    set_author, set_long_comment


def sanitize_filename(filename: str, repl='_') -> str:
    """
    Sanitize the given file name, replacing characters that are illegal in Windows
    :param repl: Char to replace illegal chars with
    :param filename: File name to sanitize
    :return: the new file name
    """
    illegal: str = "<>:\"/\\|?*"
    for char in illegal:
        filename = filename.replace(char, repl)
    return filename
