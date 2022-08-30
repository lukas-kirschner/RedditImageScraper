from enum import Enum


class TopKind(Enum):
    """This class represents a Top Kind that may be applied to a SortMethod object"""
    ALL_TIME = 0,
    """Sort by Top of All Time"""
    YEAR = 1,
    """Sort by Top of the Year"""
    MONTH = 2,
    """Sort by Top of the Month"""
    WEEK = 3,
    """Sort by Top of the Week"""
    DAY = 4,
    """Sort by Top of the Day"""
