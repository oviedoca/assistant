"""Safeway weekly flyer fetcher.

Safeway serves weekly ads through a JS-heavy platform (J4U).
This fetcher extracts what's available from the static HTML layer.
"""

import json
import logging

from bs4 import BeautifulSoup

from scripts.common.fetcher import BaseFetcher

logger = logging.getLogger(__name__)


class SafewayFetcher(BaseFetcher):
    SOURCE_NAME = "safeway"
    CATEGORY = "flyers"
    WEEKLY_AD_URL = "https://www.safeway.com/weeklyad"
    DEALS_URL = "https://www.safeway.com/foru/coupons-deals.html"

    def __init__(self, zipcode: str = "98034"):
        super().__init__()
        self.zipcode = zipcode

    def _extract_json_ld(self, soup: BeautifulSoup) -> list:
        data = []
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                parsed = json.loads(script.string)
                if isinstance(parsed, list):
                    data.extend(parsed)
                else:
                    data.append(parsed)
            except (json.JSONDecodeError, TypeError):
                continue
        return data

    def _extract_deals(self, soup: BeautifulSoup) -> list:
        deals = []
        selectors = [
            "[class*='product-card']",
            "[class*='deal-card']",
            "[class*='coupon']",
            "[data-qa*='product']",
        ]
        for selector in selectors:
            for el in soup.select(selector):
                deal = {}
                title = el.select_one("h2, h3, [class*='itle'], [class*='ame']")
                price = el.select_one("[class*='rice']")
                desc = el.select_one("[class*='description'], p")
                if title:
                    deal["title"] = title.get_text(strip=True)
                if price:
                    deal["price"] = price.get_text(strip=True)
                if desc:
                    deal["description"] = desc.get_text(strip=True)
                if deal:
                    deals.append(deal)
        return deals

    def fetch(self):
        all_deals = []
        structured = []
        page_title = ""
        errors = []

        for label, url in [("weekly_ad", self.WEEKLY_AD_URL), ("deals", self.DEALS_URL)]:
            try:
                resp = self.get(url)
                soup = BeautifulSoup(resp.text, "html.parser")
                if not page_title and soup.title:
                    page_title = soup.title.get_text(strip=True)
                structured.extend(self._extract_json_ld(soup))
                all_deals.extend(self._extract_deals(soup))
            except Exception as exc:
                logger.error("Safeway %s fetch failed: %s", label, exc)
                errors.append({"page": label, "error": str(exc)})

        return {
            "source": self.SOURCE_NAME,
            "zipcode": self.zipcode,
            "page_title": page_title,
            "deal_count": len(all_deals),
            "deals": all_deals,
            "structured_data": structured,
            "errors": errors,
        }
