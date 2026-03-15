"""Fetch LLM / AI news from all configured sources.

Usage:
    python -m scripts.llm_news.main                          # all sources
    python -m scripts.llm_news.main --sources openai arxiv
    python -m scripts.llm_news.main --date 2026-03-15
"""

import argparse
import logging
import sys

from scripts.common.storage import save_json
from scripts.llm_news.huggingface import HuggingFaceFetcher
from scripts.llm_news.openai import OpenAIFetcher
from scripts.llm_news.google_ai import GoogleAIFetcher
from scripts.llm_news.anthropic import AnthropicFetcher
from scripts.llm_news.mit_tech_review import MITTechReviewFetcher
from scripts.llm_news.arxiv import ArxivFetcher

ALL_SOURCES = {
    "huggingface": HuggingFaceFetcher,
    "openai": OpenAIFetcher,
    "google-ai": GoogleAIFetcher,
    "anthropic": AnthropicFetcher,
    "mit-tech-review": MITTechReviewFetcher,
    "arxiv": ArxivFetcher,
}

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch LLM / AI news and research"
    )
    parser.add_argument(
        "--sources",
        nargs="*",
        choices=list(ALL_SOURCES.keys()),
        default=list(ALL_SOURCES.keys()),
        help="Sources to fetch (default: all)",
    )
    parser.add_argument("--date", help="Override storage date (YYYY-MM-DD)")
    args = parser.parse_args()

    errors = []
    for name in args.sources:
        logger.info("Fetching LLM news from %s …", name)
        try:
            fetcher = ALL_SOURCES[name]()
            data = fetcher.fetch()
            path = save_json(
                data, category="llm-news", source=name,
                filename="articles.json", date=args.date,
            )
            logger.info(
                "✓ %s — %d articles → %s",
                name, data.get("article_count", 0), path,
            )
        except Exception as exc:
            logger.error("✗ %s — %s", name, exc)
            errors.append(name)

    if errors:
        logger.error("Failed sources: %s", ", ".join(errors))
        sys.exit(1)

    logger.info("Done — all LLM news sources fetched successfully.")


if __name__ == "__main__":
    main()
