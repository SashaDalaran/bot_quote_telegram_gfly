# ==================================================
# commands/date_timer.py
# ==================================================

from datetime import datetime, timedelta, timezone
from telegram import Update
from telegram.ext import ContextTypes

from core.timers import create_timer
from core.formatter import format_remaining_time


async def timerdate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    if len(args) < 3:
        await update.message.reply_text(
            "❌ Usage:\n"
            "/timerdate DD.MM.YYYY HH:MM +TZ text [--pin]\n\n"
            "Example:\n"
            "/timerdate 31.12.2025 23:59 +3 Новый год 🎆 --pin"
        )
        return

    date_str, time_str, gmt = args[:3]
    text = " ".join(args[3:]) or "⏰ Time is up!"

    pin = False
    if text.endswith("--pin"):
        pin = True
        text = text[:-5].strip()

    try:
        base_dt = datetime.strptime(
            f"{date_str} {time_str}",
            "%d.%m.%Y %H:%M",
        )

        if not (gmt.startswith("+") or gmt.startswith("-")):
            raise ValueError("Timezone must be like +3 or -5")

        tz_offset = int(gmt)
        tz = timezone(timedelta(hours=tz_offset))

        target_time = base_dt.replace(tzinfo=tz).astimezone(timezone.utc)

        remaining = int((target_time - datetime.now(timezone.utc)).total_seconds())
        if remaining <= 0:
            raise ValueError("Date already passed")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")
        return

    sent = await update.message.reply_text(
        f"⏳ <b>Timer created</b>\n"
        f"📅 Date: {date_str} {time_str} (GMT{gmt})\n"
        f"⏱ Remaining: {format_remaining_time(remaining)}\n"
        f"📝 Message: {text}",
        parse_mode="HTML",
    )

    pinned_id = None
    if pin:
        try:
            await sent.pin()
            pinned_id = sent.message_id
        except Exception:
            pass

    create_timer(
        context=context,
        chat_id=update.effective_chat.id,
        target_time=target_time,
        message=text,
        pin_message_id=pinned_id,
    )
