"""OpenAI blog fetcher — GPT releases, capabilities, and research."""

from scripts.common.fetcher import RSSFetcher


class OpenAIFetcher(RSSFetcher):
    SOURCE_NAME = "openai"
    CATEGORY = "llm-news"
    FEEDS = {
        "blog": "https://openai.com/blog/rss.xml",
    }
