"""Al Jazeera news fetcher — all stories via RSS."""

from scripts.common.fetcher import RSSFetcher


class AlJazeeraFetcher(RSSFetcher):
    SOURCE_NAME = "aljazeera"
    CATEGORY = "news"
    FEEDS = {
        "all": "https://www.aljazeera.com/xml/rss/all.xml",
    }
