# commands/cancel.py

from telegram import Update
from telegram.ext import ContextTypes

from core.timers_store import pop_last_timer, get_timers, clear_timers


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id

    entry = pop_last_timer(chat_id)
    if not entry:
        await update.message.reply_text("No timers to cancel.")
        return

    # remove scheduled jobs with that name
    for job in context.job_queue.get_jobs_by_name(entry.job_name):
        job.schedule_removal()

    # unpin + optionally notify
    try:
        await context.bot.unpin_chat_message(chat_id=chat_id, message_id=entry.message_id)
    except Exception:
        pass

    await update.message.reply_text("✅ Last timer canceled.")


async def cancel_all_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    entries = clear_timers(chat_id)

    if not entries:
        await update.message.reply_text("No timers to cancel.")
        return

    # remove all jobs + unpin their messages
    for entry in entries:
        for job in context.job_queue.get_jobs_by_name(entry.job_name):
            job.schedule_removal()
        try:
            await context.bot.unpin_chat_message(chat_id=chat_id, message_id=entry.message_id)
        except Exception:
            pass

    await update.message.reply_text(f"✅ Canceled {len(entries)} timer(s).")
