from unittest import TestCase

from reddit import SortMethod, TopKind


class TestRedditObjectHelpers(TestCase):
    def test_default_sort_method(self):
        default_sort_method = next(iter(SortMethod))
        self.assertIs(SortMethod.HOT, default_sort_method, f"Default Sort Method should be hot!")

    def test_default_top_kind(self):
        default_top_kind = next(iter(TopKind))
        self.assertIs(TopKind.DAY, default_top_kind, f"Default Top Kind should be day!")
