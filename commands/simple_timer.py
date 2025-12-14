# ==================================================
# commands/simple_timer.py
# ==================================================

from datetime import datetime, timedelta, timezone
from telegram import Update
from telegram.ext import ContextTypes

from core.timers import create_timer


def parse_duration(raw: str) -> int:
    raw = raw.lower().strip()

    if raw.endswith("s"):
        return int(raw[:-1])
    if raw.endswith("m"):
        return int(raw[:-1]) * 60
    if raw.endswith("h"):
        return int(raw[:-1]) * 3600

    raise ValueError("Invalid duration format")


async def timer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /timer 10s text")
        return

    try:
        seconds = parse_duration(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid time format. Use 10s / 3m / 1h")
        return

    message = " ".join(context.args[1:]) if len(context.args) > 1 else ""

    target_time = datetime.now(timezone.utc) + timedelta(seconds=seconds)

    sent = await update.message.reply_text("⏳")

    create_timer(
        context=context,
        chat_id=sent.chat_id,
        target_time=target_time,
        message=message,
        pin_message_id=sent.message_id,
    )
