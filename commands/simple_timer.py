ё# commands/simple_timer.py

from datetime import datetime, timedelta, timezone
from telegram import Update
from telegram.ext import ContextTypes

from core.timers import create_timer


async def timer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    seconds = int(context.args[0])
    target = datetime.now(timezone.utc) + timedelta(seconds=seconds)

    msg = await update.message.reply_text("⏳ Таймер...")
    create_timer(context, chat_id, target, "", msg.message_id)
