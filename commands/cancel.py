# commands/cancel.py

from telegram import Update
from telegram.ext import ContextTypes

from core.timers_store import pop_last_timer, clear_timers
from services.timer_service import cancel_job_by_name

# /cancel
async def cancel_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await cancel_last_timer(update, context)


# /cancelall
async def cancel_all_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await cancel_all_timers(update, context)


# ❌❌ /cancelall — отменяет ВСЕ таймеры в чате
async def cancel_all_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    entries = clear_timers(chat_id)
    if not entries:
        await update.message.reply_text("❌ No active timers.")
        return

    for entry in entries:
        cancel_job_by_name(context, entry.job_name)

    await update.message.reply_text(f"🧹 Cancelled {len(entries)} timers.")


# commands/cancel.py

from telegram import Update
from telegram.ext import ContextTypes

from services.timer_service import cancel_all_timers
from services.timer_service import cancel_last_timer  # если есть


