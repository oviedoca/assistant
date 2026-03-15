"""Hugging Face blog/papers fetcher — latest LLM research and releases."""

from scripts.common.fetcher import RSSFetcher


class HuggingFaceFetcher(RSSFetcher):
    SOURCE_NAME = "huggingface"
    CATEGORY = "llm-news"
    FEEDS = {
        "blog": "https://huggingface.co/blog/feed.xml",
        "papers": "https://huggingface.co/papers/rss",
    }
