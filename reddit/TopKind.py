from enum import Enum


class TopKind(Enum):
    """This class represents a Top Kind that may be applied to a SortMethod object"""
    DAY = 0,
    """Sort by Top of the Day"""
    YEAR = 1,
    """Sort by Top of the Year"""
    MONTH = 2,
    """Sort by Top of the Month"""
    WEEK = 3,
    """Sort by Top of the Week"""
    ALL = 4,
    """Sort by Top of All Time"""
    HOUR = 5,
    """Sort by Top of the Hour"""
