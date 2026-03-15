"""Anthropic blog fetcher — Claude releases, safety research, capabilities."""

from scripts.common.fetcher import RSSFetcher


class AnthropicFetcher(RSSFetcher):
    SOURCE_NAME = "anthropic"
    CATEGORY = "llm-news"
    FEEDS = {
        "blog": "https://www.anthropic.com/rss.xml",
    }
