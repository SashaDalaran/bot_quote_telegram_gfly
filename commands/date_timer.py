# commands/date_timer.py

from telegram import Update
from telegram.ext import ContextTypes

from services.parser import parse_datetime
from core.timers import create_timer


async def timerdate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /timerdate YYYY-MM-DD HH:MM message")
        return

    target_time, message = parse_datetime(context.args)
    if not target_time:
        await update.message.reply_text("Invalid date format.")
        return

    await create_timer(
        context=context,
        chat_id=update.effective_chat.id,
        target_time=target_time,
        message=message,
        pin_message_id=update.message.message_id,  # ✅ так и должно быть
    )

    await update.message.reply_text("⏰ Timer scheduled!")
