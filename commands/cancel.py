# commands/cancel.py

from telegram import Update
from telegram.ext import ContextTypes

from core.timers_store import (
    pop_last_timer,
    get_timers,
    clear_timers,
)


# ---------- cancel LAST timer ----------
async def cancel_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    chat_id = update.effective_chat.id

    entry = pop_last_timer(chat_id)
    if not entry:
        await update.message.reply_text("No active timers.")
        return

    # remove job
    for job in context.job_queue.jobs():
        if job.name == entry.job_name:
            job.schedule_removal()
            break

    # unpin message
    try:
        await context.bot.unpin_chat_message(
            chat_id=chat_id,
            message_id=entry.message_id,
        )
    except Exception:
        pass

    await update.message.reply_text("⛔ Timer cancelled.")


# ---------- cancel ALL timers ----------
async def cancel_all_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    chat_id = update.effective_chat.id
    timers = get_timers(chat_id)

    if not timers:
        await update.message.reply_text("No timers to cancel.")
        return

    for entry in timers:
        for job in context.job_queue.jobs():
            if job.name == entry.job_name:
                job.schedule_removal()

        try:
            await context.bot.unpin_chat_message(
                chat_id=chat_id,
                message_id=entry.message_id,
            )
        except Exception:
            pass

    clear_timers(chat_id)
    await update.message.reply_text("⛔ All timers cancelled.")
