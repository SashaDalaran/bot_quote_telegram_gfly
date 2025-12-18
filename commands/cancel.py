# ==================================================
# commands/cancel.py
# ==================================================

from telegram import Update
from telegram.ext import ContextTypes

from core.timers import get_timers, clear_timers


# /cancel — отменить таймеры в текущем чате
async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    timers = get_timers(chat_id)

    if not timers:
        await update.message.reply_text("No timers to cancel.")
        return

    # удаляем jobs из job_queue
    for entry in timers:
        for job in context.job_queue.jobs():
            if job.name == entry.job_name:
                job.schedule_removal()

        # пробуем убрать закреп
        try:
            await context.bot.unpin_chat_message(
                chat_id=chat_id,
                message_id=entry.message_id,
            )
        except Exception:
            pass

    clear_timers(chat_id)
    await update.message.reply_text("⛔ Timer cancelled.")


# /cancel_all — алиас (на будущее / если используешь)
async def cancel_all_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await cancel_command(update, context)
