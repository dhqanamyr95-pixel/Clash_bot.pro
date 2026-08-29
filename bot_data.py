"""دیتابیس (جلوگیری از تکرار) و گرفتن اخبار از منابع RSS."""

import os
import re
import sqlite3
from datetime import datetime
from contextlib import contextmanager

import requests
import feedparser

import config

# ---------------------------------------------------------------------------
# دیتابیس
# ---------------------------------------------------------------------------
SCHEMA = """
CREATE TABLE IF NOT EXISTS posted_items (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    title TEXT,
    posted_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS run_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ran_at TEXT NOT NULL,
    items_found INTEGER,
    items_posted INTEGER,
    error TEXT
);
"""


@contextmanager
def get_conn():
    conn = sqlite3.connect(config.DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
    with get_conn() as conn:
        conn.executescript(SCHEMA)
        conn.commit()


def is_posted(item_id: str) -> bool:
    with get_conn() as conn:
        cur = conn.execute("SELECT 1 FROM posted_items WHERE id = ?", (item_id,))
        return cur.fetchone() is not None


def mark_posted(item_id: str, source: str, title: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO posted_items (id, source, title, posted_at) VALUES (?, ?, ?, ?)",
            (item_id, source, title, datetime.utcnow().isoformat()),
        )
        conn.commit()


def log_run(items_found: int, items_posted: int, error: str = None):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO run_log (ran_at, items_found, items_posted, error) VALUES (?, ?, ?, ?)",
            (datetime.utcnow().isoformat(), items_found, items_posted, error),
        )
        conn.commit()


# ---------------------------------------------------------------------------
# گرفتن اخبار
# ---------------------------------------------------------------------------
def fetch_all_items():
    all_items = []
    for source in config.SOURCES:
        try:
            resp = requests.get(source["url"], headers=config.HEADERS, timeout=config.REQUEST_TIMEOUT)
            print(f"--- وضعیت HTTP برای '{source['name']}': {resp.status_code} ---", flush=True)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
            print(f"--- تعداد entries خام: {len(feed.entries)} ---", flush=True)

            for entry in feed.entries:
                item_id = entry.get("id") or entry.get("link")
                if not item_id:
                    continue
                title = entry.get("title", "").strip()
                raw_summary = entry.get("summary", "") or entry.get("description", "")
                summary = re.sub(r"<[^>]+>", " ", raw_summary)
                summary = re.sub(r"\s+", " ", summary).strip()[:500]
                link = entry.get("link", "")

                image_url = ""
                if hasattr(entry, "media_content") and entry.media_content:
                    image_url = entry.media_content[0].get("url", "")
                elif hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
                    image_url = entry.media_thumbnail[0].get("url", "")
                else:
                    m = re.search(r'<img[^>]+src="([^"]+)"', raw_summary)
                    if m:
                        image_url = m.group(1)

                all_items.append({
                    "id": item_id, "title": title, "summary": summary,
                    "link": link, "source": source["name"], "image_url": image_url,
                })
            print(f"=== منبع '{source['name']}': {len(feed.entries)} آیتم دریافت شد ===", flush=True)
        except Exception as exc:
            print(f"!!! خطا در گرفتن منبع '{source['name']}': {exc} !!!", flush=True)
    return all_items


def passes_filter(item: dict) -> bool:
    text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
    for blocked in config.BLOCKED_WORDS:
        if blocked.lower() in text:
            return False
    if not config.KEYWORDS:
        return True
    return any(k.lower() in text for k in config.KEYWORDS)


def classify_category(item: dict) -> str:
    text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
    if any(w in text for w in ["balance", "patch", "update"]):
        return "🛠️ Update / آپدیت"
    if any(w in text for w in ["event", "season", "sneak peek"]):
        return "🎉 Event / رویداد"
    if any(w in text for w in ["cwl", "clan war", "tournament"]):
        return "⚔️ Clan War / جنگ کلن"
    if "capital" in text:
        return "🏰 Capital / کپیتال"
    return "📰 News / خبر"
