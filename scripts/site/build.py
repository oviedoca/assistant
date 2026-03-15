"""Build a static HTML summary site from all fetched data.

Usage:
    python -m scripts.site.build                  # output to site/
    python -m scripts.site.build --out docs/      # custom output dir
"""

import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "data"
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"

CATEGORY_META = {
    "news": {"label": "📰 News", "item_key": "articles", "order": 1},
    "llm-news": {"label": "🤖 LLM & AI", "item_key": "articles", "order": 2},
    "flyers": {"label": "🛒 Grocery Flyers", "item_key": "deals", "order": 3},
}


def load_data() -> Dict[str, Dict[str, Any]]:
    """Walk data/ and load the most recent JSON for each category/source."""
    result: Dict[str, Dict[str, List]] = {}

    if not DATA_DIR.exists():
        return result

    for category_dir in sorted(DATA_DIR.iterdir()):
        if not category_dir.is_dir():
            continue
        category = category_dir.name
        result[category] = {}

        for source_dir in sorted(category_dir.iterdir()):
            if not source_dir.is_dir():
                continue
            source = source_dir.name

            # Get the most recent date folder
            date_dirs = sorted(
                [d for d in source_dir.iterdir() if d.is_dir()], reverse=True
            )
            if not date_dirs:
                continue

            latest = date_dirs[0]
            json_files = list(latest.glob("*.json"))
            if not json_files:
                continue

            try:
                data = json.loads(json_files[0].read_text(encoding="utf-8"))
                data["_date"] = latest.name
                data["_source_dir"] = source
                result[category][source] = data
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("Skipping %s/%s: %s", category, source, exc)

    return result


def build_site(output_dir: Path):
    """Generate the static site into output_dir."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=True,
    )

    all_data = load_data()

    # Build ordered categories list for the template
    categories = []
    for cat_name, sources in all_data.items():
        meta = CATEGORY_META.get(cat_name, {"label": cat_name, "item_key": "articles", "order": 99})
        items_by_source = []
        for source_name, source_data in sorted(sources.items()):
            item_key = meta["item_key"]
            items = source_data.get(item_key, source_data.get("items", []))
            # Filter out error entries
            items = [i for i in items if "error" not in i]
            items_by_source.append({
                "name": source_name,
                "date": source_data.get("_date", ""),
                "count": len(items),
                "entries": items,
            })
        categories.append({
            "key": cat_name,
            "label": meta["label"],
            "order": meta["order"],
            "sources": items_by_source,
        })

    categories.sort(key=lambda c: c["order"])

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Render index
    template = env.get_template("index.html")
    html = template.render(categories=categories, generated_at=now)

    output_dir.mkdir(parents=True, exist_ok=True)
    index_path = output_dir / "index.html"
    index_path.write_text(html, encoding="utf-8")
    logger.info("Built %s (%d categories)", index_path, len(categories))

    # Copy static assets if any
    style_src = TEMPLATE_DIR / "style.css"
    if style_src.exists():
        (output_dir / "style.css").write_text(
            style_src.read_text(encoding="utf-8"), encoding="utf-8"
        )


def main():
    parser = argparse.ArgumentParser(description="Build summary site from fetched data")
    parser.add_argument(
        "--out", default="site", help="Output directory (default: site/)"
    )
    args = parser.parse_args()
    build_site(REPO_ROOT / args.out)


if __name__ == "__main__":
    main()
