from abc import ABCMeta, abstractmethod
from pathlib import Path

from config import Config
from imagehashsort import ImageDatabase
from praw.models import Submission

from database import URLManager


class Downloader(metaclass=ABCMeta):
    """
    The abstract downloader base class
    """

    @abstractmethod
    def download(self, submission: Submission, cfg: Config, destination: Path, urlmanager: URLManager, library: ImageDatabase) -> int:
        """
        Download the content of the given submission
        :param library: Perceptual Hash Library
        :param urlmanager: URL Manager with already-downloaded URLs
        :param destination: Destination to download the files into
        :param cfg: Global Config
        :param submission: Submission to download
        :return: the number of successfully downloaded images
        """
        pass
