"""ArXiv AI papers fetcher — latest LLM and NLP research papers."""

import logging
from typing import Any, Dict

import feedparser

from scripts.common.fetcher import BaseFetcher

logger = logging.getLogger(__name__)

# ArXiv query: recent papers about large language models
ARXIV_QUERY = (
    "http://export.arxiv.org/api/query?"
    "search_query=all:large+language+model+OR+all:LLM+OR+all:GPT+OR+all:transformer"
    "&sortBy=submittedDate&sortOrder=descending&max_results=50"
)


class ArxivFetcher(BaseFetcher):
    SOURCE_NAME = "arxiv"
    CATEGORY = "llm-news"

    def fetch(self) -> Dict[str, Any]:
        articles = []
        try:
            resp = self.get(ARXIV_QUERY)
            feed = feedparser.parse(resp.text)
            for entry in feed.entries:
                authors = [a.get("name", "") for a in entry.get("authors", [])]
                articles.append({
                    "title": entry.get("title", "").replace("\n", " ").strip(),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", "").replace("\n", " ").strip()[:500],
                    "published": entry.get("published", ""),
                    "authors": authors[:5],
                    "section": "arxiv-cs.CL",
                })
        except Exception as exc:
            logger.error("ArXiv fetch failed: %s", exc)
            articles.append({"section": "arxiv", "error": str(exc)})

        ok = [a for a in articles if "error" not in a]
        return {
            "source": self.SOURCE_NAME,
            "article_count": len(ok),
            "articles": articles,
        }
