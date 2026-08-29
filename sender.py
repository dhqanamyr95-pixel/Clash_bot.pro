"""ارسال پست به کانال تلگرام."""

import json
import requests

import config


def _inline_keyboard(link: str):
    return {"inline_keyboard": [[{"text": "🔗 Source / منبع", "url": link}]]}


def send_post(caption: str, image_url: str, source_link: str) -> bool:
    reply_markup = _inline_keyboard(source_link) if source_link else None

    if image_url:
        if _send_photo(image_url, caption, reply_markup):
            return True
        print("!!! ارسال عکس شکست خورد، تلاش با پیام متنی !!!", flush=True)

    return _send_message(caption, reply_markup)


def _send_photo(image_url, caption, reply_markup):
    payload = {"chat_id": config.CHANNEL_ID, "photo": image_url, "caption": caption, "parse_mode": "MarkdownV2"}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        resp = requests.post(f"{config.API_BASE}/sendPhoto", data=payload, timeout=config.REQUEST_TIMEOUT)
        ok = resp.status_code == 200 and resp.json().get("ok")
        if not ok:
            print(f"!!! sendPhoto خطا: {resp.text} !!!", flush=True)
        return ok
    except Exception as exc:
        print(f"!!! خطای شبکه sendPhoto: {exc} !!!", flush=True)
        return False


def _send_message(caption, reply_markup):
    payload = {"chat_id": config.CHANNEL_ID, "text": caption, "parse_mode": "MarkdownV2"}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        resp = requests.post(f"{config.API_BASE}/sendMessage", data=payload, timeout=config.REQUEST_TIMEOUT)
        ok = resp.status_code == 200 and resp.json().get("ok")
        if not ok:
            print(f"!!! sendMessage خطا: {resp.text} !!!", flush=True)
        return ok
    except Exception as exc:
        print(f"!!! خطای شبکه sendMessage: {exc} !!!", flush=True)
        return False


def notify_admin(message: str):
    if not config.ADMIN_CHAT_ID:
        return
    try:
        requests.post(
            f"{config.API_BASE}/sendMessage",
            data={"chat_id": config.ADMIN_CHAT_ID, "text": f"⚠️ Bot error:\n{message}"},
            timeout=config.REQUEST_TIMEOUT,
        )
    except Exception:
        pass
