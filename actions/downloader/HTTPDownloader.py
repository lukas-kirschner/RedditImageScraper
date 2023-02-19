import os
import urllib.request
from collections import namedtuple
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlparse

from config import Config
from imagehashsort import ImageDatabase, perceptual_hash
from praw.models import Submission

import actions
from actions.downloader import Downloader
from database import URLManager


class HTTPDownloader(Downloader):
    """
    A downloader that downloads images that are directly linked in a subreddit
    """

    def download(self, submission: Submission, cfg: Config, destination: Path, urlmanager: URLManager, library: ImageDatabase) -> int:
        img_extensions: list[str] = ['.jpg', '.jpeg', '.png']
        if cfg['reddit_downloader.download_gif']:
            img_extensions.append(".gif")
        u: namedtuple = urlparse(submission.url)
        target_file = destination / Path(u.path).name
        img_url = submission.url
        _, extension = os.path.splitext(u.path)
        if extension not in img_extensions:
            return 0
        target_file.parent.mkdir(exist_ok=True, parents=True)
        try:
            urllib.request.urlretrieve(img_url, filename=target_file)  # Download the full-size image
        except HTTPError as e:
            if e.code == 404:
                print(f"{img_url} could not be downloaded (404 not found)!")
                return 0
        imhash = perceptual_hash(target_file)
        if cfg["reddit_downloader.discard_phashed_duplicates"] and library.hash_in_hashes(imhash):
            print(f"{target_file} was detected to be a perceptual duplicate of another image and will be deleted!")
            target_file.unlink()
            return 0
        library.store_image(target_file, imhash)
        # library.save()  # TODO Interval?
        if cfg["metadata_scraper.write_metadata"]:
            exif_data, iptc_data, xmp_data = actions.get_model_from_submission(target_file, submission)
            if cfg['metadata_scraper.write_keywords']:
                exif_data, iptc_data, xmp_data = actions.set_keywords((exif_data, iptc_data, xmp_data), submission, cfg)
            actions.write_metadata(target_file, exif_data, iptc_data, xmp_data)
        return 1
