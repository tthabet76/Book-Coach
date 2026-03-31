"""Gemini-powered book summarizer — personalized via my_context.md."""

import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

CONFIG_FILE  = Path(__file__).parent / "config.json"
CONTEXT_FILE = Path(__file__).parent / "my_context.md"


def _config() -> dict:
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))


def _gemini_key() -> str:
    return _config()["gemini_api_key"]


def _read_context() -> str:
    if CONTEXT_FILE.exists():
        return CONTEXT_FILE.read_text(encoding="utf-8").strip()
    return "(No personal context provided — add your goals to my_context.md for personalized summaries.)"


def _call_gemini(prompt: str, max_tokens: int = 2000) -> str | None:
    cfg   = _config()
    key   = _gemini_key()
    model = cfg.get("gemini_model", "gemini-2.0-flash")
    url   = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={key}"
    )
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.7},
    }).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        print(f"[gemini] HTTP {e.code}: {e.read()[:200]}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[gemini] {e}", file=sys.stderr)
        return None


def generate_outline(book: dict) -> dict | None:
    """Generate a 7-part reading plan. Returns parsed JSON dict."""
    context = _read_context()
    prompt = f"""You are creating a personalized 7-part book coaching plan.

BOOK: {book['title']} by {book['author']}

READER'S PERSONAL CONTEXT:
{context}

Create a 7-part plan:
- Parts 1–5 (Monday–Friday): Each covers a distinct chapter cluster or theme
- Part 6 (Saturday): Holistic summary — how all parts connect, the book's single lesson
- Part 7 (Sunday): 5 spaced-repetition questions with answers

Return ONLY valid JSON, no markdown fences:
{{
  "title": "{book['title']}",
  "author": "{book['author']}",
  "parts": [
    {{"day": 1, "cluster_title": "...", "chapters": "...", "core_ideas": ["...", "...", "..."]}},
    {{"day": 2, "cluster_title": "...", "chapters": "...", "core_ideas": ["...", "...", "..."]}},
    {{"day": 3, "cluster_title": "...", "chapters": "...", "core_ideas": ["...", "...", "..."]}},
    {{"day": 4, "cluster_title": "...", "chapters": "...", "core_ideas": ["...", "...", "..."]}},
    {{"day": 5, "cluster_title": "...", "chapters": "...", "core_ideas": ["...", "...", "..."]}},
    {{"day": 6, "cluster_title": "Holistic Summary", "chapters": "Full book", "core_ideas": ["...", "..."]}},
    {{"day": 7, "cluster_title": "Retention Check", "chapters": "Full book", "questions": [
      {{"q": "...", "a": "..."}},
      {{"q": "...", "a": "..."}},
      {{"q": "...", "a": "..."}},
      {{"q": "...", "a": "..."}},
      {{"q": "...", "a": "..."}}
    ]}}
  ]
}}"""

    raw = _call_gemini(prompt, max_tokens=2500)
    if not raw:
        return None
    try:
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        return json.loads(clean)
    except Exception as e:
        print(f"[outline] JSON parse error: {e}\nRaw:\n{raw[:300]}", file=sys.stderr)
        return None


def generate_part(book: dict, part_num: int, outline: dict) -> str | None:
    """Generate the full narrative for a daily part (1–7)."""
    context   = _read_context()
    part_info = outline["parts"][part_num - 1]

    if part_num <= 5:
        prompt = f"""You are delivering a daily book coaching session.

BOOK: {book['title']} by {book['author']} — Day {part_num} of 5

TODAY'S CLUSTER: {part_info['cluster_title']}
CHAPTERS / SECTIONS: {part_info['chapters']}
CORE IDEAS TO COVER: {', '.join(part_info['core_ideas'])}

READER'S PERSONAL CONTEXT (use this only for the final personalization section):
{context}

CRITICAL INSTRUCTIONS:
- 80–90% of the content must be NEW information from the book: its specific arguments, stories, data, and examples.
- Use the reader's personal context ONLY in section 4 to bridge the book's ideas to their world.
- Do NOT let the personal context dominate or replace the book's actual content.

Write a rich, narrative coaching session (550–700 words) with EXACTLY these sections:

📘 {book['title']} (Day {part_num} of 5)
by {book['author']}

1️⃣ **Key Ideas: {part_info['cluster_title']}**
[2–3 paragraphs — the book's core concepts for this cluster, in rich narrative form]

2️⃣ **Examples and Stories**
[Vivid examples, anecdotes, or data points directly from the book]

3️⃣ **Philosophical / Conceptual Insights**
[The deeper meaning — what this reveals about human nature, history, systems, etc.]

4️⃣ **💼 Reflection for You**
[Connect the book's ideas to the reader's specific context and goals — be concrete, not generic]

🔚 **Summary Pulse**
[One powerful paragraph capturing the day's essence]

Write in a warm, narrative voice — like a trusted coach speaking directly to the reader."""

    elif part_num == 6:
        prompt = f"""You are delivering a Saturday holistic book summary.

BOOK: {book['title']} by {book['author']} — Saturday: The Full Picture

WEEKLY OUTLINE:
{json.dumps(outline['parts'][:5], indent=2)}

READER'S PERSONAL CONTEXT:
{context}

Write a rich holistic synthesis (600–750 words):

📘 {book['title']} — Saturday: The Full Picture
by {book['author']}

🌐 **The Book's Single Core Thesis**
[The one idea that ties everything together]

🔗 **How the 5 Parts Connect**
[Show the arc from Day 1 to Day 5 and why this sequence matters]

💡 **The 3 Transformative Insights**
[The ideas from this book that will change how you think and act]

🌍 **Where This Book Sits in the World**
[Connect it to broader ideas, other books, or historical context]

💼 **Your Personal Action Blueprint**
[3 specific, concrete actions the reader can take — tied to their context]"""

    else:  # Part 7 — Sunday retention
        questions = part_info.get("questions", [])
        q_text = "\n".join(
            f"Q{i+1}: {q['q']}\nA{i+1}: {q['a']}" for i, q in enumerate(questions)
        )
        prompt = f"""You are delivering a Sunday spaced-repetition retention check.

BOOK: {book['title']} by {book['author']} — Sunday: Retention Check

QUESTIONS AND ANSWERS:
{q_text}

Write an engaging retention session (400–500 words):

📘 {book['title']} — Sunday: Retention Check
by {book['author']}

🧠 **This Week's 5 Key Questions**
[Present each as a challenge, let the reader think, then reveal the answer with a brief explanation of WHY it matters. Make it feel like a conversation, not a quiz.]

💪 **What You Now Own**
[A brief energizing closing — what mental models the reader permanently owns from this book]"""

    return _call_gemini(prompt, max_tokens=2000)
