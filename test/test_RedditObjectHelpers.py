from unittest import TestCase

from reddit import SortMethod


class TestRedditObjectHelpers(TestCase):
    def test_default_sort_method(self):
        default_sort_method = next(iter(SortMethod))
        self.assertIs(SortMethod.HOT, default_sort_method, f"Default Sort Method should be hot!")
