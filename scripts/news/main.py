"""Fetch news from all configured sources.

Usage:
    python -m scripts.news.main                     # all sources
    python -m scripts.news.main --sources cnn foxnews
    python -m scripts.news.main --date 2026-03-15
"""

import argparse
import logging
import sys

from scripts.common.storage import save_json
from scripts.news.cnn import CNNFetcher
from scripts.news.foxnews import FoxNewsFetcher
from scripts.news.yahoo_finance import YahooFinanceFetcher
from scripts.news.aljazeera import AlJazeeraFetcher

ALL_SOURCES = {
    "cnn": CNNFetcher,
    "foxnews": FoxNewsFetcher,
    "yahoo-finance": YahooFinanceFetcher,
    "aljazeera": AlJazeeraFetcher,
}

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Fetch news articles from RSS feeds")
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
        logger.info("Fetching news from %s …", name)
        try:
            fetcher = ALL_SOURCES[name]()
            data = fetcher.fetch()
            path = save_json(
                data, category="news", source=name,
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

    logger.info("Done — all sources fetched successfully.")


if __name__ == "__main__":
    main()
