# commands/simple_timer.py

from datetime import datetime, timedelta, timezone
from telegram import Update
from telegram.ext import ContextTypes

from core.parser import parse_timer
from core.timers import create_timer


async def timer_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    try:
        seconds, message = parse_timer(context.args)
    except ValueError:
        await update.message.reply_text(
            "Usage: /timer 5m [message]\nExamples:\n/timer 10s tea\n/timer 1h work"
        )
        return

    chat_id = update.effective_chat.id

    target_time = datetime.now(timezone.utc) + timedelta(seconds=seconds)

    await create_timer(
        context=context,
        chat_id=chat_id,
        target_time=target_time,
        message=message,
    )
