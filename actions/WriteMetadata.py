"""
This module contains functions to write metadata to images
"""
import datetime as dt
from pathlib import Path
from typing import Optional

import praw.models
import pyexiv2
from config import Config

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
    xmp_data["Xmp.xmpDM.releaseDate"] = dt.datetime.utcfromtimestamp(epoch).strftime("%Y-%M-%DT%H:%M:%S")
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
    exif_data["Exif.Image.XPTitle"] = title
    # Set IPTC title
    iptc_data["Iptc.Application2.Headline"] = title
    iptc_data["Iptc.Application2.ObjectName"] = title
    # Set XMP title
    xmp_data["Xmp.acdsee.caption"] = title
    xmp_data["Xmp.dc.title"] = "lang=\"x-default\" " + title
    return exif_data, iptc_data, xmp_data


def set_author(model: MetadataModel, author: str) -> MetadataModel:
    """
    Set the post author of the post's metadata.

    :param model: Model to set
    :param author: Post author
    :return: the new model
    """
    # Set EXIF Author
    exif_data, iptc_data, xmp_data = model
    exif_data['Exif.Image.Artist'] = author
    exif_data['Exif.Image.XPAuthor'] = author
    # Set IPTC Author
    iptc_data['Iptc.Application2.Byline'] = author
    # Set XMP Author
    xmp_data['Xmp.xmpRights.Owner'] = author
    xmp_data['Xmp.dc.creator'] = author
    xmp_data['Xmp.acdsee.author'] = author
    xmp_data['Xmp.xmpDM.artist'] = author
    return exif_data, iptc_data, xmp_data


def set_long_comment(model: MetadataModel, comment: str) -> MetadataModel:
    """
    Attach a long comment without character limitations to the metadata

    :param model: Model to set
    :param comment: Comment to attach
    :return: the new model
    """
    exif_data, iptc_data, xmp_data = model
    # Set EXIF Comment
    exif_data['Exif.Photo.UserComment'] = comment
    # Set XMP Comment
    xmp_data['Xmp.exif.UserComment'] = comment
    xmp_data['Xmp.xmpDM.comment'] = comment
    xmp_data['Xmp.dc.description'] = ("lang=\"x-default\" " + comment).strip()
    xmp_data['Xmp.acdsee.notes'] = comment.strip()[:4095]
    return exif_data, iptc_data, xmp_data


def set_keywords(model: MetadataModel, submission: praw.models.Submission, cfg: Config) -> MetadataModel:
    """
    Set the keyword hierarchy.
    For DigiKam, according to the specification, the hierarchy separator is always a '/' character.
    All other programs use the lightroom hierarchy separator from the global config.
    This does not write any IPTC tags, since Lightroom cannot import hierarchical tags if IPTC tags are present.

    :param cfg: Global Config
    :param model: Model to set
    :param submission: Submission that was scraped
    :return: the new model
    """
    lightroom_sep: str = cfg['metadata_scraper.lightroom_hierarchy_separator']
    subreddit_name: str = cfg['metadata_scraper.subreddit_name']
    user_name: str = cfg['metadata_scraper.user_name']
    exif_data, iptc_data, xmp_data = model
    # Set XMP keywords
    # noinspection PyTypeChecker
    xmp_data["Xmp.dc.subject"] = [subreddit_name, submission.subreddit.display_name]
    # noinspection PyTypeChecker
    xmp_data["Xmp.lr.hierarchicalSubject"] = [f"{subreddit_name}{lightroom_sep}{submission.subreddit.display_name}"]
    # noinspection PyTypeChecker
    xmp_data["Xmp.acdsee.categories"] = [f"{subreddit_name}{lightroom_sep}{submission.subreddit.display_name}"]
    # noinspection PyTypeChecker
    xmp_data["Xmp.digiKam.TagsList"] = [f"{subreddit_name}/{submission.subreddit.display_name}"]

    if submission.author is not None:  # Set User Keywords
        # noinspection PyTypeChecker
        xmp_data["Xmp.dc.subject"] += [user_name, submission.author.name]
        xmp_data["Xmp.lr.hierarchicalSubject"] += [f"{user_name}{lightroom_sep}{submission.author.name}"]
        xmp_data["Xmp.acdsee.categories"] += [f"{user_name}{lightroom_sep}{submission.author.name}"]
        xmp_data["Xmp.digiKam.TagsList"] += [f"{user_name}/{submission.author.name}"]
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
        'Xmp.xmp.Rating': None,  # Delete the rating, if present
        'Xmp.photoshop.AuthorsPosition': "Reddit User",
        'Xmp.photoshop.Source': "https://www.reddit.com" + submission.permalink,
        'Xmp.acdsee.rating': None,  # Delete the rating, if present
        'Xmp.dc.rights': "lang=\"x-default\" https://www.reddit.com" + submission.permalink,
        'Xmp.dc.source': "https://www.reddit.com" + submission.permalink,
        'Xmp.iptc.CreatorContactInfo/Iptc4xmpCore:CiUrlWork': "https://www.reddit.com" + submission.permalink,
    }
    if target_file is not None:
        xmp_data["Xmp.xmpMM.PreservedFileName"] = target_file.name
        xmp_data["Xmp.crs.RawFileName"] = target_file.name
    if submission.author is not None:  # For deleted users, the author is None
        exif_data, iptc_data, xmp_data = set_author((exif_data, iptc_data, xmp_data), "u/" + submission.author.name)
    if submission.author_flair_text is not None:
        iptc_data["Iptc.Application2.BylineTitle"] += f" ({submission.author_flair_text})"
    exif_data, iptc_data, xmp_data = set_time_created((exif_data, iptc_data, xmp_data), submission.created_utc)
    exif_data, iptc_data, xmp_data = set_post_title((exif_data, iptc_data, xmp_data), submission.title)
    exif_data, iptc_data, xmp_data = set_long_comment((exif_data, iptc_data, xmp_data), upvotes_comment)
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
