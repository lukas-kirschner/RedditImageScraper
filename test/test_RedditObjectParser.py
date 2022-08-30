from unittest import TestCase

from reddit import RedditObject, Subreddit, SortMethod, TopKind


class TestRedditObjectParser(TestCase):
    def test_subreddits_simple(self):
        sr_name: str = "r/Wallpapers"
        sort_method: SortMethod = next(iter(SortMethod))
        top_kind: TopKind = next(iter(TopKind))
        ro: RedditObject = RedditObject.from_user_string(sr_name)
        self.assertTrue(ro.is_subreddit, f"Expected a Subreddit")
        sr: Subreddit = ro
        self.assertIs(sort_method, sr.sort_method, f"Expected Sort Method {sort_method}, but got {sr.sort_method}")
        if sort_method.has_top_kind():
            self.assertIs(top_kind, sr.top_kind, f"Expected Top Kind {top_kind}, but got {sr.top_kind}")
        self.assertEqual(f"https://www.reddit.com/r/wallpapers/hot", sr.get_full_url())
