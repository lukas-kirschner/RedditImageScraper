from enum import Enum


class SortMethod(Enum):
    """This class represents a Sort Method that might be applied to a RedditObject"""
    HOT = 0,
    """Sort by Hot"""
    NEW = 1,
    """Sort by New"""
    CONTROVERSIAL = 2,
    """Sort by Controversial"""
    TOP = 3,
    """Sort by Top"""
    BEST = 4,
    """Sort by Best"""
    RISING = 5,
    """Sort by Rising"""

    def has_top_kind(self) -> bool:
        match self:
            case SortMethod.HOT:
                return False
            case SortMethod.NEW:
                return False
            case SortMethod.CONTROVERSIAL:
                return True
            case SortMethod.TOP:
                return True
            case SortMethod.BEST:
                return False
            case SortMethod.RISING:
                return False
            case _:
                raise NotImplementedError(f"has_top_kind() not implemented for {self}")
