from abc import ABCMeta, abstractmethod
from pathlib import Path

from config import Config
from praw.models import Submission


class Downloader(metaclass=ABCMeta):
    """
    The abstract downloader base class
    """

    @abstractmethod
    def download(self, submission: Submission, cfg: Config, destination: Path) -> int:
        """
        Download the content of the given submission
        :param destination: Destination to download the files into
        :param cfg: Global Config
        :param submission: Submission to download
        :return: the number of successfully downloaded images
        """
        pass
