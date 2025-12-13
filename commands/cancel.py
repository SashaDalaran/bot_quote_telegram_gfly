# ==================================================
# commands/cancel.py — Telegram Timer Cancel
# ==================================================

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from core.timers import cancel_timer, cancel_all_timers


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usage: /cancel <ID>")
        return

    try:
        timer_id = int(context.args[0])
        success = cancel_timer(timer_id)
    except Exception:
        success = False

    if success:
        await update.message.reply_text(f"✅ Timer {timer_id} canceled.")
    else:
        await update.message.reply_text("❌ Timer not found.")


async def cancelall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = cancel_all_timers(update.effective_chat.id)
    await update.message.reply_text(f"🗑 Removed {count} timers.")


def setup(application):
    application.add_handler(CommandHandler("cancel", cancel_command))
    application.add_handler(CommandHandler("cancelall", cancelall_command))
