"""ترجمه به فارسی و ساخت متن نهایی پست (دوزبانه: انگلیسی + فارسی)."""

from deep_translator import GoogleTranslator

import config
from bot_data import classify_category

_translator = GoogleTranslator(source="en", target="fa")


def translate_to_fa(text: str) -> str:
    if not text or not text.strip():
        return text
    try:
        if len(text) > 4500:
            text = text[:4500]
        return _translator.translate(text)
    except Exception as exc:
        print(f"!!! ترجمه ناموفق: {exc} !!!", flush=True)
        return text


def _escape_md(text: str) -> str:
    special_chars = r"_*[]()~`>#+-=|{}.!"
    for ch in special_chars:
        text = text.replace(ch, f"\\{ch}")
    return text


def build_caption(item: dict) -> str:
    """
    متن نهایی پست را می‌سازد: ابتدا متن اصلی انگلیسی، سپس ترجمه فارسی زیر آن.
    این‌طوری هم کاربران فارسی‌زبان و هم انگلیسی‌زبان می‌توانند بخوانند.
    """
    category = classify_category(item)

    en_title = item["title"].strip()
    en_summary = item["summary"].strip()
    fa_title = translate_to_fa(en_title)
    fa_summary = translate_to_fa(en_summary)

    source = _escape_md(item.get("source", ""))
    footer = _escape_md(config.FOOTER_TEXT)
    hashtags = _escape_md(config.HASHTAGS_DEFAULT)

    parts = [f"*{category}*", ""]

    # بخش انگلیسی
    parts.append(f"🇬🇧 *{_escape_md(en_title)}*")
    if en_summary:
        parts.append(_escape_md(en_summary))
    parts.append("")

    # بخش فارسی
    parts.append(f"🇮🇷 *{_escape_md(fa_title)}*")
    if fa_summary:
        parts.append(_escape_md(fa_summary))

    parts += ["", f"Source / منبع: {source}", hashtags, "", footer]

    caption = "\n".join(parts)
    if len(caption) > config.MAX_TEXT_LENGTH:
        caption = caption[: config.MAX_TEXT_LENGTH - 1] + "…"
    return caption
