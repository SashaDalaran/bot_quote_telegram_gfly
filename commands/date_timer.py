# commands/date_timer.py

from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timezone

from core.timers import create_timer


async def timerdate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /timerdate YYYY-MM-DD HH:MM message"
        )
        return

    date_part = context.args[0]
    time_part = context.args[1]
    message = " ".join(context.args[2:]) if len(context.args) > 2 else None

    try:
        target_time = datetime.strptime(
            f"{date_part} {time_part}",
            "%Y-%m-%d %H:%M",
        ).replace(tzinfo=timezone.utc)
    except ValueError:
        await update.message.reply_text(
            "Bad format. Use YYYY-MM-DD HH:MM"
        )
        return

    await create_timer(
        context=context,
        chat_id=update.effective_chat.id,
        target_time=target_time,
        message=message,
        pin_message_id=update.message.message_id,
    )

    await update.message.reply_text("📅 Date timer set")
