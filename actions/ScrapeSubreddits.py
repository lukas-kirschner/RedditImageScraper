import os
import urllib
import urllib.request
from collections import namedtuple
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import praw
from config import Config
from praw.models import Submission, Redditor
from prawcore import NotFound, PrawcoreException

from actions.downloader import ImgurAlbumDownloader
from reddit import RedditObject, Subreddit, User, SortMethod, UserPageKind


# TODO
# # handle 'ctrl + c' if downloads takes too long
#     def sigint_handler(signum, frame):
#         print('\nQuitting...')
#         sys.exit(1)
#     signal.signal(signal.SIGINT, sigint_handler)

class SubredditDoesNotExist(Exception):
    """
    Exception that is thrown if a subreddit does not exist
    """
    pass


class UserDoesNotExist(Exception):
    """
    Exception that is thrown if a user account does not exist
    """
    pass


def scrape_subreddit(reddit_object: RedditObject, limit: Optional[int], destination: Path, cfg: Config) -> None:
    """
    Scrape the given reddit object
    :param cfg: The global configuration
    :param destination: Destination directory
    :param reddit_object: Reddit object to scrape
    :param limit: Limit of images that should newly be downloaded, or None to disable the limit
    :return: None
    """
    import actions
    reddit: praw.reddit.Reddit = actions.connect_to_reddit(cfg)

    print(f"Searching for {reddit_object.printable_name()}...")
    # Check if the subreddit or user exists
    if reddit_object.is_subreddit:
        # noinspection PyTypeChecker
        reddit_object: Subreddit = reddit_object
        destination_path: Path = destination / f"reddit_sub_{reddit_object.subreddit_name}"
        try:
            reddit.subreddits.search_by_name(reddit_object.subreddit_name, exact=True)
        except NotFound as e:
            raise SubredditDoesNotExist from e
    elif reddit_object.is_user:
        # noinspection PyTypeChecker
        reddit_object: User = reddit_object
        try:
            reddit.redditors.search(reddit_object.user_name, exact=True)
        except NotFound as e:
            raise UserDoesNotExist from e
        destination_path: Path = destination / f"reddit_user_{reddit_object.user_name}"
        pass  # TODO IMPLEMENT
    else:
        raise NotImplementedError(f"Unknown kind of RedditObject to download: {reddit_object}")

    # Build the Praw objects
    if reddit_object.is_subreddit:
        reddit_object: Subreddit = reddit_object
        results = reddit.subreddit(reddit_object.subreddit_name)
    elif reddit_object.is_user:
        reddit_object: User = reddit_object
        results = Redditor(reddit, reddit_object.user_name)
        match reddit_object.user_page_kind:
            case UserPageKind.SUBMITTED:
                results = results.submissions
            case UserPageKind.COMMENTS:
                results = results.comments
            case UserPageKind.UPVOTED:
                results = results.upvoted()
            case UserPageKind.DOWNVOTED:
                results = results.downvoted()
            case UserPageKind.GILDED:
                results = results.gilded()
            case UserPageKind.SAVED:
                results = results.saved()
            # case UserPageKind.HISTORY:
            # results = results.todo
            # pass #TODO implement
            case UserPageKind.HIDDEN:
                results = results.hidden()
            case _:
                raise NotImplementedError(f"Not implemented: {reddit_object.user_page_kind}")

    else:
        raise NotImplementedError(f"Unknown kind of RedditObject to download: {reddit_object}")
    match reddit_object.sort_method:
        case SortMethod.HOT:
            results = results.hot(limit=None)  # TODO This is technically limited to 1000 posts :(
        case SortMethod.NEW:
            results = results.new(limit=None)
        case SortMethod.CONTROVERSIAL:
            results = results.controversial(reddit_object.top_kind.name.lower(), limit=None)
        case SortMethod.TOP:
            results = results.top(reddit_object.top_kind.name.lower(), limit=None)
        case SortMethod.BEST:
            results = results.best(limit=None)
        case SortMethod.RISING:
            results = results.rising(limit=None)
        case _:
            raise NotImplementedError(f"Unknown sort method: {reddit_object.sort_method}")

    print(f"Found {reddit_object.printable_name()}. Starting Download.")

    # Todo Convert imagehashsort.py database to object and use it here to determine whether to download an image.
    # Todo add known URLs to that library and import everything from RIPME (possibly include import information)
    # Todo Use SQLite as database format and enable imagehashsort.py to use the same database format
    # 1. Check if submission URL is already downloaded, skip
    # 2. Download the image into its appropriate location (?)
    # 3. Check if the phash is already known, if yes, delete the downloaded image
    # 4. (opt-out) rename image to its PHash
    # find images/gifs in subreddit
    img_extensions: list[str] = ['.jpg', '.jpeg', '.png']
    if cfg['reddit_downloader.download_gif']:
        img_extensions.append(".gif")
    try:
        count = 0
        submission: Submission
        for submission in results:
            if count >= limit:
                print(f"Reached limit of {limit} submissions to download!")
                break
            u: namedtuple = urlparse(submission.url)
            """The parts of the URL"""
            if "imgur.com/a/" in submission.url or "imgur.com/gallery/" in submission.url:
                downloader = ImgurAlbumDownloader()
                count += downloader.download(submission, cfg, destination_path)
            elif '://i.imgur.com/' in submission.url or '://i.redd.it' in submission.url:
                target_file = destination_path / Path(u.path).name  # Download a single file
                img_url = submission.url
                _, extension = os.path.splitext(u.path)
                if extension in img_extensions:
                    target_file.parent.mkdir(exist_ok=True, parents=True)
                    print(f'Downloading image {count} from {reddit_object.printable_name()} {submission.url}')
                    urllib.request.urlretrieve(img_url, filename=target_file)  # Download the full-size image
                    if cfg["metadata_scraper.write_metadata"]:
                        exif_data, iptc_data, xmp_data = actions.get_model_from_submission(target_file, submission)
                        if cfg['metadata_scraper.write_keywords']:
                            exif_data, iptc_data, xmp_data = actions.set_keywords((exif_data, iptc_data, xmp_data), submission, cfg)
                        actions.write_metadata(target_file, exif_data, iptc_data, xmp_data)
                    count += 1
                # .gifv file extensions do not play, convert to .gif
                # elif extension == '.gifv':
                #     print('\nDownloading', subreddit + str(count) + '.gif')
                #     print('Source:', img_url)
                #     print('Comments: https://www.reddit.com/r/' + subreddit + '/comments/' + str(submission))
                #     root, _ = os.path.splitext(img_url)
                #     img_url = root + '.gif'
                #     urllib.urlretrieve(img_url, 'images/%s%i%s' %
                #                        (subreddit, count, '.gif'))
                #     count += 1

    except PrawcoreException as e:
        print(f'Error accessing subreddit!\n{str(e)}')
