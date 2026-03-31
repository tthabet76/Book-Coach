# 📖 Book Coach

A personal AI book coaching bot that delivers daily voice summaries of your books directly to Discord.

Every morning at 9 AM, you get a 4–5 minute MP3 audio note — narrated by an AI voice — that summarizes one part of your current book and connects it directly to **your life, your goals, and your challenges**.

One book per week. 5 daily parts + Saturday synthesis + Sunday retention check.

---

## What it does

| Day | Delivery |
|-----|----------|
| Mon–Fri | Deep summary of one chapter cluster — key ideas, stories, insights, and a personal reflection tied to your goals |
| Saturday | Holistic synthesis — how all 5 days connect, the book's core thesis, and your action blueprint |
| Sunday | Spaced-repetition check — 5 questions to cement what you learned |

---

## Setup (5 steps, ~15 minutes)

### 1. Clone and install

```bash
git clone https://github.com/tthabet76/book-coach.git
cd book-coach
pip install -r requirements.txt
```

### 2. Configure

```bash
cp config.template.json config.json
```

Open `config.json` and fill in:
- `gemini_api_key` — get a free key at [aistudio.google.com](https://aistudio.google.com)
- `discord_webhook` — see step 4 below
- `voice` — leave as `en-US-AriaNeural` or pick another (see voices below)

### 3. Write your personal context

```bash
cp my_context.template.md my_context.md
```

Open `my_context.md` and write 1–2 pages about yourself: your job, your current projects, your goals, what you want from books. **This is what makes the summaries personal — the more specific you are, the better.**

### 4. Create a Discord channel and webhook

1. Create a new text channel (e.g. `#book-coach`)
2. Edit Channel → Integrations → Webhooks → New Webhook → Copy URL
3. Paste the URL into `config.json` as `discord_webhook`

### 5. Add your books

**Option A — Goodreads (recommended)**

Goodreads gives you ratings, rich metadata, and hundreds of books to choose from.

1. Go to [goodreads.com](https://goodreads.com) → My Books → Import/Export → Export Library
2. Save the CSV file somewhere on your computer
3. Set `goodreads_csv` in `config.json` to the full path of the file
4. Set `goodreads_shelf` to `"read"` (your read books), `"to-read"`, or `"currently-reading"`

**Option B — Manual list**

```bash
cp my_books.template.csv my_books.csv
```

Edit `my_books.csv` and add your books (title, author, rating, pages). Simple and fast.

---

## Running the bot

```bash
# Post 3 book candidates to Discord and pick one
python book_coach.py --select
python book_coach.py --pick 2

# Deliver today's part manually
python book_coach.py

# Check status
python book_coach.py --status
```

---

## Automating at 9 AM daily

**Windows (Task Scheduler):**
- Open Task Scheduler → Create Basic Task
- Trigger: Daily at 9:00 AM
- Action: `python C:\path\to\book-coach\book_coach.py`

**Mac / Linux (cron):**
```bash
crontab -e
# Add this line:
0 9 * * * python /path/to/book-coach/book_coach.py
```

---

## Available voices

Change `voice` in `config.json` to any of these:

| Voice | Style |
|-------|-------|
| `en-US-AriaNeural` | Warm, expressive (default) |
| `en-US-AndrewNeural` | Calm, narrator |
| `en-US-GuyNeural` | Clear, professional |
| `en-GB-RyanNeural` | British, authoritative |
| `en-AU-NatashaNeural` | Australian, friendly |

Full list: `python -m edge_tts --list-voices`

---

## File structure

```
book-coach/
├── book_coach.py          ← main entry point
├── books.py               ← book list management
├── summarizer.py          ← Gemini AI summarization
├── tts.py                 ← text-to-speech (Edge TTS)
├── discord_post.py        ← Discord delivery
├── state.py               ← weekly progress tracking
├── config.json            ← your settings (gitignored)
├── my_context.md          ← your personal context (gitignored)
├── my_books.csv           ← your book list if not using Goodreads (gitignored)
├── state.json             ← runtime state (auto-created, gitignored)
└── books_done.json        ← completed books log (auto-created, gitignored)
```

---

## Privacy

`config.json`, `my_context.md`, `my_books.csv`, and all runtime files are in `.gitignore` — they will never be committed to Git.

---

## Built with

- [Google Gemini](https://aistudio.google.com) — AI summarization
- [Edge TTS](https://github.com/rany2/edge-tts) — Microsoft neural voices (free)
- [Discord Webhooks](https://discord.com/developers/docs/resources/webhook) — delivery
