"""
dedupe_guard.py
ماژول جلوگیری از ارسال خبر تکراری.
"""

import re
import sqlite3
import hashlib
import time
import os

DB_PATH = os.environ.get("DEDUPE_DB_PATH", "sent_news.db")
DAYS_TO_KEEP = int(os.environ.get("DEDUPE_DAYS_TO_KEEP", "30"))

URL_RE = re.compile(r"https?://\S+|www\.\S+")
ZWNJ = "\u200c"


def normalize(text: str) -> str:
    if not text:
        return ""
    t = text.replace(ZWNJ, " ")
    t = URL_RE.sub("", t)
    t = re.sub(r"[^\w\s]", "", t, flags=re.UNICODE)
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class DuplicateGuard:
    def __init__(self, db_path: str = DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sent_news (
                hash TEXT PRIMARY KEY,
                created_at INTEGER
            )
            """
        )
        self.conn.commit()
        self._cleanup_old()

    def _cleanup_old(self):
        cutoff = int(time.time()) - DAYS_TO_KEEP * 86400
        self.conn.execute("DELETE FROM sent_news WHERE created_at < ?", (cutoff,))
        self.conn.commit()

    def is_duplicate(self, text: str) -> bool:
        norm = normalize(text)
        if not norm:
            return False
        h = _hash(norm)
        row = self.conn.execute(
            "SELECT 1 FROM sent_news WHERE hash = ?", (h,)
        ).fetchone()
        return row is not None

    def mark_sent(self, text: str):
        norm = normalize(text)
        if not norm:
            return
        h = _hash(norm)
        self.conn.execute(
            "INSERT OR IGNORE INTO sent_news (hash, created_at) VALUES (?, ?)",
            (h, int(time.time())),
        )
        self.conn.commit()

    def close(self):
        self.conn.close()
