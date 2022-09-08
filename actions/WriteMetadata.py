"""
This module contains functions to write metadata to images
"""
import datetime as dt
from pathlib import Path

import praw.models
import pyexiv2


def write_metadata_from_reddit_submission(target_file: Path, submission: praw.models.Submission) -> None:
    """
    Write the metadata found in the given Reddit submission to the image
    :param target_file: Image to write
    :param submission: Reddit post to scrape for metadata
    :return: None
    """
    # For a reference, see https://exiv2.org/iptc.html
    # and https://github.com/LeoHsiao1/pyexiv2/blob/master/docs/Tutorial.md
    # and https://exiv2.org/tags.html
    # and https://praw.readthedocs.io/en/latest/code_overview/models/submission.html
    exif_data = {
        "Exif.Photo.DateTimeOriginal": dt.datetime.utcfromtimestamp(submission.created_utc).strftime("%Y:%m:%d %H:%M:%S"),
        "Exif.Image.DateTime": dt.datetime.utcfromtimestamp(submission.created_utc).strftime("%Y:%m:%d %H:%M:%S"),
        "Exif.Photo.DateTimeDigitized": dt.datetime.utcfromtimestamp(submission.created_utc).strftime("%Y:%m:%d %H:%M:%S"),
        'Exif.Image.Rating': None,  # Delete the rating
        "Exif.Image.ImageDescription": submission.title,
    }
    iptc_data = {
        "Iptc.Application2.Headline": submission.title,
        "Iptc.Application2.ObjectName": submission.title,
        "Iptc.Application2.Caption": submission.selftext,
        "Iptc.Application2.BylineTitle": "Reddit User",
        "Iptc.Application2.DateCreated": dt.datetime.utcfromtimestamp(submission.created_utc).strftime("%Y-%m-%d"),
        "Iptc.Application2.TimeCreated": dt.datetime.utcfromtimestamp(submission.created_utc).strftime("%H:%M:%S"),
        "Iptc.Application2.Source": "r/" + submission.subreddit.display_name,
        "Iptc.Application2.Contact": "https://www.reddit.com" + submission.permalink,
    }
    xmp_data = {
        "Xmp.xmp.CreateDate": dt.datetime.utcfromtimestamp(submission.created_utc).strftime("%Y-%M-%DT%H:%M:%S") + ".000",
        'Xmp.xmp.Rating': None,  # Delete the rating, if there is any
        'Xmp.photoshop.AuthorsPosition': "Reddit User",
        'Xmp.photoshop.Source': "https://www.reddit.com" + submission.permalink,
        'Xmp.dc.title': "lang=\"x-default\" " + submission.title,
        'Xmp.dc.description': "lang=\"x-default\" " + submission.selftext,
        'Xmp.dc.rights': "lang=\"x-default\" https://www.reddit.com" + submission.permalink,
        'Xmp.iptc.CreatorContactInfo/Iptc4xmpCore:CiUrlWork': "https://www.reddit.com" + submission.permalink,
        'Xmp.xmpMM.PreservedFileName': target_file.name,
        'Xmp.crs.RawFileName': target_file.name,
    }
    if submission.author is not None:  # For deleted users, the author is None
        exif_data['Exif.Image.Artist'] = "u/" + submission.author.name
        iptc_data['Iptc.Application2.Byline'] = "u/" + submission.author.name
        xmp_data['Xmp.dc.creator'] = "u/" + submission.author.name
    if submission.author_flair_text is not None:
        iptc_data["Iptc.Application2.BylineTitle"] += f" ({submission.author_flair_text})"
    return write_metadata(target_file, exif_data, iptc_data, xmp_data)


def write_metadata(target_file: Path, exif_data: dict[str, str], iptc_data: dict[str, str], xmp_data: dict[str, str]) -> None:
    """
    Write the given metadata to an image file

    :param xmp_data:
    :param iptc_data:
    :param exif_data:
    :param target_file: File to write
    :return: None
    """

    with pyexiv2.Image(target_file.as_posix()) as metadata:
        metadata.modify_exif(exif_data)
        metadata.modify_iptc(iptc_data)
        metadata.modify_xmp(xmp_data)
