"""نقطه ورود اصلی ربات."""

import sys
import traceback

print("=== شروع اجرای ربات ===", flush=True)

try:
    import config
    import bot_data
    import formatter
    import sender
    print("=== ماژول‌ها با موفقیت import شدند ===", flush=True)
except Exception:
    print("!!! خطا در import ماژول‌ها !!!", flush=True)
    traceback.print_exc()
    sys.exit(1)


def run():
    if not config.BOT_TOKEN or not config.CHANNEL_ID:
        print("!!! BOT_TOKEN یا CHANNEL_ID تنظیم نشده است !!!", flush=True)
        return

    bot_data.init_db()
    print("=== دیتابیس آماده شد ===", flush=True)

    items_found = 0
    items_posted = 0
    error_msg = None

    try:
        print("=== شروع گرفتن اخبار ===", flush=True)
        raw_items = bot_data.fetch_all_items()
        items_found = len(raw_items)
        print(f"=== تعداد آیتم خام: {items_found} ===", flush=True)

        new_items = [it for it in raw_items if not bot_data.is_posted(it["id"])]
        filtered_items = [it for it in new_items if bot_data.passes_filter(it)]
        print(f"=== جدید: {len(new_items)} | بعد از فیلتر: {len(filtered_items)} ===", flush=True)

        filtered_items = list(reversed(filtered_items))[: config.MAX_POSTS_PER_RUN]

        for item in filtered_items:
            print(f"--- در حال پردازش: {item['title'][:60]} ---", flush=True)
            caption = formatter.build_caption(item)

            if sender.send_post(caption, item["image_url"], item["link"]):
                bot_data.mark_posted(item["id"], item["source"], item["title"])
                items_posted += 1
                print(f"=== پست شد: {item['title'][:60]} ===", flush=True)
            else:
                print(f"!!! پست ناموفق: {item['title'][:60]} !!!", flush=True)

    except Exception as exc:
        print("!!! خطای غیرمنتظره !!!", flush=True)
        traceback.print_exc()
        error_msg = str(exc)
        sender.notify_admin(str(exc))

    bot_data.log_run(items_found, items_posted, error_msg)
    print(f"=== پایان اجرا. پست‌شده: {items_posted} ===", flush=True)


if __name__ == "__main__":
    run()
