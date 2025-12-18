# ==================================================
# commands/cancel.py
# ==================================================

from telegram import Update
from telegram.ext import ContextTypes

from core.timers import TIMERS


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    jobs = context.application.job_queue.jobs()
    timer_jobs = [job for job in jobs if job.name.startswith("timer_")]

    if not timer_jobs:
        await update.message.reply_text("❌ No timers to cancel.")
        return

    # ---------- remove jobs ----------
    for job in timer_jobs:
        job.schedule_removal()

    # ---------- unpin + cleanup ----------
    entries = TIMERS.pop(chat_id, [])
    for entry in entries:
        try:
            await context.bot.unpin_chat_message(
                chat_id=chat_id,
                message_id=entry.message_id,
            )
        except Exception:
            pass

    await update.message.reply_text(
        f"🛑 Cancelled {len(timer_jobs)} timer(s)."
    )
