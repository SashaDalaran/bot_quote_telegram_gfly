# commands/date_timer.py
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from core.parser import parse_date_time
from core.timers import create_timer


async def timerdate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        target_utc, msg = parse_date_time(context.args)
    except Exception:
        await update.effective_message.reply_text(
            "Usage: /timerdate <date> <time> [TZ] [message]\n"
            "Examples:\n"
            "  /timerdate 2025-12-31 23:59 UTC Happy New Year\n"
            "  /timerdate 31.12.2025 23:59 GET Test"
        )
        return

    chat_id = update.effective_chat.id

    bot_msg = await update.effective_message.reply_text("⏰ Timer scheduled.")

    create_timer(
        context=context,
        chat_id=chat_id,
        target_time=target_utc,
        message_id=bot_msg.message_id,
        message=msg,
    )
