"""Data storage utilities — persist fetched data to data/[category]/[source]/[date]/."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def get_data_dir(
    category: str, source: str, date: Optional[str] = None
) -> Path:
    """Return (and create) the target directory for a source's data."""
    if date is None:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    data_dir = REPO_ROOT / "data" / category / source / date
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def save_json(
    data: Any,
    category: str,
    source: str,
    filename: str = "data.json",
    date: Optional[str] = None,
) -> Path:
    """Persist *data* as pretty-printed JSON."""
    out = get_data_dir(category, source, date) / filename
    out.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    logger.info("Saved %s", out)
    return out


def save_text(
    content: str,
    category: str,
    source: str,
    filename: str,
    date: Optional[str] = None,
) -> Path:
    """Persist raw text content."""
    out = get_data_dir(category, source, date) / filename
    out.write_text(content, encoding="utf-8")
    logger.info("Saved %s", out)
    return out
