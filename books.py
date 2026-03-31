"""Book list management — Goodreads CSV (recommended) or manual my_books.csv."""

import csv
import json
import random
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "config.json"


def _config() -> dict:
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))


def load_books() -> list[dict]:
    """
    Load books from Goodreads CSV (if configured) or my_books.csv fallback.

    Goodreads adds value because it:
    - Includes your personal star ratings (1–5) for smarter selection
    - Has 100s of books with rich metadata
    - Lets you filter by shelf (read / to-read / currently-reading)
    """
    cfg = _config()
    goodreads_path = cfg.get("goodreads_csv", "").strip()

    if goodreads_path and Path(goodreads_path).exists():
        return _load_goodreads(goodreads_path, cfg.get("goodreads_shelf", "read"))

    # Fallback: my_books.csv
    fallback = Path(__file__).parent / "my_books.csv"
    if fallback.exists():
        return _load_simple_csv(fallback)

    raise FileNotFoundError(
        "No book list found. Either:\n"
        "  1. Set 'goodreads_csv' in config.json (recommended), or\n"
        "  2. Copy my_books.template.csv to my_books.csv and add your books."
    )


def _load_goodreads(path: str, shelf: str) -> list[dict]:
    books = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("Exclusive Shelf", "").strip() == shelf:
                books.append({
                    "title":  row["Title"].strip(),
                    "author": row["Author"].strip(),
                    "my_rating": row.get("My Rating", "0").strip(),
                    "pages":  row.get("Number of Pages", "?").strip(),
                })
    return books


def _load_simple_csv(path: Path) -> list[dict]:
    books = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            books.append({
                "title":     row.get("title", "").strip(),
                "author":    row.get("author", "").strip(),
                "my_rating": row.get("my_rating", "0").strip(),
                "pages":     row.get("pages", "?").strip(),
            })
    return [b for b in books if b["title"]]


def pick_candidates(n: int = 3, exclude_titles: list[str] | None = None) -> list[dict]:
    """Pick n random books, excluding already-completed ones."""
    exclude = set(t.lower() for t in (exclude_titles or []))
    pool = [b for b in load_books() if b["title"].lower() not in exclude]
    if len(pool) < n:
        n = len(pool)
    return random.sample(pool, n)
