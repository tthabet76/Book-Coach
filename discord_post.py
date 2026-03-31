"""Discord delivery — text and MP3 file attachments via webhook."""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "config.json"


def _webhook_url() -> str:
    cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    url = cfg.get("discord_webhook", "").strip()
    if not url or url == "YOUR_DISCORD_WEBHOOK_URL_HERE":
        raise ValueError("Discord webhook not configured. Set 'discord_webhook' in config.json.")
    return url


def send_text(text: str) -> bool:
    url = _webhook_url()
    for chunk in _split(text, 1990):
        body = json.dumps({"content": chunk}).encode()
        req  = urllib.request.Request(
            url, data=body,
            headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                if r.status not in (200, 204):
                    return False
        except urllib.error.HTTPError as e:
            print(f"[discord] HTTP {e.code}: {e.read()}", file=sys.stderr)
            return False
    return True


def send_audio(caption: str, mp3_path: Path, filename: str) -> bool:
    url      = _webhook_url()
    boundary = "----BookCoachBoundary" + os.urandom(8).hex()
    payload  = json.dumps({"content": caption[:1990]})

    with open(mp3_path, "rb") as f:
        file_data = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="payload_json"\r\n'
        f"Content-Type: application/json\r\n\r\n"
        f"{payload}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="files[0]"; filename="{filename}"\r\n'
        f"Content-Type: audio/mpeg\r\n\r\n"
    ).encode("utf-8") + file_data + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        url, data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent":   "Mozilla/5.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status in (200, 204)
    except urllib.error.HTTPError as e:
        print(f"[discord] HTTP {e.code}: {e.read()}", file=sys.stderr)
        return False


def _split(text: str, limit: int) -> list[str]:
    if len(text) <= limit:
        return [text]
    chunks = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break
        at = text.rfind("\n", 0, limit)
        if at == -1:
            at = limit
        chunks.append(text[:at])
        text = text[at:].lstrip("\n")
    return chunks
