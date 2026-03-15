# Assistant — Automated Data Fetcher

A modular data-fetching platform powered by **GitHub Actions**.  
Data is stored in `data/<source>/<date>/` and committed back to the repo automatically.

## Data Sources

### 📰 News (daily)
| Source | Method |
|--------|--------|
| CNN | RSS feeds (top stories, world, US, business) |
| Fox News | RSS feeds (latest, politics, world, US) |
| Yahoo Finance | RSS feeds (top news, market stories) |
| Al Jazeera | RSS feed (all stories) |

### 🛒 Grocery Flyers (weekly — zipcode 98034)
| Store | Method |
|-------|--------|
| Fred Meyer | HTML + embedded JSON extraction |
| Safeway | HTML + embedded JSON extraction |
| Trader Joe's | Fearless Flyer page scraping |

## Quick Start

```bash
pip install -r requirements.txt

# Fetch all news
python -m scripts.news.main

# Fetch specific news sources
python -m scripts.news.main --sources cnn aljazeera

# Fetch all grocery flyers (default zip 98034)
python -m scripts.flyers.main

# Fetch flyers for a different zipcode
python -m scripts.flyers.main --zipcode 98033
```

## GitHub Actions

| Workflow | Schedule | Trigger |
|----------|----------|---------|
| `fetch-news.yml` | Daily 08:00 UTC | `workflow_dispatch` |
| `fetch-flyers.yml` | Wednesdays 10:00 UTC | `workflow_dispatch` (zipcode input) |

## Adding a New Source

1. Create `scripts/<category>/my_source.py` with a class extending `BaseFetcher` (or `RSSFetcher` for feeds)
2. Register it in the corresponding `main.py`'s `ALL_SOURCES` dict
3. Done — the CLI and workflow will pick it up automatically

## Project Structure

```
scripts/
├── common/
│   ├── fetcher.py        # BaseFetcher (HTTP+retry) and RSSFetcher
│   └── storage.py        # save_json / save_text → data/[category]/[source]/[date]/
├── news/                 # One module per news source + main.py CLI
└── flyers/               # One module per store + main.py CLI
.github/workflows/        # Scheduled GitHub Actions
data/                     # Auto-generated, git-ignored
```
