# commands/simple_timer.py

from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta

from core.timers import create_timer
from services.parser import parse_duration


async def timer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    if not args:
        await update.message.reply_text("Usage: /timer 5m message")
        return

    seconds, message = parse_duration(args)
    if seconds <= 0:
        await update.message.reply_text("Invalid time format.")
        return

    target_time = datetime.utcnow() + timedelta(seconds=seconds)

    await create_timer(
        context=context,
        chat_id=update.effective_chat.id,
        target_time=target_time,
        message=message,
        pin_message_id=update.message.message_id,
    )

    await update.message.reply_text("⏰ Timer started")
