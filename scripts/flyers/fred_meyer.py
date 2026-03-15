"""Fred Meyer weekly flyer fetcher.

Fred Meyer (Kroger family) serves weekly ads through a JS-heavy SPA.
This fetcher extracts available deal info from HTML and embedded structured data.
For full extraction, consider adding Playwright/Selenium.
"""

import json
import logging

from bs4 import BeautifulSoup

from scripts.common.fetcher import BaseFetcher

logger = logging.getLogger(__name__)


class FredMeyerFetcher(BaseFetcher):
    SOURCE_NAME = "fred-meyer"
    CATEGORY = "flyers"
    WEEKLY_AD_URL = "https://www.fredmeyer.com/savings/cl/weeklyad/"

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
            "[data-testid*='product']",
            "[class*='ProductCard']",
            "[class*='deal']",
            ".kds-Card",
        ]
        for selector in selectors:
            for el in soup.select(selector):
                deal = {}
                title = el.select_one("h2, h3, [class*='itle'], [class*='ame']")
                price = el.select_one("[class*='rice']")
                img = el.select_one("img")
                if title:
                    deal["title"] = title.get_text(strip=True)
                if price:
                    deal["price"] = price.get_text(strip=True)
                if img and img.get("alt"):
                    deal["description"] = img["alt"]
                if deal:
                    deals.append(deal)
        return deals

    def _extract_next_data(self, soup: BeautifulSoup) -> dict:
        script = soup.find("script", id="__NEXT_DATA__")
        if script and script.string:
            try:
                return json.loads(script.string)
            except (json.JSONDecodeError, TypeError):
                pass
        return {}

    def fetch(self):
        deals = []
        structured = []
        next_data = {}
        page_title = ""
        errors = []

        try:
            resp = self.get(self.WEEKLY_AD_URL)
            soup = BeautifulSoup(resp.text, "html.parser")
            page_title = soup.title.get_text(strip=True) if soup.title else ""
            structured = self._extract_json_ld(soup)
            deals = self._extract_deals(soup)
            next_data = self._extract_next_data(soup)
        except Exception as exc:
            logger.error("Fred Meyer fetch failed: %s", exc)
            errors.append(str(exc))

        return {
            "source": self.SOURCE_NAME,
            "zipcode": self.zipcode,
            "page_title": page_title,
            "deal_count": len(deals),
            "deals": deals,
            "structured_data": structured,
            "has_next_data": bool(next_data),
            "errors": errors,
        }
