"""Fred Meyer weekly flyer fetcher via Flipp API.

Fred Meyer (Kroger family) publishes weekly ads through Flipp.
"""

import logging

from scripts.common.fetcher import BaseFetcher
from scripts.common.flipp import FlippClient

logger = logging.getLogger(__name__)


class FredMeyerFetcher(BaseFetcher):
    SOURCE_NAME = "fred-meyer"
    CATEGORY = "flyers"
    MERCHANT = "Fred Meyer"

    def __init__(self, zipcode: str = "98034"):
        super().__init__()
        self.zipcode = zipcode

    def fetch(self):
        client = FlippClient()
        try:
            result = client.get_merchant_deals(self.zipcode, self.MERCHANT)
            return {
                "source": self.SOURCE_NAME,
                "zipcode": self.zipcode,
                "method": result.get("method"),
                "flyers": result.get("flyers", []),
                "deal_count": result.get("deal_count", 0),
                "deals": result.get("deals", []),
                "errors": [],
            }
        except Exception as exc:
            logger.error("Fred Meyer fetch failed: %s", exc)
            return {
                "source": self.SOURCE_NAME,
                "zipcode": self.zipcode,
                "deal_count": 0,
                "deals": [],
                "errors": [str(exc)],
            }
