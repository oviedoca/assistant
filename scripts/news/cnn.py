"""CNN news fetcher — top stories, world, US, and business via RSS."""

from scripts.common.fetcher import RSSFetcher


class CNNFetcher(RSSFetcher):
    SOURCE_NAME = "cnn"
    CATEGORY = "news"
    FEEDS = {
        "top_stories": "http://rss.cnn.com/rss/cnn_topstories.rss",
        "world": "http://rss.cnn.com/rss/cnn_world.rss",
        "us": "http://rss.cnn.com/rss/cnn_us.rss",
        "business": "http://rss.cnn.com/rss/money_latest.rss",
    }
