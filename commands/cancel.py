from telegram import Update
from telegram.ext import ContextTypes

from core.timers_store import pop_last_timer


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    entry = pop_last_timer(chat_id)

    if not entry:
        await update.message.reply_text("❌ No active timers.")
        return

    for job in context.job_queue.jobs():
        if job.name == entry.job_id:
            job.schedule_removal()
            break

    await update.message.reply_text("⏹ Timer cancelled.")
