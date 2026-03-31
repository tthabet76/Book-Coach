#!/usr/bin/env python3
"""
Book Coach — Daily personalized book summaries delivered to Discord as voice notes.

Setup:
    1. cp config.template.json config.json  and fill in your values
    2. cp my_context.template.md my_context.md  and write your personal context
    3. pip install -r requirements.txt

CLI:
    python book_coach.py             — deliver today's part (run via cron/Task Scheduler)
    python book_coach.py --select    — post 3 book candidates to Discord
    python book_coach.py --pick 2    — select candidate #2
    python book_coach.py --status    — show current state
    python book_coach.py --reset     — reset state (start fresh)
"""

import argparse
import sys
import tempfile
from datetime import date
from pathlib import Path

import books as bk
import discord_post as dp
import state as st
import summarizer as sm
import tts


# ── Selection flow ─────────────────────────────────────────────────────────────

def do_select():
    done_titles = [b["title"] for b in st.load_done()]
    candidates  = bk.pick_candidates(n=3, exclude_titles=done_titles)

    state = st.load_state()
    state["status"]     = "selecting"
    state["candidates"] = candidates
    st.save_state(state)

    lines = ["📚 **This week's book — your 3 candidates:**\n"]
    for i, b in enumerate(candidates, 1):
        stars = "⭐" * int(b["my_rating"]) if b.get("my_rating", "0") not in ("0", "") else ""
        lines.append(f"**{i}.** {b['title']} — *{b['author']}* {stars}")
    lines.append(
        "\nTo choose, run:\n"
        "`python book_coach.py --pick 1`  (or 2 or 3)"
    )

    dp.send_text("\n".join(lines))
    print("[select] 3 candidates posted to Discord.")


def do_pick(choice: int):
    state      = st.load_state()
    candidates = state.get("candidates", [])

    if not candidates:
        print("[pick] No candidates. Run --select first.", file=sys.stderr)
        sys.exit(1)
    if choice < 1 or choice > len(candidates):
        print(f"[pick] Choice must be 1–{len(candidates)}.", file=sys.stderr)
        sys.exit(1)

    book = candidates[choice - 1]
    print(f"[pick] Generating 7-part outline for: {book['title']} ...")

    outline = sm.generate_outline(book)
    if not outline:
        print("[pick] Gemini failed to generate outline.", file=sys.stderr)
        sys.exit(1)

    state["status"]       = "active"
    state["current_book"] = book
    state["current_part"] = 1
    state["week_start"]   = date.today().isoformat()
    state["outline"]      = outline
    st.save_state(state)

    dp.send_text(
        f"✅ **This week's book: {book['title']}** by {book['author']}\n\n"
        f"Your 7-part coaching starts tomorrow at 9 AM. 📖"
    )
    print(f"[pick] Book confirmed. Part 1 delivers tomorrow.")


# ── Daily delivery ─────────────────────────────────────────────────────────────

def do_daily():
    state = st.load_state()

    if state["status"] == "idle":
        do_select()
        return

    if state["status"] == "selecting":
        print("[daily] Waiting for book selection — run: python book_coach.py --pick N")
        return

    if state["status"] != "active":
        print(f"[daily] Unknown status: {state['status']}", file=sys.stderr)
        return

    book    = state["current_book"]
    part    = state["current_part"]
    outline = state["outline"]

    print(f"[daily] Generating Part {part}/7 — {book['title']} ...")
    text = sm.generate_part(book, part, outline)
    if not text:
        print("[daily] Gemini failed to generate content.", file=sys.stderr)
        sys.exit(1)

    print(f"[daily] Converting to audio ({tts._voice()}) ...")
    with tempfile.TemporaryDirectory() as tmpdir:
        mp3_path = Path(tmpdir) / f"part{part}.mp3"
        tts.text_to_mp3(text, mp3_path)

        safe    = "".join(c for c in book["title"] if c.isalnum() or c in " -_")[:40]
        fname   = f"{safe} - Day {part}.mp3"
        caption = f"📖 **{book['title']}** — {_day_label(part)}"

        print("[daily] Posting to Discord ...")
        ok = dp.send_audio(caption, mp3_path, fname)

    if not ok:
        print("[daily] Discord delivery failed.", file=sys.stderr)
        sys.exit(1)

    if part < 7:
        state["current_part"] = part + 1
    else:
        st.mark_done(book)
        state.update({"status": "idle", "current_book": None,
                      "current_part": 0, "outline": None, "candidates": []})
        dp.send_text(
            f"🎉 **{book['title']}** complete!\n"
            f"Run `python book_coach.py --select` to pick next week's book."
        )

    st.save_state(state)
    print(f"[daily] Part {part}/7 delivered.")


def _day_label(part: int) -> str:
    return {
        1: "Day 1 of 5 — Monday",
        2: "Day 2 of 5 — Tuesday",
        3: "Day 3 of 5 — Wednesday",
        4: "Day 4 of 5 — Thursday",
        5: "Day 5 of 5 — Friday",
        6: "Saturday: The Full Picture",
        7: "Sunday: Retention Check",
    }.get(part, f"Part {part}")


# ── Utilities ──────────────────────────────────────────────────────────────────

def do_status():
    state = st.load_state()
    done  = st.load_done()
    print(f"Status     : {state['status']}")
    if state.get("current_book"):
        b = state["current_book"]
        print(f"Book       : {b['title']} by {b['author']}")
        print(f"Part       : {state['current_part']}/7")
        print(f"Week start : {state['week_start']}")
    print(f"Books done : {len(done)}")


def do_reset():
    st.save_state({
        "status": "idle", "candidates": [],
        "current_book": None, "current_part": 0,
        "week_start": None, "outline": None,
    })
    print("[reset] State cleared.")


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Book Coach — daily Discord voice summaries")
    parser.add_argument("--select", action="store_true", help="Post 3 book candidates to Discord")
    parser.add_argument("--pick",   type=int, metavar="N", help="Select candidate N")
    parser.add_argument("--status", action="store_true", help="Show current state")
    parser.add_argument("--reset",  action="store_true", help="Reset state (start fresh)")
    args = parser.parse_args()

    if args.select:
        do_select()
    elif args.pick is not None:
        do_pick(args.pick)
    elif args.status:
        do_status()
    elif args.reset:
        do_reset()
    else:
        do_daily()


if __name__ == "__main__":
    main()
