"""Trader Joe's flyer fetcher via Flipp API.

Trader Joe's doesn't publish traditional weekly flyers — they release the
"Fearless Flyer" with featured / new products.  This fetcher tries Flipp
first (Trader Joe's may or may not participate).  If Flipp has no results
it falls back to scraping the Fearless Flyer page.
"""

import json
import logging

from bs4 import BeautifulSoup

from scripts.common.fetcher import BaseFetcher
from scripts.common.flipp import FlippClient

logger = logging.getLogger(__name__)


class TraderJoesFetcher(BaseFetcher):
    SOURCE_NAME = "trader-joes"
    CATEGORY = "flyers"
    MERCHANT = "Trader Joe"
    FLYER_URL = "https://www.traderjoes.com/home/discover/fearless-flyer"

    def __init__(self, zipcode: str = "98034"):
        super().__init__()
        self.zipcode = zipcode

    def _fetch_via_flipp(self):
        """Try Flipp API for Trader Joe's deals."""
        client = FlippClient()
        result = client.get_merchant_deals(self.zipcode, self.MERCHANT)
        if result.get("deal_count", 0) > 0:
            return result
        return None

    def _fetch_fearless_flyer(self):
        """Fallback: scrape the Fearless Flyer page."""
        items = []
        resp = self.get(self.FLYER_URL)
        soup = BeautifulSoup(resp.text, "html.parser")

        for script in soup.find_all("script", type="application/ld+json"):
            try:
                parsed = json.loads(script.string)
                entries = parsed if isinstance(parsed, list) else [parsed]
                for entry in entries:
                    if entry.get("name"):
                        items.append({
                            "name": entry["name"],
                            "description": entry.get("description", ""),
                            "price": entry.get("offers", {}).get("price", ""),
                        })
            except (json.JSONDecodeError, TypeError):
                continue

        for el in soup.select("article, [class*='Article'], [class*='product']"):
            title = el.select_one("h2, h3, h4")
            if title:
                item = {"name": title.get_text(strip=True)}
                price = el.select_one("[class*='rice']")
                desc = el.select_one("p")
                if price:
                    item["price"] = price.get_text(strip=True)
                if desc:
                    item["description"] = desc.get_text(strip=True)[:300]
                items.append(item)

        # Deduplicate
        seen = set()
        unique = []
        for item in items:
            key = item.get("name", "")
            if key and key not in seen:
                seen.add(key)
                unique.append(item)
        return unique

    def fetch(self):
        errors = []

        # Try Flipp first
        try:
            flipp_result = self._fetch_via_flipp()
            if flipp_result:
                return {
                    "source": self.SOURCE_NAME,
                    "zipcode": self.zipcode,
                    "method": flipp_result.get("method"),
                    "flyers": flipp_result.get("flyers", []),
                    "deal_count": flipp_result.get("deal_count", 0),
                    "deals": flipp_result.get("deals", []),
                    "errors": [],
                }
        except Exception as exc:
            logger.warning("Trader Joe's Flipp lookup failed: %s", exc)
            errors.append(f"flipp: {exc}")

        # Fallback to Fearless Flyer scrape
        try:
            items = self._fetch_fearless_flyer()
            return {
                "source": self.SOURCE_NAME,
                "zipcode": self.zipcode,
                "method": "fearless_flyer_scrape",
                "deal_count": len(items),
                "deals": items,
                "errors": errors,
            }
        except Exception as exc:
            logger.error("Trader Joe's Fearless Flyer scrape failed: %s", exc)
            errors.append(f"scrape: {exc}")

        return {
            "source": self.SOURCE_NAME,
            "zipcode": self.zipcode,
            "deal_count": 0,
            "deals": [],
            "errors": errors,
        }
