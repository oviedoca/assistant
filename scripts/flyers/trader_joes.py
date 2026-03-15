"""Trader Joe's Fearless Flyer fetcher.

Trader Joe's doesn't publish traditional weekly ad flyers.  Instead they
release the "Fearless Flyer" — a curated list of featured / new products.
This fetcher scrapes the Fearless Flyer page for current items.
"""

import json
import logging

from bs4 import BeautifulSoup

from scripts.common.fetcher import BaseFetcher

logger = logging.getLogger(__name__)


class TraderJoesFetcher(BaseFetcher):
    SOURCE_NAME = "trader-joes"
    CATEGORY = "flyers"
    FLYER_URL = "https://www.traderjoes.com/home/discover/fearless-flyer"
    PRODUCTS_URL = "https://www.traderjoes.com/home/products"

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

    def _extract_flyer_items(self, soup: BeautifulSoup) -> list:
        items = []
        # Fearless Flyer articles are typically in article or card elements
        selectors = [
            "article",
            "[class*='Article']",
            "[class*='product']",
            "[class*='Product']",
            "[class*='card']",
        ]
        for selector in selectors:
            for el in soup.select(selector):
                item = {}
                title = el.select_one("h2, h3, h4, [class*='itle']")
                price = el.select_one("[class*='rice']")
                desc = el.select_one("p, [class*='description']")
                link = el.select_one("a[href]")
                img = el.select_one("img")
                if title:
                    item["title"] = title.get_text(strip=True)
                if price:
                    item["price"] = price.get_text(strip=True)
                if desc:
                    item["description"] = desc.get_text(strip=True)[:300]
                if link:
                    href = link.get("href", "")
                    if href.startswith("/"):
                        href = f"https://www.traderjoes.com{href}"
                    item["link"] = href
                if img and img.get("alt"):
                    item["image_alt"] = img["alt"]
                if item.get("title"):
                    items.append(item)
        return items

    def fetch(self):
        items = []
        structured = []
        page_title = ""
        errors = []

        for label, url in [("flyer", self.FLYER_URL), ("products", self.PRODUCTS_URL)]:
            try:
                resp = self.get(url)
                soup = BeautifulSoup(resp.text, "html.parser")
                if not page_title and soup.title:
                    page_title = soup.title.get_text(strip=True)
                structured.extend(self._extract_json_ld(soup))
                items.extend(self._extract_flyer_items(soup))
            except Exception as exc:
                logger.error("Trader Joe's %s fetch failed: %s", label, exc)
                errors.append({"page": label, "error": str(exc)})

        # Deduplicate by title
        seen = set()
        unique_items = []
        for item in items:
            key = item.get("title", "")
            if key and key not in seen:
                seen.add(key)
                unique_items.append(item)

        return {
            "source": self.SOURCE_NAME,
            "zipcode": self.zipcode,
            "page_title": page_title,
            "item_count": len(unique_items),
            "items": unique_items,
            "structured_data": structured,
            "errors": errors,
        }
