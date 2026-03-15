"""MIT Technology Review AI section — broader AI/LLM coverage and analysis."""

from scripts.common.fetcher import RSSFetcher


class MITTechReviewFetcher(RSSFetcher):
    SOURCE_NAME = "mit-tech-review"
    CATEGORY = "llm-news"
    FEEDS = {
        "ai": "https://www.technologyreview.com/topic/artificial-intelligence/feed",
    }
