#!/usr/bin/env python3
"""Local chat. Reads KEY_OPENAI from ../.env and reviews with the Ryan skill."""

from __future__ import annotations

import base64
import json
import re
import sqlite3
from contextlib import contextmanager
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / ".cursor" / "skills" / "ryan-review"
INDEX = Path(__file__).resolve().parent / "index.html"
MODEL_CACHE = Path(__file__).resolve().parent / ".model"
DB_PATH = Path(__file__).resolve().parent / "ryan.db"
ENV_PATH = ROOT / ".env"
HOST = "127.0.0.1"
PORT = 8787

# Newest flagship first. The key may only see a subset; we take the first hit.
PRIORITY = (
    "gpt-6-astra",
    "gpt-6.1-sol",
    "gpt-6-sol",
    "gpt-6-luna",
    "gpt-5.6-sol",
    "gpt-5.6-terra",
    "gpt-5.4",
    "gpt-5",
    "gpt-4.1",
    "gpt-4o",
)

PREAMBLE = """You are Ryan in a working conversation with someone on his team. They use you to get an experiment, a plan, or a writeup as far as it can go before they show the real Ryan. They will also just talk.

Speak in the first person, in English only, even when they write in another language. You are the person in the conversation. Do not talk about Ryan in the third person. Direct and short. Do not wrap the reply in a code fence. Do not say you are a language model, a skill, or a simulation. If they ask whether you are the real Ryan, say you are a stand-in that applies his 9 Oct and 12 Oct 2026 bar, then go back to the work.

The message mode at the end of this prompt wins over the headings above. Never print Claim I can read, Failed gates, Misread, What has to be in the doc, or Knee-jerk.

A greeting gets one or two sentences and nothing else. If they ask what to run, what you would change, or whether something is ready, answer in speech, with no headings. An attached image is the artifact: read it. Do not invent a setting they did not name. Do not ask where a result came from when the result is the experiment. Do not ask for a pasted model prompt unless this message is a retelling of a model session. Do not ask them to confirm a word they already wrote. When they ask for a daily summary or a note a colleague can read, follow the daily-summary prompt: title, why, purpose, architecture drawn only from what they described, then the findings with their context. Ask if the architecture is missing. Do not use the review headings for that note. When they ask you to generate, write, or rewrite the report and a fact you asked for is still missing, reply with What's missing and Questions only. Do not write the conclusion. When the answers are in the thread, write the title, Purpose, Architecture as the diagram only, Context as one short paragraph behind the findings, one ASCII table inside a code fence, and Conclusion in two sentences. Say each fact once. Do not assign a score they did not give. Use only facts in their text, image, or answers. Do not invent episode counts, dates, approvals, protocols, or what a name was trained on. When they answer you, continue from that answer. Do not threaten pay, firing, or status.

The expectations and examples are included below. Do not ask for those files.
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


@contextmanager
def db():
    conn = connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS meetings (
              id TEXT PRIMARY KEY,
              title TEXT NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS messages (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              meeting_id TEXT NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
              role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
              content TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS notes (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              body TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS attachments (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              message_id INTEGER NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
              mime TEXT NOT NULL,
              data BLOB NOT NULL
            );
            """
        )
        columns = {row[1] for row in conn.execute("PRAGMA table_info(messages)")}
        if "mode" not in columns:
            conn.execute("ALTER TABLE messages ADD COLUMN mode TEXT NOT NULL DEFAULT 'talk'")


def list_meetings() -> list[dict]:
    with db() as conn:
        rows = conn.execute(
            "SELECT id, title, updated_at FROM meetings ORDER BY updated_at DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def create_meeting(title: str) -> dict:
    meeting = {
        "id": str(uuid.uuid4()),
        "title": title[:72],
        "created_at": now(),
        "updated_at": now(),
    }
    with db() as conn:
        conn.execute(
            "INSERT INTO meetings (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (meeting["id"], meeting["title"], meeting["created_at"], meeting["updated_at"]),
        )
    return meeting


def rename_meeting(meeting_id: str, title: str) -> bool:
    with db() as conn:
        cur = conn.execute(
            "UPDATE meetings SET title = ? WHERE id = ?",
            (title[:72], meeting_id),
        )
    return cur.rowcount > 0


def delete_meeting(meeting_id: str) -> bool:
    with db() as conn:
        cur = conn.execute("DELETE FROM meetings WHERE id = ?", (meeting_id,))
    return cur.rowcount > 0


def meeting_messages(meeting_id: str) -> list[dict] | None:
    with db() as conn:
        found = conn.execute("SELECT id FROM meetings WHERE id = ?", (meeting_id,)).fetchone()
        if found is None:
            return None
        rows = conn.execute(
            "SELECT id, role, content, mode FROM messages WHERE meeting_id = ? ORDER BY id",
            (meeting_id,),
        ).fetchall()
        ids = [row["id"] for row in rows]
        attachments = []
        if ids:
            marks = ",".join("?" * len(ids))
            attachments = conn.execute(
                f"SELECT id, message_id, mime FROM attachments WHERE message_id IN ({marks}) ORDER BY id",
                ids,
            ).fetchall()
    grouped: dict[int, list[dict]] = {}
    for item in attachments:
        grouped.setdefault(item["message_id"], []).append({"id": item["id"], "mime": item["mime"]})
    return [
        {
            "role": row["role"],
            "content": row["content"],
            "mode": row["mode"] or "talk",
            "images": grouped.get(row["id"], []),
        }
        for row in rows
    ]


def add_message(meeting_id: str, role: str, content: str, mode: str = "talk") -> int:
    stamp = now()
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO messages (meeting_id, role, content, created_at, mode) VALUES (?, ?, ?, ?, ?)",
            (meeting_id, role, content, stamp, mode if mode == "report" else "talk"),
        )
        conn.execute("UPDATE meetings SET updated_at = ? WHERE id = ?", (stamp, meeting_id))
        return int(cur.lastrowid)


def add_images(message_id: int, images: list[tuple[str, bytes]]) -> None:
    if not images:
        return
    with db() as conn:
        conn.executemany(
            "INSERT INTO attachments (message_id, mime, data) VALUES (?, ?, ?)",
            [(message_id, mime, blob) for mime, blob in images],
        )


def attachment(attachment_id: int) -> tuple[str, bytes] | None:
    with db() as conn:
        row = conn.execute(
            "SELECT mime, data FROM attachments WHERE id = ?",
            (attachment_id,),
        ).fetchone()
    if row is None:
        return None
    return row["mime"], row["data"]


IMAGE_TYPES = {"image/png", "image/jpeg", "image/gif", "image/webp"}
MAX_IMAGE_BYTES = 4_000_000


def decode_image(item: object) -> tuple[str, bytes] | None:
    if not isinstance(item, dict):
        return None
    mime = item.get("mime")
    raw = item.get("data")
    if not isinstance(raw, str):
        return None
    if raw.startswith("data:"):
        header, _, raw = raw.partition(",")
        declared = header[5:].split(";")[0]
        if declared in IMAGE_TYPES:
            mime = declared
    if mime not in IMAGE_TYPES:
        return None
    try:
        blob = base64.b64decode(raw, validate=True)
    except Exception:
        return None
    if not blob or len(blob) > MAX_IMAGE_BYTES:
        return None
    return str(mime), blob


def history_for_model(messages: list[dict]) -> list[dict]:
    image_ids = [image["id"] for message in messages for image in message["images"]]
    blobs: dict[int, tuple[str, bytes]] = {}
    if image_ids:
        marks = ",".join("?" * len(image_ids))
        with db() as conn:
            rows = conn.execute(
                f"SELECT id, mime, data FROM attachments WHERE id IN ({marks})",
                image_ids,
            ).fetchall()
        blobs = {row["id"]: (row["mime"], row["data"]) for row in rows}
    clean = []
    for message in messages[-40:]:
        text = message["content"]
        if message["role"] == "user" and message.get("mode") == "report":
            text = "Report for a colleague.\n" + text
        if not message["images"]:
            clean.append({"role": message["role"], "content": text})
            continue
        parts: list[dict] = []
        if text:
            parts.append({"type": "text", "text": text})
        for image in message["images"]:
            mime, blob = blobs[image["id"]]
            encoded = base64.b64encode(blob).decode()
            parts.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime};base64,{encoded}"},
                }
            )
        clean.append({"role": message["role"], "content": parts})
    return clean


def list_notes() -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT id, body, created_at FROM notes ORDER BY id").fetchall()
    return [dict(row) for row in rows]


def add_note(body: str) -> dict:
    note = {"id": None, "body": body, "created_at": now()}
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO notes (body, created_at) VALUES (?, ?)",
            (note["body"], note["created_at"]),
        )
        note["id"] = cur.lastrowid
    return note


def delete_note(note_id: int) -> bool:
    with db() as conn:
        cur = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    return cur.rowcount > 0


TALK_MODE = """
This message is a conversation, not a report. Answer in speech. No Purpose, Architecture, Context, Conclusion, What this shows, What's missing, or Questions. Help them think. Stay direct. If they are marking time or saying hello, one or two sentences.
"""

REPORT_MODE = """
This message is a report for a colleague. Read the text and any table before you ask. Start with What this shows: the numbers that are earned, and the sentence they do not support. A title line such as "T1: [name]" is the title. Do not ask for it. A labeled table already says what was compared. Do not ask what the numbers mean. A best group that skips a row, or lumps arms whose intervals barely overlap, is not earned. Name the skipped row. Ask only for a field that is truly absent, usually the architecture. Do not ask for a score. If they gave none, write not scored. Do not write the finished report while a real gap is open.
"""


def prompt_with_notes(base: str, mode: str = "talk") -> str:
    notes = list_notes()
    if notes:
        lines = "\n".join(f"- {note['body']}" for note in notes)
        base += (
            "\n\nDurable context stored by the researcher. Treat it as background, not as the update under review:\n"
            + lines
        )
    base += REPORT_MODE if mode == "report" else TALK_MODE
    return base


def load_key() -> str:
    for line in ENV_PATH.read_text().splitlines():
        if line.startswith("KEY_OPENAI="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("KEY_OPENAI is missing from .env")


def system_prompt() -> str:
    chunks = [PREAMBLE]
    for name in ("SKILL.md", "expectations.md", "examples.md"):
        text = (SKILL_DIR / name).read_text()
        if text.startswith("---"):
            end = text.find("\n---", 3)
            if end != -1:
                text = text[end + 4 :].lstrip()
        chunks.append(text)
    return "\n\n".join(chunks)


def _openai(key: str, path: str, payload: dict | None = None):
    data = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request(
        "https://api.openai.com/v1" + path,
        data=data,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="GET" if payload is None else "POST",
    )
    try:
        response = urllib.request.urlopen(request, timeout=30)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        return error.code, detail
    with response:
        return response.status, response.read().decode()


def pick_model(key: str) -> str:
    cached = MODEL_CACHE.read_text().strip() if MODEL_CACHE.exists() else ""
    if cached:
        return cached
    status, detail = _openai(key, "/models")
    if status == 200:
        ids = {item["id"] for item in json.loads(detail)["data"]}
        for name in PRIORITY:
            if name in ids:
                MODEL_CACHE.write_text(name)
                return name
            snaps = sorted(item for item in ids if item.startswith(name + "-"))
            if snaps:
                MODEL_CACHE.write_text(snaps[-1])
                return snaps[-1]
    # Restricted keys often cannot list models and can still call chat.
    for name in PRIORITY:
        status, detail = _openai(
            key,
            "/chat/completions",
            {
                "model": name,
                "messages": [{"role": "user", "content": "hi"}],
                "max_completion_tokens": 1,
            },
        )
        if status == 200:
            MODEL_CACHE.write_text(name)
            return name
        if "model_not_found" in detail or "does not exist" in detail:
            continue
        if status in (400, 404) and "model" in detail.lower():
            continue
        raise SystemExit(f"{name} rejected: {status} {detail[:300]}")
    raise SystemExit("none of the candidate models are enabled for this key")


def iter_deltas(response):
    for raw in response:
        line = raw.decode("utf-8", errors="replace").strip()
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            break
        obj = json.loads(data)
        choices = obj.get("choices") or []
        if not choices:
            continue
        delta = (choices[0].get("delta") or {}).get("content") or ""
        if delta:
            yield delta


class ChatHandler(BaseHTTPRequestHandler):
    key = ""
    model = ""
    prompt = ""

    def log_message(self, fmt: str, *args) -> None:
        print(f"{self.address_string()} {fmt % args}")

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _path(self) -> str:
        return urlparse(self.path).path

    def _read_json(self) -> dict | None:
        length = int(self.headers.get("Content-Length", "0"))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return None
        return payload if isinstance(payload, dict) else None

    def do_GET(self) -> None:  # noqa: N802
        path = self._path()
        if path in ("/", "/index.html"):
            body = INDEX.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/api/meta":
            self._send(200, json.dumps({"model": self.model}).encode(), "application/json")
            return
        if path == "/api/meetings":
            self._send(200, json.dumps(list_meetings()).encode(), "application/json")
            return
        if path == "/api/notes":
            self._send(200, json.dumps(list_notes()).encode(), "application/json")
            return
        attachment_match = re.fullmatch(r"/api/attachments/(\d+)", path)
        if attachment_match:
            found = attachment(int(attachment_match.group(1)))
            if found is None:
                self._send(404, b"not found", "text/plain")
                return
            mime, blob = found
            self._send(200, blob, mime)
            return
        meeting = re.fullmatch(r"/api/meetings/([0-9a-f-]{36})", path)
        if meeting:
            messages = meeting_messages(meeting.group(1))
            if messages is None:
                self._send(404, b'{"error":"not found"}', "application/json")
                return
            self._send(200, json.dumps(messages).encode(), "application/json")
            return
        self._send(404, b"not found", "text/plain")

    def do_POST(self) -> None:  # noqa: N802
        path = self._path()
        if path == "/api/notes":
            payload = self._read_json()
            body = (payload or {}).get("body") if payload else None
            if not isinstance(body, str) or not body.strip():
                self._send(400, b'{"error":"body required"}', "application/json")
                return
            note = add_note(body.strip()[:2000])
            self._send(200, json.dumps(note).encode(), "application/json")
            return
        if path != "/api/chat":
            self._send(404, b"not found", "text/plain")
            return
        payload = self._read_json()
        if payload is None:
            self._send(400, b'{"error":"bad json"}', "application/json")
            return
        content = payload.get("content")
        if content is None:
            content = ""
        if not isinstance(content, str):
            self._send(400, b'{"error":"content required"}', "application/json")
            return
        raw_images = payload.get("images") or []
        if not isinstance(raw_images, list) or len(raw_images) > 4:
            self._send(400, b'{"error":"bad images"}', "application/json")
            return
        images = []
        for item in raw_images:
            decoded = decode_image(item)
            if decoded is None:
                self._send(400, b'{"error":"bad image"}', "application/json")
                return
            images.append(decoded)
        content = content.strip()[:20000]
        if not content and not images:
            self._send(400, b'{"error":"content required"}', "application/json")
            return
        meeting_id = payload.get("meeting_id")
        created = None
        if not meeting_id:
            line = content.splitlines()[0] if content else "Image"
            created = create_meeting(line[:72])
            meeting_id = created["id"]
        elif not re.fullmatch(r"[0-9a-f-]{36}", str(meeting_id)):
            self._send(400, b'{"error":"bad meeting"}', "application/json")
            return
        elif meeting_messages(meeting_id) is None:
            self._send(404, b'{"error":"not found"}', "application/json")
            return
        mode = payload.get("mode")
        if mode != "report":
            mode = "talk"
        message_id = add_message(meeting_id, "user", content, mode)
        add_images(message_id, images)
        history = meeting_messages(meeting_id) or []
        clean = history_for_model(history)

        outbound = {
            "model": self.model,
            "stream": True,
            "messages": [{"role": "system", "content": prompt_with_notes(self.prompt, mode)}, *clean],
        }
        request = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(outbound).encode(),
            headers={
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            response = urllib.request.urlopen(request, timeout=120)
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")[:500]
            body = json.dumps({"error": detail, "meeting_id": meeting_id}).encode()
            self._send(502, body, "application/json")
            return
        except urllib.error.URLError as error:
            body = json.dumps({"error": str(error.reason), "meeting_id": meeting_id}).encode()
            self._send(502, body, "application/json")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        parts: list[str] = []
        try:
            if created:
                opened = json.dumps({"meeting": created})
                self.wfile.write(f"data: {opened}\n\n".encode())
                self.wfile.flush()
            for delta in iter_deltas(response):
                parts.append(delta)
                chunk = "data: " + json.dumps({"d": delta}) + "\n\n"
                self.wfile.write(chunk.encode())
                self.wfile.flush()
            reply = "".join(parts).strip()
            if reply:
                add_message(meeting_id, "assistant", reply)
            self.wfile.write(b"data: {\"done\": true}\n\n")
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            reply = "".join(parts).strip()
            if reply:
                add_message(meeting_id, "assistant", reply)
            return

    def do_PATCH(self) -> None:  # noqa: N802
        match = re.fullmatch(r"/api/meetings/([0-9a-f-]{36})", self._path())
        if not match:
            self._send(404, b"not found", "text/plain")
            return
        payload = self._read_json()
        title = (payload or {}).get("title") if payload else None
        if not isinstance(title, str) or not title.strip():
            self._send(400, b'{"error":"title required"}', "application/json")
            return
        clean = title.strip()[:72]
        if not rename_meeting(match.group(1), clean):
            self._send(404, b'{"error":"not found"}', "application/json")
            return
        self._send(200, json.dumps({"id": match.group(1), "title": clean}).encode(), "application/json")

    def do_DELETE(self) -> None:  # noqa: N802
        path = self._path()
        meeting = re.fullmatch(r"/api/meetings/([0-9a-f-]{36})", path)
        if meeting:
            if not delete_meeting(meeting.group(1)):
                self._send(404, b'{"error":"not found"}', "application/json")
                return
            self._send(200, b'{"ok":true}', "application/json")
            return
        match = re.fullmatch(r"/api/notes/(\d+)", path)
        if not match:
            self._send(404, b"not found", "text/plain")
            return
        if not delete_note(int(match.group(1))):
            self._send(404, b'{"error":"not found"}', "application/json")
            return
        self._send(200, b'{"ok":true}', "application/json")


def main() -> None:
    init_db()
    key = load_key()
    ChatHandler.key = key
    ChatHandler.model = pick_model(key)
    ChatHandler.prompt = system_prompt()
    print(f"model {ChatHandler.model}", flush=True)
    print(f"http://{HOST}:{PORT}", flush=True)
    ThreadingHTTPServer((HOST, PORT), ChatHandler).serve_forever()


if __name__ == "__main__":
    main()
