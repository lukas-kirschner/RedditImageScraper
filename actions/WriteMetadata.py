"""
This module contains functions to write metadata to images
"""
import datetime as dt
from pathlib import Path
from typing import Optional

import praw.models
import pyexiv2

MetadataModel = tuple[dict[str, str], dict[str, str], dict[str, str]]


def set_time_created(model: MetadataModel, epoch: int) -> MetadataModel:
    """
    Set the time created to the time specified by the given epoch.

    :param model: Model to set
    :param epoch: Epoch
    :return: the new model
    """
    exif_data, iptc_data, xmp_data = model
    # Set Exif Time
    exif_data["Exif.Photo.DateTimeOriginal"] = dt.datetime.utcfromtimestamp(epoch).strftime("%Y:%m:%d %H:%M:%S")
    exif_data["Exif.Image.DateTime"] = dt.datetime.utcfromtimestamp(epoch).strftime("%Y:%m:%d %H:%M:%S")
    exif_data["Exif.Photo.DateTimeDigitized"] = dt.datetime.utcfromtimestamp(epoch).strftime("%Y:%m:%d %H:%M:%S")
    # Set IPTC Time
    iptc_data["Iptc.Application2.DateCreated"] = dt.datetime.utcfromtimestamp(epoch).strftime("%Y-%m-%d")
    iptc_data["Iptc.Application2.TimeCreated"] = dt.datetime.utcfromtimestamp(epoch).strftime("%H:%M:%S")
    # Set XMP Time
    xmp_data["Xmp.xmp.CreateDate"] = dt.datetime.utcfromtimestamp(epoch).strftime("%Y-%M-%DT%H:%M:%S") + ".000"
    xmp_data["Xmp.acdsee.datetime"] = dt.datetime.utcfromtimestamp(epoch).strftime("%Y:%m:%d %H:%M:%S")
    xmp_data["Xmp.dc.date"] = dt.datetime.utcfromtimestamp(epoch).strftime("%Y-%M-%DT%H:%M:%S")
    return exif_data, iptc_data, xmp_data


def set_post_title(model: MetadataModel, title: str) -> MetadataModel:
    """
    Set the post title of the post's metadata.

    :param model: Model to set
    :param title: Post title
    :return: the new model
    """
    exif_data, iptc_data, xmp_data = model
    # Set Exif title
    exif_data["Exif.Image.ImageDescription"] = title
    # Set IPTC title
    iptc_data["Iptc.Application2.Headline"] = title
    iptc_data["Iptc.Application2.ObjectName"] = title
    # Set XMP title
    xmp_data["Xmp.acdsee.caption"] = title
    xmp_data["Xmp.dc.title"] = "lang=\"x-default\" " + title
    return exif_data, iptc_data, xmp_data


def get_model_from_submission(target_file: Optional[Path], submission: praw.models.Submission) -> MetadataModel:
    """
    Get the metadata model from the given submission.

    :param target_file: Target file to write, or None, if not applicable
    :param submission: Submission to scrape
    :return: the model
    """
    # For a reference, see https://exiv2.org/iptc.html
    # and https://github.com/LeoHsiao1/pyexiv2/blob/master/docs/Tutorial.md
    # and https://exiv2.org/tags.html
    # and https://praw.readthedocs.io/en/latest/code_overview/models/submission.html
    upvotes_comment: str = f"{submission.score} upvotes ({submission.upvote_ratio}%), {submission.num_comments} comments."
    exif_data = {
        'Exif.Image.Rating': None,  # Delete the rating
    }
    iptc_data = {
        "Iptc.Application2.Caption": submission.selftext,
        "Iptc.Application2.BylineTitle": "Reddit User",
        "Iptc.Application2.Source": "r/" + submission.subreddit.display_name,
        "Iptc.Application2.Contact": "https://www.reddit.com" + submission.permalink,
    }
    xmp_data = {
        'Xmp.xmp.Rating': None,  # Delete the rating, if there is any
        'Xmp.photoshop.AuthorsPosition': "Reddit User",
        'Xmp.photoshop.Source': "https://www.reddit.com" + submission.permalink,
        'Xmp.acdsee.rating': 0,
        'Xmp.acdsee.notes': (submission.selftext + "\n" + upvotes_comment).strip()[:4095],
        'Xmp.dc.description': "lang=\"x-default\" " + (submission.selftext + "\n" + upvotes_comment).strip(),
        'Xmp.dc.rights': "lang=\"x-default\" https://www.reddit.com" + submission.permalink,
        'Xmp.dc.source': "https://www.reddit.com" + submission.permalink,
        'Xmp.iptc.CreatorContactInfo/Iptc4xmpCore:CiUrlWork': "https://www.reddit.com" + submission.permalink,
        'Xmp.exif.UserComment': upvotes_comment,
    }
    if target_file is not None:
        xmp_data["Xmp.xmpMM.PreservedFileName"] = target_file.name
        xmp_data["Xmp.crs.RawFileName"] = target_file.name
    if submission.author is not None:  # For deleted users, the author is None
        exif_data['Exif.Image.Artist'] = "u/" + submission.author.name
        iptc_data['Iptc.Application2.Byline'] = "u/" + submission.author.name
        xmp_data['Xmp.dc.creator'] = "u/" + submission.author.name
        xmp_data['Xmp.acdsee.author'] = "u/" + submission.author.name
    if submission.author_flair_text is not None:
        iptc_data["Iptc.Application2.BylineTitle"] += f" ({submission.author_flair_text})"
    exif_data, iptc_data, xmp_data = set_time_created((exif_data, iptc_data, xmp_data), submission.created_utc)
    exif_data, iptc_data, xmp_data = set_post_title((exif_data, iptc_data, xmp_data), submission.title)
    return exif_data, iptc_data, xmp_data


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
