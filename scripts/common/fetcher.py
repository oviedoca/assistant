"""Base fetcher with HTTP session management, retry logic, and RSS support."""

import logging
import time
from typing import Any, Dict, List, Optional

import feedparser
import requests

logger = logging.getLogger(__name__)


class BaseFetcher:
    """HTTP fetcher with automatic retries and exponential backoff."""

    SOURCE_NAME: str = ""
    CATEGORY: str = ""

    def __init__(self, source_name: str = "", category: str = ""):
        self.source_name = source_name or self.SOURCE_NAME
        self.category = category or self.CATEGORY
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            }
        )

    def get(
        self, url: str, retries: int = 3, backoff: float = 1.0, **kwargs
    ) -> requests.Response:
        """GET a URL with retry + exponential backoff."""
        for attempt in range(retries):
            try:
                resp = self.session.get(url, timeout=30, **kwargs)
                resp.raise_for_status()
                return resp
            except requests.RequestException as exc:
                logger.warning(
                    "Attempt %d/%d for %s: %s", attempt + 1, retries, url, exc
                )
                if attempt < retries - 1:
                    time.sleep(backoff * (2**attempt))
                else:
                    raise

    def fetch(self) -> Dict[str, Any]:
        """Override in subclasses to fetch and return structured data."""
        raise NotImplementedError


class RSSFetcher(BaseFetcher):
    """Fetcher for RSS / Atom feeds.

    Subclasses only need to define SOURCE_NAME, CATEGORY, and FEEDS.
    """

    FEEDS: Dict[str, str] = {}

    def fetch(self) -> Dict[str, Any]:
        articles: List[Dict[str, str]] = []
        for section, url in self.FEEDS.items():
            try:
                resp = self.get(url)
                feed = feedparser.parse(resp.text)
                for entry in feed.entries:
                    articles.append(
                        {
                            "title": entry.get("title", ""),
                            "link": entry.get("link", ""),
                            "summary": entry.get("summary", ""),
                            "published": entry.get("published", ""),
                            "section": section,
                        }
                    )
            except Exception as exc:
                logger.error("%s/%s failed: %s", self.SOURCE_NAME, section, exc)
                articles.append({"section": section, "error": str(exc)})

        ok = [a for a in articles if "error" not in a]
        return {
            "source": self.SOURCE_NAME,
            "article_count": len(ok),
            "articles": articles,
        }
