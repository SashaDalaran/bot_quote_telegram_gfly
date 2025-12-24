# commands/cancel.py
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from core.timers import cancel_last_timer, cancel_all_timers


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    entry = cancel_last_timer(context, chat_id)

    if not entry:
        await update.effective_message.reply_text("No active timers to cancel.")
        return

    await update.effective_message.reply_text("✅ Last timer canceled.")


async def cancel_all_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    n = cancel_all_timers(context, chat_id)

    await update.effective_message.reply_text(f"✅ Canceled: {n} timer(s).")
