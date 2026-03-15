"""Google DeepMind / AI blog fetcher — Gemini, research, and breakthroughs."""

from scripts.common.fetcher import RSSFetcher


class GoogleAIFetcher(RSSFetcher):
    SOURCE_NAME = "google-ai"
    CATEGORY = "llm-news"
    FEEDS = {
        "blog": "https://blog.google/technology/ai/rss/",
        "deepmind": "https://deepmind.google/blog/rss.xml",
    }
