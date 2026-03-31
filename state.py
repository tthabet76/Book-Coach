"""State management — tracks current book, part, and week."""

import json
from pathlib import Path

STATE_FILE = Path(__file__).parent / "state.json"
DONE_FILE  = Path(__file__).parent / "books_done.json"


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "status": "idle",       # idle | selecting | active
        "candidates": [],
        "current_book": None,   # {title, author, my_rating, pages}
        "current_part": 0,      # 1–7
        "week_start": None,
        "outline": None,        # 7-part plan from Gemini
    }


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def load_done() -> list:
    if DONE_FILE.exists():
        try:
            return json.loads(DONE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def mark_done(book: dict):
    from datetime import date
    done = load_done()
    done.append({**book, "completed_date": date.today().isoformat()})
    DONE_FILE.write_text(json.dumps(done, indent=2, ensure_ascii=False), encoding="utf-8")
