# commands/simple_timer.py
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from telegram import Update
from telegram.ext import ContextTypes

from core.parser import parse_timer
from core.formatter import format_remaining_time
from core.timers import create_timer


async def timer_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        seconds, msg = parse_timer(context.args)
    except Exception:
        await update.effective_message.reply_text(
            "Usage: /timer <duration> [message]\n"
            "Examples: /timer 10s tea\n"
            "          /timer 5m\n"
            "          /timer 1h30m stretching\n"
            "(If you pass only digits like /timer 10 -> it's 10 minutes.)"
        )
        return

    chat_id = update.effective_chat.id

    started_text = f"⏰ Timer started: {format_remaining_time(seconds)}"
    bot_msg = await update.effective_message.reply_text(started_text)

    target = datetime.now(timezone.utc) + timedelta(seconds=seconds)

    create_timer(
        context=context,
        chat_id=chat_id,
        target_time=target,
        message_id=bot_msg.message_id,  # IMPORTANT: we edit bot's own message
        message=msg,
    )
