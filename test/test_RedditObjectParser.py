from unittest import TestCase

from reddit import RedditObject, Subreddit, SortMethod, TopKind, User


# noinspection HttpUrlsUsage,DuplicatedCode
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

    def test_subreddits_with_default_values(self):
        params: list[tuple[str, str, str, SortMethod, TopKind]] = [
            ("r/WaLlpaperS", "https://www.reddit.com/r/wallpapers/hot", "wallpapers", next(iter(SortMethod)), next(iter(TopKind))),
            ("WALLPAPERS", "https://www.reddit.com/r/wallpapers/hot", "wallpapers", next(iter(SortMethod)), next(iter(TopKind))),
            ("r//////Wallpapers", "https://www.reddit.com/r/wallpapers/hot", "wallpapers", next(iter(SortMethod)), next(iter(TopKind))),
            ("http://reddit.com/r/wallPapers", "http://www.reddit.com/r/wallpapers/hot", "wallpapers", next(iter(SortMethod)), next(iter(TopKind))),
            ("https://www.reddit.com/r/wallPapers", "https://www.reddit.com/r/wallpapers/hot", "wallpapers", next(iter(SortMethod)),
             next(iter(TopKind))),
            ("https://www.reddit.com/r/wallpapers/controversial/?t=week", "https://www.reddit.com/r/wallpapers/controversial/?t=week", "wallpapers",
             SortMethod.CONTROVERSIAL, TopKind.WEEK),
            ("http://www.reddit.com/r/wallpapers/top/?t=all", "http://www.reddit.com/r/wallpapers/top/?t=all", "wallpapers", SortMethod.TOP,
             TopKind.ALL),
            ("http://www.reddit.com/r/Wall_Papers/top/?t=all&var=value&t=hour", "http://www.reddit.com/r/wall_papers/top/?t=hour", "wall_papers", SortMethod.TOP,
             TopKind.HOUR),
        ]
        for sr_name, ref, refname, sort_method, top_kind in params:
            with self.subTest(f"Check if a correct Subreddit user input is parsed to the correct Subreddit URL", sr_name=sr_name, ref=ref,
                              refname=refname, sort_method=sort_method, top_kind=top_kind):
                ro: RedditObject = RedditObject.from_user_string(sr_name)
                self.assertTrue(ro.is_subreddit, f"Expected a Subreddit")
                self.assertFalse(ro.is_user, f"Did not expect a User")
                sr: Subreddit = ro
                self.assertIs(sort_method, sr.sort_method, f"Expected Sort Method {sort_method}, but got {sr.sort_method}")
                self.assertEqual(refname, sr.subreddit_name, f"Subreddit Object returned wrong name \"{sr.subreddit_name}\" instead of \"{refname}\"")
                if sort_method.has_top_kind():
                    self.assertIs(top_kind, sr.top_kind, f"Expected Top Kind {top_kind}, but got {sr.top_kind}")
                self.assertEqual(ref, sr.get_full_url())

    def test_users_with_default_values(self):
        sort_method: SortMethod = next(iter(SortMethod))
        top_kind: TopKind = next(iter(TopKind))
        params: list[tuple[str, str, str]] = [
            ("https://www.reddit.com/user/my_memes_will_cure_u", "https://www.reddit.com/user/my_memes_will_cure_u/submitted/hot",
             "my_memes_will_cure_u"),
        ]
        for user_name, ref, refname in params:
            with self.subTest(f"Check if a correct User input is parsed to the correct User URL", user_name=user_name, ref=ref,
                              refname=refname):
                ro: RedditObject = RedditObject.from_user_string(user_name)
                self.assertTrue(ro.is_user, f"Expected a User")
                self.assertFalse(ro.is_subreddit, f"Did not expect a Subreddit")
                sr: User = ro
                self.assertIs(sort_method, sr.sort_method, f"Expected Sort Method {sort_method}, but got {sr.sort_method}")
                self.assertEqual(refname, sr.user_name, f"User Object returned wrong name \"{sr.user_name}\" instead of \"{refname}\"")
                # TODO page
                if sort_method.has_top_kind():
                    self.assertIs(top_kind, sr.top_kind, f"Expected Top Kind {top_kind}, but got {sr.top_kind}")
                self.assertEqual(ref, sr.get_full_url())
