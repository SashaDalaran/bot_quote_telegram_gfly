# commands/cancel.py

from telegram import Update
from telegram.ext import ContextTypes

from core.timers_store import (
    cancel_timer,
    cancel_all_timers_for_chat,
)


# -------------------------
# /cancel <id>
# -------------------------

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Укажи ID таймера")
        return

    timer_id = context.args[0]

    if cancel_timer(timer_id):
        await update.message.reply_text(f"🛑 Таймер {timer_id} отменён")
    else:
        await update.message.reply_text("❌ Таймер не найден")


# -------------------------
# /cancelall
# -------------------------

async def cancel_all_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    count = cancel_all_timers_for_chat(chat_id)

    await update.message.reply_text(
        f"🧹 Отменено таймеров: {count}"
    )
