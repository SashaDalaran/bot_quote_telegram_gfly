# commands/cancel.py
from telegram import Update
from telegram.ext import ContextTypes

from core.timers_store import clear_timers


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    cleared = clear_timers(chat_id)

    if cleared:
        await update.message.reply_text("❌ Timer cancelled.")
    else:
        await update.message.reply_text("⚠️ No active timer.")


async def cancel_all_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    count = clear_timers(chat_id)

    await update.message.reply_text(
        f"🧹 Cleared {count} timer(s)." if count else "⚠️ No timers to clear."
    )
