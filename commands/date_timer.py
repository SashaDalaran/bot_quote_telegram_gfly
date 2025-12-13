# ==================================================
# commands/date_timer.py — Telegram Date Timer
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
            "/timerdate DD.MM.YYYY HH:MM +TZ text --pin\n\n"
            "Example:\n"
            "/timerdate 31.12.2025 23:59 +3 New Year! --pin"
        )
        return

    date, time_str, gmt = args[:3]
    raw_text = " ".join(args[3:]) or "⏰ Time is up!"

    should_pin = False
    if raw_text.endswith("--pin"):
        should_pin = True
        raw_text = raw_text[:-5].strip()

    try:
        base_dt = datetime.strptime(
            f"{date} {time_str}", "%d.%m.%Y %H:%M"
        )

        if not (gmt.startswith("+") or gmt.startswith("-")):
            raise ValueError("GMT must be like +3 or -5")

        tz_offset = int(gmt)
        tz = timezone(timedelta(hours=tz_offset))

        target_dt = base_dt.replace(tzinfo=tz).astimezone(timezone.utc)
        now_utc = datetime.now(timezone.utc)

        remaining = int((target_dt - now_utc).total_seconds())
        if remaining <= 0:
            raise ValueError("Date already passed")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")
        return

    msg = await update.message.reply_text(
        f"⏳ **Timer created**\n"
        f"Date: `{date} {time_str} (GMT{gmt})`\n"
        f"Remaining: **{format_remaining_time(remaining)}**",
        parse_mode="Markdown",
    )

    if should_pin:
        try:
            await context.bot.pin_chat_message(
                chat_id=update.effective_chat.id,
                message_id=msg.message_id,
            )
        except Exception:
            await update.message.reply_text("⚠️ Cannot pin message.")

    await create_timer(
        context=context,
        chat_id=update.effective_chat.id,
        target_time=target_dt,
        message=raw_text,
        pin_message_id=msg.message_id,
    )
