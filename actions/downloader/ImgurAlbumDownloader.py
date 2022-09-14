#!/usr/bin/env python3
import datetime as dt
import json
import pprint
import sys
import urllib
import urllib.request
from collections import namedtuple
from copy import deepcopy
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests
from config import Config
from praw.models import Submission

import actions
from actions import get_imgur_client_id
from actions.downloader.Downloader import Downloader


class NotAnImgurAlbumUrlError(Exception):

    def __init__(self, url, *args: object) -> None:
        super().__init__(f"Not a valid Imgur album URL: {url}", *args)


class ImgurAlbumDownloader(Downloader):
    """
    A downloader that downloads whole Imgur albums and sorts their images into a subfolder
    """

    def download(self, submission: Submission, cfg: Config, destination: Path) -> int:
        url: str = submission.url
        if cfg["metadata_scraper.write_metadata"]:
            meta_object = actions.get_model_from_submission(None, submission)
        else:
            meta_object = None
        client_id = get_imgur_client_id(cfg)
        return self.download_single_album(url, destination, client_id, reddit_post_metadata=meta_object)

    # noinspection PyMethodMayBeStatic
    def download_single_album(self, url: str, target_path: Path, client_id: str, /, debug=False,
                              reddit_post_metadata: Optional[tuple[dict[str, str], dict[str, str], dict[str, str]]] = None) -> int:
        """
        Download a single given Imgur album and store it into the appropriate subfolder in the given path.
        The subfolder is the title of the imgur album, plus a unique identifier (the id part of the imgur URL).

        :param reddit_post_metadata: The base metadata of the reddit post, or None, if no metadata should be scraped at all
        :param client_id: Imgur Client ID
        :param url: URL to download
        :param target_path: Target path where the subfolder shall be created
        :return: the number of downloaded images
        """
        if not url.endswith("/"):
            url += "/"  # Makes parsing easier
        if 'imgur.com/a/' in url:
            urlstart = 'imgur.com/a/'
            album = True
        elif 'imgur.com/gallery/' in url:
            urlstart = 'imgur.com/gallery/'
            album = False
        else:
            raise NotAnImgurAlbumUrlError(url)
        ind: int = url.find(urlstart)
        if ind == -1:
            raise NotAnImgurAlbumUrlError(url)
        ind = ind + len(urlstart)
        album_id: str = url[ind:url.find("/", ind)]
        api_url: str = f"https://api.imgur.com/3/{'album' if album else 'gallery'}/{album_id}"
        headers = {'Authorization': f'Client-ID {client_id}'}
        if debug:
            print(f"{headers=}\n{api_url=}\n{url[ind:]=}")
        response = requests.request("GET", api_url, headers=headers)
        if debug:
            print(f"{response=}\n{response.status_code=}\n{response.text=}")
        if response.status_code != 200:
            # TODO Handle errors here
            return 0
        success_json = json.loads(response.text)
        pprint.pprint(success_json)

        album_title: str = f"{success_json['data']['title']}" \
            if success_json['data']['title'] is not None else success_json['data']['id']
        album_description: str = f"{success_json['data']['description'] if success_json['data']['description'] is not None else ''}"
        album_epoch: int = int(success_json['data']['datetime'])
        album_title_id: str = f"{album_title} {success_json['data']['id']}".strip()
        """A unique album identifier that is both unique and human-readable"""

        if success_json['data']['is_album']:
            target_folder: Path = target_path / album_title_id
            images: list[dict[str, str]] = success_json['data']['images']
        else:
            # This is not an album, but an image in itself!
            target_folder: Path = target_path
            images: list[dict[str, str]] = [success_json['data']]

        # Download the images and add metadata
        downloaded: int = 0
        for i, image_data in enumerate(images):
            if image_data['is_ad']:
                if debug:
                    print(f"Skipped image {image_data['link']} because it is an ad")
                continue  # Skip ads
            image_title: str = "" if image_data['title'] is None else image_data['title']
            image_description: str = "" if image_data['description'] is None else image_data['description']
            image_url: str = image_data['link']
            image_u: namedtuple = urlparse(image_data['link'])
            image_epoch: int = int(image_data['datetime'])

            # Download the image
            image_file: Path = target_folder / f"{i + 1:02d} {Path(image_u.path).name}"
            image_file.parent.mkdir(exist_ok=True, parents=True)
            urllib.request.urlretrieve(image_url, filename=image_file)
            downloaded += 1

            # Add metadata
            if reddit_post_metadata is not None:
                br: str = '\n'
                add_comment: str = f"Imgur Album: {album_title} {success_json['data']['link']} " \
                                   f"({success_json['data'].get('images_count', '1')} images)" \
                                   f"{(br + album_description) if album_description else ''}\n" \
                                   f"Album Views: {success_json['data']['views']}, Image Views: {image_data['views']}, " \
                                   f"Account name: {success_json['data']['account_url']} ({success_json['data']['account_id']})\n" \
                                   f"Album Upvotes on Imgur: {success_json['data'].get('ups', 'N/A')}, " \
                                   f"Points: {success_json['data'].get('points', 'N/A')}, " \
                                   f"Score: {success_json['data'].get('score', 'N/A')}, " \
                                   f"Number of Comments: Image {image_data.get('comment_count', 'N/A')} Album " \
                                   f"{success_json['data'].get('comment_count', 'N/A')}.\n" \
                                   f"Album uploaded: {dt.datetime.utcfromtimestamp(album_epoch).strftime('%Y:%m:%d %H:%M:%S')}"
                exif, iptc, xmp = deepcopy(reddit_post_metadata)
                exif, iptc, xmp = actions.set_time_created((exif, iptc, xmp), image_epoch)
                if image_title:
                    if exif.get("Exif.Image.ImageDescription", "") != "":  # Append reddit post title
                        image_title += " - " + exif["Exif.Image.ImageDescription"]
                    actions.set_post_title((exif, iptc, xmp), image_title)
                if album_description:
                    image_description = (image_description + "\n" + "(" + album_description + ")").strip()
                if image_description:
                    iptc["Iptc.Application2.Caption"] = image_description.strip()
                xmp['Xmp.exif.UserComment'] = (xmp.get('Xmp.exif.UserComment', "") + "\n" + add_comment).strip()
                xmp['Xmp.dc.description'] = xmp.get('Xmp.dc.description', "") + "\n" + (image_description + "\n" + add_comment).strip()
                xmp["Xmp.xmpMM.PreservedFileName"] = image_file.name
                xmp["Xmp.crs.RawFileName"] = image_file.name
                xmp["Xmp.xmpDM.album"] = album_title_id
                actions.write_metadata(image_file, exif, iptc, xmp)

        return downloaded


def test() -> int:
    credentials_file: Path = Path("credentials.json")
    with credentials_file.open("r") as cf:
        credentials = json.load(cf)
    downloader: ImgurAlbumDownloader = ImgurAlbumDownloader()
    # Gallery link to album
    downloader.download_single_album("https://imgur.com/gallery/P3K8Z", Path("testpics-Albums"), credentials['imgur_client_id'], debug=True,
                                     reddit_post_metadata=({}, {}, {}))
    # Album direct link
    downloader.download_single_album("https://imgur.com/a/XTVbp/", Path("testpics-Albums"), credentials['imgur_client_id'], debug=True,
                                     reddit_post_metadata=({}, {}, {}))
    # Gallery link to single image
    downloader.download_single_album("https://imgur.com/gallery/u1j9f7T", Path("testpics-Albums"), credentials['imgur_client_id'], debug=True,
                                     reddit_post_metadata=({}, {}, {}))
    return 0


if __name__ == "__main__":
    sys.exit(test())
