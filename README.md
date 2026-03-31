# 📖 Book Coach — Your Personal AI Reading Coach

## The Problem This Solves

You've read dozens (maybe hundreds) of books. But 12 months later, most of it is gone.
Generic summaries like Blinkist don't help — they're written for everyone, so they speak to no one.

What actually works is **hyper-personalized micro-learning**: short daily doses of a book's ideas,
connected directly to *your* life, *your* work, and *your* current challenges.

That's what this bot does.

---

## What It Does

Every morning at 9 AM, a **4–5 minute voice note lands in your Discord channel**.
It's narrated by a natural-sounding AI voice and covers one part of your current book —
not as a generic summary, but filtered through your personal context: your job, your goals,
your ongoing projects, your family, your challenges.

One book per week. Seven parts:

| Day | What you get |
|-----|-------------|
| Monday | Part 1 — First chapter cluster: key ideas, stories, insights + personal reflection |
| Tuesday | Part 2 — Second cluster |
| Wednesday | Part 3 — Third cluster |
| Thursday | Part 4 — Fourth cluster |
| Friday | Part 5 — Fifth cluster |
| Saturday | The Full Picture — how all 5 days connect, the book's core thesis, your action blueprint |
| Sunday | Retention Check — 5 spaced-repetition questions to cement what you learned |

---

## How Book Selection Works

The bot doesn't just pick randomly. Every new week:

1. Run `python book_coach.py --select`
2. The bot picks **3 candidates** from your book list and posts them to Discord with ratings
3. You reply by running `python book_coach.py --pick 2` (or 1 or 3)
4. The bot generates a full 7-part outline for your chosen book and confirms in Discord
5. Parts start delivering from the next morning

This keeps you in control while removing the friction of choosing from a list of hundreds.

---

## What You'll See in Discord

**Monday–Friday (Parts 1–5):**
```
📖 Thinking, Fast and Slow — Day 1 of 5 — Monday
```
▶ `Thinking Fast and Slow - Day 1.mp3`  ← tap to play, ~4–5 min

**Saturday:**
```
📖 Thinking, Fast and Slow — Saturday: The Full Picture
```
▶ MP3 — synthesis of the whole week

**Sunday:**
```
📖 Thinking, Fast and Slow — Sunday: Retention Check
```
▶ MP3 — 5 questions, Socratic style, with answers

**End of week:**
```
🎉 Thinking, Fast and Slow complete!
Run python book_coach.py --select to pick next week's book.
```

---

## The Personalization Engine (`my_context.md`)

This is the most important file in the project. Before generating any summary,
the AI reads your `my_context.md` and uses it to connect every book idea to *your* world.

**Without it:** You get a good generic summary.
**With it:** You get coaching that feels like it was written specifically for you.

Write 1–2 pages covering:
- Your job and role (what you actually do day to day)
- Your current projects and challenges
- What you're learning right now
- Your personal goals (health, family, finances, etc.)
- 3–5 books that shaped how you think (the bot uses these as reference points)

The bot follows a strict ratio: **80–90% of every summary is the book's actual content**
(its arguments, stories, data, and examples). Only the final section connects it to your context.
This ensures you always learn the book deeply, not just hear about yourself.

---

## Goodreads Integration (Recommended)

You can use a simple list of books (`my_books.csv`), but connecting your Goodreads account
adds significant value:

| Without Goodreads | With Goodreads |
|-------------------|----------------|
| Manual list you maintain | Auto-synced from your actual reading history |
| No ratings | Your personal star ratings (helps smarter selection) |
| Usually a short list | Hundreds of books with full metadata |
| Fixed shelf | Filter by read / to-read / currently-reading |

To export from Goodreads:
1. Go to goodreads.com → My Books → Import/Export → Export Library
2. Download the CSV
3. Set the path in `config.json`

---

## Prerequisites

Before you start, make sure you have:

- **Python 3.10+** — [python.org](https://python.org)
- **A Discord account and server** — any server where you can create channels
- **A Gemini API key (free)** — [aistudio.google.com](https://aistudio.google.com) → Get API Key
- **Your book list** — either a Goodreads export or a simple CSV (template included)
- **15–20 minutes** for setup

---

## Setup — Step by Step

### Step 1 — Clone the repo

```bash
git clone https://github.com/tthabet76/Book-Coach.git
cd Book-Coach
```

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `edge-tts` — Microsoft neural text-to-speech (free, no API key needed)
- `python-docx` — document reading (optional, only if you use .docx context files)

### Step 3 — Create your config file

```bash
cp config.template.json config.json
```

Open `config.json` and fill in:

```json
{
  "gemini_api_key": "your_key_here",
  "discord_webhook": "your_webhook_url_here",
  "voice": "en-US-AriaNeural",
  "goodreads_csv": "C:/path/to/your/goodreads_export.csv",
  "goodreads_shelf": "read"
}
```

> `config.json` is in `.gitignore` — it will never be pushed to GitHub. Keep your keys safe.

### Step 4 — Write your personal context

```bash
cp my_context.template.md my_context.md
```

Open `my_context.md` and replace the template with your own details.
This is the step most people skip and then wonder why summaries feel generic.
**Don't skip it.** 20 minutes here will make every summary significantly better.

### Step 5 — Add your books

**Option A — Goodreads (recommended):**
Export your library and set the path in `config.json` as shown above.

**Option B — Manual list:**
```bash
cp my_books.template.csv my_books.csv
```
Edit `my_books.csv` and add your books. Columns: `title, author, my_rating, pages`.

### Step 6 — Create a Discord channel and webhook

1. In Discord, create a new **text channel** (e.g. `#book-coach` or `#daily-reads`)
2. Click the gear icon → **Integrations** → **Webhooks** → **New Webhook**
3. Copy the webhook URL
4. Paste it into `config.json` as `discord_webhook`

### Step 7 — Test the voice (optional but recommended)

Before committing to a voice, test a few:

```bash
python -m edge_tts --voice en-US-AriaNeural --text "Your mind is a library. Let us open it together." --write-media test_aria.mp3
python -m edge_tts --voice en-US-AndrewNeural --text "Your mind is a library. Let us open it together." --write-media test_andrew.mp3
python -m edge_tts --voice en-GB-RyanNeural --text "Your mind is a library. Let us open it together." --write-media test_ryan.mp3
```

Play the MP3 files and pick the voice you like. Update `voice` in `config.json`.

**Available voices:**

| Voice | Character |
|-------|-----------|
| `en-US-AriaNeural` | Warm, expressive — good for storytelling (default) |
| `en-US-AndrewNeural` | Calm, narrator tone |
| `en-US-GuyNeural` | Clear, professional |
| `en-GB-RyanNeural` | British, authoritative |
| `en-AU-NatashaNeural` | Australian, friendly |

Full list: `python -m edge_tts --list-voices`

### Step 8 — Run your first selection

```bash
python book_coach.py --select
```

Check Discord. You'll see 3 book candidates. Pick one:

```bash
python book_coach.py --pick 2
```

The bot will generate a 7-part outline (takes ~10 seconds) and confirm in Discord.

### Step 9 — Test one delivery manually

```bash
python book_coach.py
```

Check Discord for the audio file. If it arrives and sounds right, you're ready to automate.

### Step 10 — Automate at 9 AM daily

**Windows (Task Scheduler):**
1. Open Task Scheduler → Create Basic Task
2. Name: `Book Coach`
3. Trigger: Daily, at 9:00 AM
4. Action: Start a program → `python`
5. Arguments: `C:\path\to\Book-Coach\book_coach.py`
6. Start in: `C:\path\to\Book-Coach\`

**Mac / Linux (cron):**
```bash
crontab -e
# Add:
0 9 * * * cd /path/to/Book-Coach && python book_coach.py
```

---

## CLI Reference

```bash
python book_coach.py              # Deliver today's part (called by cron)
python book_coach.py --select     # Post 3 book candidates to Discord
python book_coach.py --pick 2     # Select candidate #2 and generate outline
python book_coach.py --status     # Show current book, part, and books completed
python book_coach.py --reset      # Clear state and start fresh
```

---

## Accelerating (Reading More Than One Book Per Week)

If you want to go faster — for example, finish 2 books before a specific date — simply
run the bot more than once per day:

```bash
python book_coach.py   # delivers Part 3
python book_coach.py   # delivers Part 4
```

Each run advances to the next part. Normal rhythm is once a day. Sprint mode is
however many times you want. The content quality is identical — only the pace changes.

---

## File Structure

```
Book-Coach/
├── book_coach.py           ← main entry point (run this)
├── books.py                ← loads your book list
├── summarizer.py           ← Gemini AI — generates outlines and daily summaries
├── tts.py                  ← converts text to MP3 (Edge TTS)
├── discord_post.py         ← sends text and audio to Discord
├── state.py                ← tracks current book, part, week
│
├── config.template.json    ← copy to config.json and fill in
├── my_context.template.md  ← copy to my_context.md and write your context
├── my_books.template.csv   ← copy to my_books.csv if not using Goodreads
├── requirements.txt        ← pip dependencies
├── .gitignore              ← keeps your personal files out of Git
│
├── config.json             ← YOUR settings (gitignored — never committed)
├── my_context.md           ← YOUR personal context (gitignored)
├── my_books.csv            ← YOUR book list (gitignored, if not using Goodreads)
├── state.json              ← runtime state — auto-created, gitignored
└── books_done.json         ← completed books log — auto-created, gitignored
```

---

## Troubleshooting

**"No book list found"**
→ Either set `goodreads_csv` in `config.json`, or copy `my_books.template.csv` to `my_books.csv`

**"Discord webhook not configured"**
→ Set `discord_webhook` in `config.json` with a valid Discord webhook URL

**"Gemini failed to generate outline"**
→ Check your `gemini_api_key` in `config.json`. Test it at [aistudio.google.com](https://aistudio.google.com)

**Audio file sounds robotic**
→ Make sure you're using a `Neural` voice (e.g. `en-US-AriaNeural`), not a legacy voice

**Summaries feel too generic**
→ Your `my_context.md` needs more detail. Be specific about your current projects,
challenges, and goals — vague context produces vague personalization

---

## Privacy

The following files are in `.gitignore` and will **never** be committed to GitHub:
- `config.json` (contains your API keys)
- `my_context.md` (contains personal information)
- `my_books.csv` (your book list)
- `state.json` and `books_done.json` (runtime data)

---

## Built with

- [Google Gemini](https://aistudio.google.com) — AI summarization and personalization
- [Edge TTS](https://github.com/rany2/edge-tts) — Microsoft neural voices (completely free)
- [Discord Webhooks](https://discord.com/developers/docs/resources/webhook) — delivery channel
