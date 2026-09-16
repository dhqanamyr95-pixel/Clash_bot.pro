"""ترجمه به فارسی و ساخت متن نهایی پست (دوزبانه: انگلیسی + فارسی)"""

import html
import time

import requests
from deep_translator import GoogleTranslator, MyMemoryTranslator

from bot_data import classify_category

# گوگل ترنسلیت حداکثر ۵ درخواست در ثانیه اجازه می‌دهد.
# این مکث قبل از هر درخواست، باعث می‌شود از این سقف رد نشویم.
TRANSLATE_DELAY_SECONDS = 1.2


def clean_raw_text(text: str) -> str:
    """رفع مشکل HTML entities مثل &#32; و امثالش"""
    if not text:
        return text
    return html.unescape(text)


def _translate_libre(text: str) -> str:
    """لایه‌ی سوم: LibreTranslate — یه سرویس متن‌باز رایگان که پاراگراف بلند رو هم قبول می‌کنه"""
    response = requests.post(
        "https://libretranslate.de/translate",
        data={"q": text, "source": "en", "target": "fa", "format": "text"},
        timeout=15,
    )
    response.raise_for_status()
    result = response.json().get("translatedText", "")
    return result


def translate_to_fa(text: str) -> str:
    if not text or not text.strip():
        return text

    if len(text) > 4500:
        text = text[:4500]

    time.sleep(TRANSLATE_DELAY_SECONDS)

    # لایه ۱: گوگل ترنسلیت (بالاترین کیفیت، اولویت اول)
    for attempt in range(3):
        try:
            result = GoogleTranslator(source="en", target="fa").translate(text)
            if result and result.strip():
                return result
        except Exception as exc:
            print(f"!!! گوگل تلاش {attempt+1} ناموفق: {exc} !!!", flush=True)
            time.sleep(8 * (attempt + 1))

    # لایه ۲: MyMemory (fallback، ممکنه ترجمه‌ی ناقص بده برای جمله‌های غیرمعمول)
    for attempt in range(2):
        try:
            result = MyMemoryTranslator(
                source="en-GB", target="fa-IR", email="youremail@example.com"
            ).translate(text)
            if result and result.strip():
                return result
        except Exception as exc:
            print(f"!!! MyMemory تلاش {attempt+1} ناموفق: {exc} !!!", flush=True)
            time.sleep(3 * (attempt + 1))

    # لایه ۳: LibreTranslate (آخرین راه‌حل)
    for attempt in range(2):
        try:
            result = _translate_libre(text)
            if result and result.strip():
                return result
        except Exception as exc:
            print(f"!!! LibreTranslate تلاش {attempt+1} ناموفق: {exc} !!!", flush=True)
            time.sleep(3 * (attempt + 1))

    print("!!! هر سه مترجم شکست خوردند، متن انگلیسی باقی می‌ماند !!!", flush=True)
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
