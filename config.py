"""تنظیمات مرکزی ربات."""

import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "")

SOURCES = [
    {"name": "Reddit r/ClashOfClans", "url": "https://www.reddit.com/r/ClashOfClans/.rss"},
]

KEYWORDS = [
    "update", "event", "balance", "season", "cwl", "clan war",
    "troop", "hero", "equipment", "town hall", "builder base",
    "sneak peek", "patch", "maintenance", "tournament", "capital",
]
BLOCKED_WORDS = ["looking for clan", "lfc", "giveaway scam", "nsfw"]

MAX_POSTS_PER_RUN = 5
MAX_TEXT_LENGTH = 1024
REQUEST_TIMEOUT = 15
FOOTER_TEXT = "📢 Join / عضو شوید: @Clash1sk"
HASHTAGS_DEFAULT = "#کلش_اف_کلنز #ClashOfClans"
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "bot.db")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"
