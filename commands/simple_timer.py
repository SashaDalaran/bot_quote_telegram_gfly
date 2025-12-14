from datetime import datetime, timedelta, timezone
from telegram import Update
from telegram.ext import ContextTypes

from core.models import TimerEntry
from core.timers import create_timer


async def timer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /timer 10s text")
        return

    duration = context.args[0]
    text = " ".join(context.args[1:]) or "⏱ Таймер"

    seconds = int(duration.rstrip("s"))
    target_time = datetime.now(timezone.utc) + timedelta(seconds=seconds)

    msg = await update.message.reply_text("⏳ Таймер запущен...")

    entry = TimerEntry(
        chat_id=update.effective_chat.id,
        message=text,
        target_time=target_time,
        message_id=msg.message_id,
    )

    create_timer(context, entry)
