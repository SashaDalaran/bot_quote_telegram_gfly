# ==================================================
# commands/date_timer.py
# ==================================================

from __future__ import annotations

from datetime import datetime, timezone

from telegram import Update
from telegram.ext import ContextTypes

from core.timers import create_timer


DATE_FORMAT = "%d.%m.%Y"
TIME_FORMAT = "%H:%M"

USAGE = f"Usage: /timer_date {DATE_FORMAT} {TIME_FORMAT} [message]"


async def date_timer_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text(USAGE)
        return

    date_str = args[0]
    time_str = args[1]
    message = " ".join(args[2:]).strip()

    try:
        dt = datetime.strptime(f"{date_str} {time_str}", f"{DATE_FORMAT} {TIME_FORMAT}")
    except ValueError:
        await update.message.reply_text(USAGE)
        return

    # Interpret as UTC to match server behavior/logs.
    dt = dt.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    if dt <= now:
        await update.message.reply_text("That time is in the past. Give me a future time.")
        return

    initial_text = f"⏰ Timer set for {dt.strftime('%d.%m.%Y %H:%M')} UTC"
    if message:
        initial_text += f"\n{message}"

    sent = await update.message.reply_text(initial_text)

    entry = create_timer(
        context=context,
        chat_id=update.effective_chat.id,
        target_time=dt,
        message=message,
        message_id=sent.message_id,
    )
    entry.last_text = initial_text
