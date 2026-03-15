"""Flipp API client — aggregated grocery flyer data.

Flipp (flipp.com) powers digital flyers for major retailers.
Their backend API returns structured JSON with flyer items and prices.

Primary endpoint:
    GET https://backflipp.wishabi.com/flipp/items/search
        ?locale=en-us&postal_code={zip}&q={merchant}

Note: This is an unofficial API used by Flipp's web frontend.
"""

import logging
from typing import Any, Dict, List, Optional

from scripts.common.fetcher import BaseFetcher

logger = logging.getLogger(__name__)

FLIPP_API = "https://backflipp.wishabi.com/flipp"


class FlippClient(BaseFetcher):
    """Client for querying Flipp's flyer aggregation backend."""

    def __init__(self):
        super().__init__(source_name="flipp", category="flyers")
        self.session.headers.update({"Accept": "application/json"})

    def search_items(
        self, postal_code: str, merchant: str
    ) -> List[Dict[str, Any]]:
        """Search flyer items for a merchant in a postal code area."""
        resp = self.get(
            f"{FLIPP_API}/items/search",
            params={"locale": "en-us", "postal_code": postal_code, "q": merchant},
        )
        data = resp.json()
        # Response may be a list directly or nested under a key
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("items", data.get("results", [data]))
        return []

    def get_flyers(self, postal_code: str) -> List[Dict[str, Any]]:
        """List all available flyers for a postal code."""
        resp = self.get(
            f"{FLIPP_API}/flyers",
            params={"locale": "en-us", "postal_code": postal_code},
        )
        data = resp.json()
        return data if isinstance(data, list) else data.get("flyers", [])

    def get_flyer_items(self, flyer_id: int) -> List[Dict[str, Any]]:
        """Get all items in a specific flyer by ID."""
        resp = self.get(
            f"{FLIPP_API}/flyer_items",
            params={"locale": "en-us", "flyer_id": flyer_id},
        )
        data = resp.json()
        return data if isinstance(data, list) else data.get("items", [])

    def get_merchant_deals(
        self, postal_code: str, merchant: str
    ) -> Dict[str, Any]:
        """Get deals for a specific merchant — tries item search first,
        then falls back to flyer listing + per-flyer items."""
        items = []
        flyer_info = []
        method_used = None

        # Method 1: Direct item search
        try:
            items = self.search_items(postal_code, merchant)
            if items:
                method_used = "items_search"
                items = [self._normalize_item(i) for i in items]
        except Exception as exc:
            logger.warning("Flipp items/search for %s failed: %s", merchant, exc)

        # Method 2: Get flyers list, filter by merchant, fetch items
        if not items:
            try:
                all_flyers = self.get_flyers(postal_code)
                merchant_lower = merchant.lower()
                matched = [
                    f for f in all_flyers
                    if merchant_lower in f.get("merchant", "").lower()
                    or merchant_lower in f.get("name", "").lower()
                ]
                for flyer in matched:
                    fid = flyer.get("id")
                    flyer_info.append({
                        "id": fid,
                        "merchant": flyer.get("merchant", ""),
                        "name": flyer.get("name", ""),
                        "valid_from": flyer.get("valid_from", ""),
                        "valid_to": flyer.get("valid_to", ""),
                    })
                    if fid:
                        try:
                            flyer_items = self.get_flyer_items(fid)
                            items.extend(
                                self._normalize_item(i) for i in flyer_items
                            )
                        except Exception as exc:
                            logger.warning(
                                "Flipp flyer_items %s failed: %s", fid, exc
                            )
                if items:
                    method_used = "flyer_listing"
            except Exception as exc:
                logger.warning("Flipp flyers list for %s failed: %s", merchant, exc)

        return {
            "method": method_used,
            "flyers": flyer_info,
            "deal_count": len(items),
            "deals": items,
        }

    @staticmethod
    def _normalize_item(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Extract a consistent set of fields from a raw Flipp item."""
        return {
            "name": raw.get("name", raw.get("title", "")),
            "description": raw.get("description", ""),
            "brand": raw.get("brand", ""),
            "price": raw.get("current_price", raw.get("price", raw.get("price_text", ""))),
            "pre_price_text": raw.get("pre_price_text", ""),
            "post_price_text": raw.get("post_price_text", ""),
            "valid_from": raw.get("valid_from", ""),
            "valid_to": raw.get("valid_to", ""),
            "image_url": raw.get("cutout_image_url", raw.get("image_url", "")),
        }
