"""Fox News fetcher — latest, politics, world, and US via RSS."""

from scripts.common.fetcher import RSSFetcher


class FoxNewsFetcher(RSSFetcher):
    SOURCE_NAME = "foxnews"
    CATEGORY = "news"
    FEEDS = {
        "latest": "https://moxie.foxnews.com/google-publisher/latest.xml",
        "politics": "https://moxie.foxnews.com/google-publisher/politics.xml",
        "world": "https://moxie.foxnews.com/google-publisher/world.xml",
        "us": "https://moxie.foxnews.com/google-publisher/us.xml",
    }
