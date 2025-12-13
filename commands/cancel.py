from telegram import Update
from telegram.ext import ContextTypes

from core.timers import cancel_all_timers
from core.admin import is_admin


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("⛔ Only admins can cancel all timers.")
        return

    removed = cancel_all_timers(
        context=context,
        chat_id=update.effective_chat.id,
    )

    if removed == 0:
        await update.message.reply_text("❌ No active timers found.")
    else:
        await update.message.reply_text(f"🗑 Canceled {removed} timer(s).")


async def cancelall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await cancel_command(update, context)
