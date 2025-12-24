# ==================================================
# commands/simple_timer.py
# ==================================================

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from telegram import Update
from telegram.ext import ContextTypes

from core.parser import parse_timer
from core.formatter import format_remaining
from core.timers import create_timer


USAGE = "Usage: /timer 10s [message]  | units: s/m/h/d"


async def timer_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    try:
        seconds, message = parse_timer(context.args)
    except Exception:
        await update.message.reply_text(USAGE)
        return

    target_time = datetime.now(timezone.utc) + timedelta(seconds=seconds)

    # Send a bot-owned message (editable) and use it as the countdown container.
    initial_text = f"⏰ Time left: {format_remaining(seconds)}"
    if message:
        initial_text += f"\n{message}"

    sent = await update.message.reply_text(initial_text)

    entry = create_timer(
        context=context,
        chat_id=update.effective_chat.id,
        target_time=target_time,
        message=message,
        message_id=sent.message_id,
    )
    # prevent a pointless first edit
    entry.last_text = initial_text
