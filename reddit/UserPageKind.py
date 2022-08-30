from enum import Enum


class UserPageKind(Enum):
    """This class represents a User Page Kind"""
    SUBMITTED = 0,
    """Show the User's Submissions"""
    COMMENTS = 1,
    """Show the User's Comments"""
    GILDED = 2,
    """Show the User's gilded posts and comments"""
    SAVED = 3,
    """Show the user's saved posts"""
    HISTORY = 4,
    """Show the User's History"""
    HIDDEN = 5,
    """Show the user's hidden posts"""
    UPVOTED = 6,
    """Show the posts and comments upvoted by the user"""
    DOWNVOTED = 7,
    """Show the posts and comments downvoted by the user"""
