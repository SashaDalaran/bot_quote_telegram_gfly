# commands/cancel.py
from telegram import Update
from telegram.ext import ContextTypes

from core.timers_store import get_timers, clear_timers


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    timers = get_timers(chat_id)

    if not timers:
        await update.message.reply_text("⛔ Нет активных таймеров")
        return

    clear_timers(chat_id)
    await update.message.reply_text(f"🗑 Отменено таймеров: {len(timers)}")


# ✅ ДОБАВЛЯЕМ ЭТО
async def cancel_all_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await cancel_command(update, context)
