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
# - Store a URL history, like Ripme
# - Use sqlite or Mongodb for all storage files
import argparse
import sys
from pathlib import Path
from textwrap import dedent
from typing import Optional

import xdg
from config import Config

from actions import scrape_subreddit
from reddit import RedditObject, NoValidRedditObjectError

_default_config: str = dedent("""
metadata_scraper: { # Configuration related to the metadata scraper
    write_metadata: true # Setting this to false completely disables the metadata scraper
},
reddit_connector: { # Configuration related to the reddit connector
    use_credential_file: true, # If true, use a credentials file and ignore the credentials provided below
    credential_file: 'credentials.json', # Path of the credentials file
    client_id: '', # Client ID to use for login
    client_secret: '', # Client Secret
    user_agent: '' # User agent
},
reddit_downloader: { # Configuration related to the reddit downloader
    download_gif: false # If true, download .gif files from imgur and reddit
}
""")
"""The default config that is saved if a config file could not be found"""


def main():
    # Initialize global paths
    xdg_conf: Path = xdg.xdg_config_home()
    if xdg_conf is None:
        config_base_dir: Path = (Path.home() / ".config").absolute()
        print(f"XDG_CONFIG_HOME is not set! Attempting to store the global config in {config_base_dir}", file=sys.stderr)
    else:
        config_base_dir: Path = xdg_conf / "RedditImageScraper"
    config_base_dir.mkdir(exist_ok=True, parents=False)

    xdg_data: Path = xdg.xdg_data_home()
    if xdg_data is None:
        data_base_dir: Path = (Path.home() / ".local/share").absolute()
        print(f"XDG_DATA_HOME is not set! Attempting to store application data in {data_base_dir}", file=sys.stderr)
    else:
        data_base_dir: Path = xdg_data / "RedditImageScraper"
    data_base_dir.mkdir(exist_ok=True, parents=False)

    # Initialize Argument Parser
    parser = argparse.ArgumentParser(prog="Reddit Image Scraper",
                                     description='A Reddit Image Downloader that supports metadata scraping.')
    parser.add_argument('-s', '--subreddit', required=True, action="store", dest='subreddit',
                        help='Specify the subreddit or user account to scrape. Valid formats include "https://www.reddit.com/r/wallpapers/",'
                             ' "wallpapers", "r/wallpapers", "u/exampleuser", "reddit.com/user/exampleuser/submitted/?sort=top&t=day"')
    parser.add_argument('-l', '--limit', required=False, action="store", type=int, dest='limit', default=None,
                        help='Specify the maximum number of new images to download')
    parser.add_argument('-o', '--out-dir', required=False, action="store", dest="dest_dir", default='out',
                        help='Specify the destination directory to download scraped files into. Default is "out/"')
    parser.add_argument('-c', '--config', required=False, action="store", dest="config_file", default=None,
                        help='Specifies the config file to read the configuration from. Defaults to a global config file '
                             'in the user\'s configuration directory.')
    args = parser.parse_args()

    dest_dir: Path = Path(args.dest_dir)

    cfg_file: Path = Path(args.config_file) if args.config_file is not None else (xdg_conf / "RedditImageScraper.cfg")
    if not cfg_file.is_file():  # Write the default config file
        with cfg_file.open("w") as cf:
            cf.write(_default_config)
    with cfg_file.open("r") as cf:
        cfg: Config = Config(cf)

    # initialize variables
    try:
        subreddit: RedditObject = RedditObject.from_user_string(args.subreddit)
    except NoValidRedditObjectError as e:
        print(e, file=sys.stderr)
        print(f"Could not parse subreddit or user account {args.subreddit}:\n{str(e)}")
        sys.exit(1)
    num_pics: Optional[int] = args.limit

    scrape_subreddit(subreddit, num_pics, dest_dir, cfg)


if __name__ == '__main__':
    main()
