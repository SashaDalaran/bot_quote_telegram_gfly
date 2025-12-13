# commands/cancel.py

from telegram import Update
from telegram.ext import ContextTypes

from core.timers import cancel_all_timers


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    removed = cancel_all_timers(
        context=context,
        chat_id=update.effective_chat.id,
    )

    if removed == 0:
        await update.message.reply_text("❌ No active timers found.")
    else:
        await update.message.reply_text(f"🗑 Canceled {removed} timer(s).")


# alias
async def cancelall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await cancel_command(update, context)
