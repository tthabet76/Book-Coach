"""Text-to-speech via Edge TTS."""

import asyncio
import json
import re
import tempfile
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "config.json"


def _voice() -> str:
    try:
        cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        return cfg.get("voice", "en-US-AriaNeural")
    except Exception:
        return "en-US-AriaNeural"


def text_to_mp3(text: str, output_path: str | Path | None = None) -> Path:
    """Convert text to MP3. Returns path to the generated file."""
    import edge_tts

    if output_path is None:
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        output_path = Path(tmp.name)
        tmp.close()
    else:
        output_path = Path(output_path)

    clean = _strip_markdown(text)

    async def _run():
        communicate = edge_tts.Communicate(clean, _voice())
        await communicate.save(str(output_path))

    asyncio.run(_run())
    return output_path


def _strip_markdown(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*",     r"\1", text)
    text = re.sub(r"#{1,6}\s+",     "",    text)
    for _e in ["🧠","📘","💼","🔚","🌐","🔗","💡","🌍","💪","1️⃣","2️⃣","3️⃣","4️⃣","5️⃣"]:
        text = text.replace(_e, "")
    text = re.sub(r"\[(.+?)\]",     r"\1", text)
    return text.strip()
