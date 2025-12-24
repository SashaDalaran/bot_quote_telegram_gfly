# commands/date_timer.py

from datetime import datetime, timezone
from telegram import Update
from telegram.ext import ContextTypes

from core.timers import create_timer


async def date_timer_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Not implemented yet. Use /timer 10s message")
