# commands/simple_timer.py

from datetime import datetime, timedelta, timezone
from telegram import Update
from telegram.ext import ContextTypes

from core.timers import create_timer
from core.parser import parse_duration


async def timer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not context.args:
        await update.message.reply_text(
            "❌ Формат: /timer 30s | 5m | 1h | 1h30m"
        )
        return

    try:
        seconds = parse_duration(context.args[0])
    except ValueError as e:
        await update.message.reply_text(f"❌ {e}")
        return

    target_time = datetime.now(timezone.utc) + timedelta(seconds=seconds)

    msg = await update.message.reply_text("⏳ Таймер...")
    create_timer(
        context=context,
        chat_id=chat_id,
        target_time=target_time,
        message="",
        pin_message_id=msg.message_id,
    )
