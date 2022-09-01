#!/usr/bin/env python3
"""

Reddit Image Downloader

Usage: download_images.py [-s SUBREDDIT] [-n NUMBER OF PICTURES] [-p PAGE] [-q SEARCH QUERY]

-h --help                           show this
-s --subreddit SUBREDDIT            specify subreddit
-n --number NUMBER OF PICTURES      specify number of pictures to download [default: 20]
-p --page PAGE                      hot, top, controversial, new, rising [default: hot]
-q --query SEARCH QUERY             specify a specific search term

"""
# TODOS
# - Change to argparse
# - Convert Python3 & style
# - Change to an object-oriented design
# - Use phash from imagehashsort.py to filter out images with a known hash or directory name
# - Store credentials in a central place and ask from user
# - Store all configuration in system config folder, like ripme
# - Store a URL history, like Ripme
# - Use sqlite or Mongodb for all storage files
import argparse
import sys
from pathlib import Path
from typing import Optional

from actions import scrape_subreddit
from reddit import RedditObject, NoValidRedditObjectError


def main():
    parser = argparse.ArgumentParser(prog="Reddit Image Scraper",
                                     description='A Reddit Image Downloader that supports metadata scraping.')
    parser.add_argument('-s', '--subreddit', required=True, action="store", dest='subreddit',
                        help='Specify the subreddit or user account to scrape. Valid formats include "https://www.reddit.com/r/wallpapers/",'
                             ' "wallpapers", "r/wallpapers", "u/exampleuser", "reddit.com/user/exampleuser/submitted/?sort=top&t=day"')
    parser.add_argument('-l', '--limit', required=False, action="store", type=int, dest='limit', default=None,
                        help='Specify the maximum number of new images to download')
    parser.add_argument('-o', '--out-dir', required=False, action="store", dest="dest_dir", default='out',
                        help='Specify the destination directory to download scraped files into. Default is "out/"')
    args = parser.parse_args()

    # Init Source DirTODO
    dest_dir: Path = Path(args.dest_dir)

    # initialize variables
    try:
        subreddit: RedditObject = RedditObject.from_user_string(args.subreddit)
    except NoValidRedditObjectError as e:
        print(e, file=sys.stderr)
        print(f"Could not parse subreddit or user account {args.subreddit}:\n{str(e)}")
        sys.exit(1)
    num_pics: Optional[int] = args.limit

    scrape_subreddit(subreddit, num_pics, dest_dir)


if __name__ == '__main__':
    main()
