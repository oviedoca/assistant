"""Fetch grocery flyers / deals from all configured stores.

Usage:
    python -m scripts.flyers.main                        # all stores, zip 98034
    python -m scripts.flyers.main --zipcode 98033
    python -m scripts.flyers.main --sources safeway trader-joes
"""

import argparse
import logging
import os
import sys

from scripts.common.storage import save_json
from scripts.flyers.fred_meyer import FredMeyerFetcher
from scripts.flyers.safeway import SafewayFetcher
from scripts.flyers.trader_joes import TraderJoesFetcher

ALL_SOURCES = {
    "fred-meyer": FredMeyerFetcher,
    "safeway": SafewayFetcher,
    "trader-joes": TraderJoesFetcher,
}

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

DEFAULT_ZIPCODE = "98034"


def main():
    parser = argparse.ArgumentParser(description="Fetch grocery store flyers / deals")
    parser.add_argument(
        "--sources",
        nargs="*",
        choices=list(ALL_SOURCES.keys()),
        default=list(ALL_SOURCES.keys()),
        help="Stores to fetch (default: all)",
    )
    parser.add_argument(
        "--zipcode",
        default=os.environ.get("FLYER_ZIPCODE", DEFAULT_ZIPCODE),
        help=f"Zipcode for store location (default: {DEFAULT_ZIPCODE})",
    )
    parser.add_argument("--date", help="Override storage date (YYYY-MM-DD)")
    args = parser.parse_args()

    errors = []
    for name in args.sources:
        logger.info("Fetching flyer from %s (zip %s) …", name, args.zipcode)
        try:
            fetcher = ALL_SOURCES[name](zipcode=args.zipcode)
            data = fetcher.fetch()
            count = data.get("deal_count", data.get("item_count", 0))
            path = save_json(
                data, category="flyers", source=name,
                filename="flyer.json", date=args.date,
            )
            logger.info("✓ %s — %d items → %s", name, count, path)
        except Exception as exc:
            logger.error("✗ %s — %s", name, exc)
            errors.append(name)

    if errors:
        logger.error("Failed sources: %s", ", ".join(errors))
        sys.exit(1)

    logger.info("Done — all flyers fetched successfully.")


if __name__ == "__main__":
    main()
