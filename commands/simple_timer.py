# ==================================================
# commands/simple_timer.py
# ==================================================

import re
from datetime import datetime, timedelta, timezone

from telegram import Update
from telegram.ext import ContextTypes

from core.timers import create_timer


TIME_RE = re.compile(
    r"(?:(\d+)d)?\s*(?:(\d+)h)?\s*(?:(\d+)m)?\s*(?:(\d+)s)?",
    re.IGNORECASE,
)


async def timer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Использование:\n"
            "/timer 1h20m перерыв"
        )
        return

    text = " ".join(context.args)
    match = TIME_RE.match(text)

    if not match:
        await update.message.reply_text("Неверный формат времени.")
        return

    days, hours, minutes, seconds = match.groups()
    delta = timedelta(
        days=int(days or 0),
        hours=int(hours or 0),
        minutes=int(minutes or 0),
        seconds=int(seconds or 0),
    )

    if delta.total_seconds() <= 0:
        await update.message.reply_text("⛔ Время должно быть больше 0.")
        return

    label = text[match.end():].strip()
    target_time = datetime.now(timezone.utc) + delta

    # --- сообщение ---
    msg = await update.message.reply_text("⏳")

    # --- пин ---
    await context.bot.pin_chat_message(
        chat_id=update.effective_chat.id,
        message_id=msg.message_id,
    )

    # --- таймер ---
    create_timer(
        context=context,
        chat_id=update.effective_chat.id,
        target_time=target_time,
        message=label,
        pin_message_id=msg.message_id,
    )
