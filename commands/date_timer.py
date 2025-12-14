# ==================================================
# commands/date_timer.py
# ==================================================

from datetime import datetime, timedelta, timezone
from telegram import Update
from telegram.ext import ContextTypes

from core.timers import create_timer


async def timerdate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /timerdate DD.MM.YYYY HH:MM +TZ text [--pin]
    """

    if len(context.args) < 3:
        await update.message.reply_text(
            "Usage: /timerdate 31.12.2025 23:59 +3 Text [--pin]"
        )
        return

    date_str = context.args[0]
    time_str = context.args[1]
    tz_str = context.args[2]

    pin = "--pin" in context.args
    text_parts = [a for a in context.args[3:] if a != "--pin"]
    text = " ".join(text_parts) or "⏰ Таймер"

    try:
        tz_hours = int(tz_str.replace("+", ""))
    except ValueError:
        await update.message.reply_text("Invalid timezone format. Example: +3")
        return

    local_dt = datetime.strptime(
        f"{date_str} {time_str}", "%d.%m.%Y %H:%M"
    )

    target_time = (
        local_dt.replace(tzinfo=timezone.utc)
        - timedelta(hours=tz_hours)
    )

    msg = await update.message.reply_text("⏳ Таймер создан...")

    if pin:
        await context.bot.pin_chat_message(
            chat_id=update.effective_chat.id,
            message_id=msg.message_id,
        )

    create_timer(
        context=context,
        chat_id=update.effective_chat.id,
        target_time=target_time,
        message=text,
        pin_message_id=msg.message_id,
    )
