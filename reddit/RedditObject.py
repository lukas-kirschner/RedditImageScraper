"""
This file contains all classes that are downloadable Reddit Objects
"""
from __future__ import annotations

from abc import ABCMeta
from typing import Any

from reddit.SortMethod import SortMethod
from reddit.TopKind import TopKind
from reddit.UserPageKind import UserPageKind


class NoValidRedditObjectError(Exception):
    def __init__(self, string: str, *args: object) -> None:
        super().__init__(f"The given request was not a valid RedditObject: \"{string}\"", *args)


# noinspection HttpUrlsUsage
class RedditObject(metaclass=ABCMeta):
    _URLHOST: str = f"www.reddit.com"

    def __init__(self, sort_method: SortMethod, top_kind: TopKind, https: bool):
        self.https = https
        self.sort_method: SortMethod = sort_method
        self.top_kind: TopKind = top_kind

    @property
    def is_subreddit(self) -> bool:
        """
        Check if this reddit object is a Subreddit.
        :return: True, if this Reddit object is a Subreddit
        """
        return False

    @property
    def is_user(self) -> bool:
        """
        Check if this reddit object is a User.
        :return: True, if this Reddit object is a User
        """
        return False

    @staticmethod
    def from_user_string(user_string: str, /, default_top_kind: TopKind = next(iter(TopKind)),
                         default_sort_method: SortMethod = next(iter(SortMethod)),
                         default_user_page: UserPageKind = next(iter(UserPageKind))) -> RedditObject:
        """
        Convert a user's request into the appropriate user string
        :param default_user_page: User Page Kind to choose if no one is given. Defaults to the first UserPageKind that is declared in UserPageKind
        :param default_top_kind: Top Kind to choose if no one is given. Defaults to the first TopKind that is declared in TopKind
        :param default_sort_method: Sort Method to choose if no one is given. Defaults to the first SortMethod that is declared in SortMethod
        :param user_string: User string given by the user
        :return: a Reddit Object
        :raises NoValidRedditObject: if the given request string is not a valid RedditObject
        """
        SUBREDDIT, USER = 0, 1

        def parse_enum(remaining_string: str, type: Any) -> tuple[str, Any]:
            tk = ""
            while len(remaining_string) > 0 and remaining_string[0].isalpha():
                tk += remaining_string[0]
                remaining_string = remaining_string[1:]
            if len(tk) == 0:
                raise NoValidRedditObjectError(user_string, f"Expected {type}, instead got {remaining_string}")
            try:
                return remaining_string, type[tk.upper()]
            except KeyError:
                raise NoValidRedditObjectError(user_string, f"Not a {type}: {rem}")

        def parse_topkind(rem: str) -> tuple[str, TopKind]:
            return parse_enum(rem, TopKind)

        def parse_sortmethod(rem: str) -> tuple[str, SortMethod]:
            return parse_enum(rem, SortMethod)

        def parse_userpage(rem: str) -> tuple[str, SortMethod]:
            return parse_enum(rem, UserPageKind)

        def parse_slashes(rem: str, expect=False) -> str:
            if len(rem) == 0 or rem[0] != '/':
                if expect:
                    raise NoValidRedditObjectError(user_string, f"Expected a slash before {rem}")
                else:
                    return rem
            while len(rem) > 0 and rem[0] == '/':
                rem = rem[1:]
            return rem

        def parse_variable_name(rem: str) -> tuple[str, str]:
            """Parse a variable name given like variable=value... and return "value..." """
            if len(rem) == 0:
                raise NoValidRedditObjectError(user_string, f"Expected a variable identifier after the question mark, instead got {rem}")
            ret = ""
            while len(rem) > 0 and rem[0] != '=':
                ret += rem[0]
                rem = rem[1:]
            if len(rem) > 0 and rem[0] == '=':
                rem = rem[1:]
            return rem, ret

        rem: str = user_string.strip()

        # Parse the protocol
        if rem.lower().startswith("https://"):
            https = True
            rem = rem[len("https://"):]
        elif rem.lower().startswith("http://"):
            https = False
            rem = rem[len("http://"):]
        else:
            https = True
        rem = parse_slashes(rem)

        # Parse the host
        if rem.lower().startswith("www.reddit.com/"):
            rem = rem[len("www.reddit.com/"):]
        elif rem.lower().startswith("reddit.com/"):
            rem = rem[len("reddit.com/"):]
        rem = parse_slashes(rem)

        # Parse the kind
        if rem.lower().startswith("r/"):
            kind = SUBREDDIT
            rem = rem[len("r/"):]
        elif rem.lower().startswith("user/"):
            kind = USER
            rem = rem[len("user/"):]
        elif rem.lower().startswith("u/"):
            kind = USER
            rem = rem[len("u/"):]
        else:
            kind = SUBREDDIT
        rem = parse_slashes(rem)

        # Parse Name
        def is_allowable_character(char: str):
            return char.isalnum() or char == '_'

        if len(rem) == 0 or not is_allowable_character(rem[0]):
            raise NoValidRedditObjectError(user_string, f"Invalid Subreddit or User name: {rem}")
        name: str = ""
        while len(rem) > 0 and is_allowable_character(rem[0]):
            name += rem[0]
            rem = rem[1:]
        if len(name) == 0:
            raise NoValidRedditObjectError(user_string, f"Empty name! Remaining: {rem}")

        sort_method = default_sort_method
        top_kind = default_top_kind
        user_page = default_user_page
        # Parse specifiers
        if len(rem) > 0:
            rem = parse_slashes(rem, expect=True)
            if kind is USER:
                rem, user_page = parse_userpage(rem)
                rem = parse_slashes(rem)
            if len(rem) > 0:
                rem, sort_method = parse_sortmethod(rem)
        rem = parse_slashes(rem)
        while len(rem) > 0:
            if rem[0] == '?' or rem[0] == '&':
                rem = rem[1:]
                rem, varname = parse_variable_name(rem)
                if varname == 't':
                    rem, top_kind = parse_topkind(rem)
                else:
                    while len(rem) > 0 and (rem[0].isalnum() or rem[0] == '_'):
                        rem = rem[1:]
            else:
                raise NoValidRedditObjectError(user_string, f"Must have a question mark: {rem}")
        rem = parse_slashes(rem)
        if len(rem) > 0:
            raise NoValidRedditObjectError(user_string, f"Unexpected input: \"{rem}\"")

        if kind is USER:
            return User(user_name=name.lower(), user_page_kind=user_page, sort_method=sort_method, top_kind=top_kind, https=https)
        elif kind is SUBREDDIT:
            return Subreddit(subreddit_name=name.lower(), sort_method=sort_method, top_kind=top_kind, https=https)
        else:
            raise NoValidRedditObjectError(user_string, f"Invalid Kind {kind}")

    def get_full_url(self) -> str:
        """
        Get the full URL of this Reddit Object, which might be accessed with a web browser
        :return: the full URL, e.g. "https://www.reddit.com/r/wallpapers"
        """
        if self.https:
            return f"https://{self._URLHOST}"
        else:
            return f"http://{self._URLHOST}"


class Subreddit(RedditObject):
    """
    This class represents a downloadable Subreddit.
    It shall be instantiated via a call to .from_user_string()
    """

    def __init__(self, subreddit_name: str, **kwargs):
        super().__init__(**kwargs)
        self.subreddit_name: str = subreddit_name
        """The name of this subreddit, e.g. "wallpapers" """

    @property
    def is_subreddit(self) -> bool:
        return True

    def get_full_url(self) -> str:
        ret: str = f"{super().get_full_url()}/r/{self.subreddit_name}/{self.sort_method.name.lower()}"
        if self.sort_method.has_top_kind():
            ret = f"{ret}/?t={self.top_kind.name.lower()}"
        return ret


class User(RedditObject):
    """
    This class represents a downloadable User Account.
    It shall be instantiated via a call to .from_user_string()
    """

    def __init__(self, user_name: str, user_page_kind: UserPageKind, **kwargs):
        super().__init__(**kwargs)
        self.user_page_kind: UserPageKind = user_page_kind
        self.user_name: str = user_name
        """The name of this user, e.g. "exampleuser" """

    @property
    def is_user(self) -> bool:
        return True

    def get_full_url(self) -> str:
        ret: str = f"{super().get_full_url()}/user/{self.user_name}/{self.user_page_kind.name.lower()}/{self.sort_method.name.lower()}"
        if self.sort_method.has_top_kind():
            ret = f"{ret}/?t={self.top_kind.name.lower()}"
        return ret
