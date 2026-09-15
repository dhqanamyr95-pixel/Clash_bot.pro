"""ترجمه به فارسی و ساخت متن نهایی پست (دوزبانه: انگلیسی + فارسی)"""

import html
import time

from deep_translator import GoogleTranslator

from bot_data import classify_category


def clean_raw_text(text: str) -> str:
    """رفع مشکل HTML entities مثل &#32; و امثالش"""
    if not text:
        return text
    return html.unescape(text)


def translate_to_fa(text: str) -> str:
    if not text or not text.strip():
        return text

    if len(text) > 4500:
        text = text[:4500]

    last_error = None
    for attempt in range(3):
        try:
            translator = GoogleTranslator(source="en", target="fa")
            result = translator.translate(text)
            if result and result.strip():
                return result
        except Exception as exc:
            last_error = exc
            print(f"!!! تلاش {attempt+1} ترجمه ناموفق: {exc} !!!", flush=True)
            time.sleep(2 * (attempt + 1))

    print(f"!!! ترجمه بعد از سه تلاش شکست خورد: {last_error} !!!", flush=True)
    return text


def _escape_md(text: str) -> str:
    special_chars = r"_*[]()~`>#+-=|{}.!"
    for ch in special_chars:
        text = text.replace(ch, f"\\{ch}")
    return text


def build_caption(item: dict) -> str:
    """
    caption نهایی رو می‌سازد: ابتدا متن اصلی انگلیسی، سپس ترجمه فارسی زیر آن.
    این‌طوری هم کاربران فارسی‌زبان و هم انگلیسی‌زبان می‌توانند بخوانند.
    """
    raw_title = clean_raw_text(item.get("title", ""))
    raw_body = clean_raw_text(item.get("summary", ""))

    # نکته‌ی مهم: قبلاً اینجا یک رشته (raw_title + raw_body) پاس داده می‌شد
    # که چون classify_category در bot_data.py یک دیکشنری (item) انتظار دارد،
    # باعث AttributeError: 'str' object has no attribute 'get' و کرش کل ران می‌شد.
    # الان مستقیم خود item (که از قبل title و summary را دارد) پاس داده می‌شود.
    category = classify_category(item)

    fa_title = translate_to_fa(raw_title)
    fa_body = translate_to_fa(raw_body) if raw_body else ""

    en_title = _escape_md(raw_title)
    fa_title_esc = _escape_md(fa_title)
    en_body = _escape_md(raw_body) if raw_body else ""
    fa_body_esc = _escape_md(fa_body) if fa_body else ""

    lines = [category, ""]
    lines.append(f"🇬🇧 {en_title}")
    if en_body:
        lines.append(en_body)
    lines.append("")
    lines.append(f"🇮🇷 {fa_title_esc}")
    if fa_body_esc:
        lines.append(fa_body_esc)
    lines.append("")
    lines.append("Source / منبع: Reddit r/ClashOfClans")
    lines.append("\\#کلش\\_اف\\_کلنز \\#ClashOfClans")
    lines.append("")
    lines.append("📢 Join / عضو شوید: @Clash1sk")

    return "\n".join(lines)
