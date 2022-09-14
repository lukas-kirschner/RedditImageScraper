import sys
from collections import namedtuple
from pathlib import Path
from urllib.parse import urlparse


# noinspection PyMethodMayBeStatic
class URLManager:
    """
    A URL Manager that manages URLs that have already been downloaded
    """

    def __init__(self, database_file: Path) -> None:
        """
        Init a new URL Manager with the given Database File.
        :param database_file: Database File
        """
        super().__init__()
        self.database_file: Path = database_file
        self.database_file.touch(exist_ok=True)
        self.paths: set[str] = set()
        with self.database_file.open("r") as df:
            for line in df:
                url: str = line.strip()
                if url:
                    try:
                        urlparts = urlparse(url)
                    except ValueError:
                        print(f"File {self.database_file.as_posix()} contained invalid URL {url}", file=sys.stderr)
                        continue
                    self.paths.add(self._url_to_lookupstring(urlparts))

    def _url_to_lookupstring(self, url: namedtuple) -> str:
        """
        Convert the given URL to a lookup string
        :param url: URL, as parsed by urlparse
        :return: the lookup string
        """
        ret: str = f"{url.netloc}{url.path}"
        ret.removeprefix("www.")
        return ret

    def url_already_in_database(self, url: str) -> bool:
        """
        Check if the given URL is valid and already in the database
        :param url: URL to check
        :return: True, if the valid URL is already in the database
        """
        try:
            urlparts = urlparse(url)
        except ValueError:
            return False
        return self.parsed_url_already_in_database(urlparts)

    def parsed_url_already_in_database(self, urlparts: namedtuple) -> bool:
        """
        Check if the given parsed URL is valid and already in the database
        :param urlparts: URL to check
        :return: True, if the valid URL is already in the database
        """
        return self._url_to_lookupstring(urlparts) in self.paths

    def add_url_to_database(self, url: str) -> None:
        """
        Add the given URL to the database. This operation might be expensive, i.e. write data to the database immediately!
        :param url: URL to write
        :return: None
        """
        try:
            urlparts = urlparse(url)
        except ValueError:
            return
        lookupstr: str = self._url_to_lookupstring(urlparts)
        if lookupstr in self.paths:
            return
        with self.database_file.open("a") as df:
            df.write(f"{url}\n")
        self.paths.add(lookupstr)
