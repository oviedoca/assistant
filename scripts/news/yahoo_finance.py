"""Yahoo Finance news fetcher — top financial news and market stories via RSS."""

from scripts.common.fetcher import RSSFetcher


class YahooFinanceFetcher(RSSFetcher):
    SOURCE_NAME = "yahoo-finance"
    CATEGORY = "news"
    FEEDS = {
        "top": "https://finance.yahoo.com/news/rssindex",
        "markets": "https://finance.yahoo.com/rss/topfinstories",
    }
