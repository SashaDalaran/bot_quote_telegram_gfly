# commands/simple_timer.py

from datetime import datetime, timedelta, timezone
from telegram import Update
from telegram.ext import ContextTypes

from core.parser import parse_duration
from core.timers import create_timer


async def timer_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    msg = update.effective_message
    if msg is None:
        return

    args = context.args
    if not args:
        await msg.reply_text("Usage: /timer <time> [message] [--pin]")
        return

    chat_id = update.effective_chat.id
    now = datetime.now(timezone.utc)

    try:
        duration = parse_duration(args[0])
    except ValueError:
        await msg.reply_text("❌ Invalid time format.")
        return

    target_time = now + timedelta(seconds=duration)

    message_parts = [a for a in args[1:] if not a.startswith("--")]
    message = " ".join(message_parts) if message_parts else None

    should_pin = "--pin" in args

    create_timer(
        context=context,
        chat_id=chat_id,
        target_time=target_time,
        text=message,
        pin=should_pin,
    )

    await msg.reply_text("⏳ Timer started.")
