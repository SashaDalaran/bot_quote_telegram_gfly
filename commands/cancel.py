# commands/cancel.py

from telegram import Update
from telegram.ext import ContextTypes

from core.timers import list_timers, cancel_timer


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    timers = list_timers(context, chat_id)

    if not timers:
        await update.message.reply_text("❌ Нет активных таймеров")
        return

    if context.args:
        idx = int(context.args[0]) - 1
        if 0 <= idx < len(timers):
            cancel_timer(context, timers[idx].job_name)
            await update.message.reply_text("✅ Таймер отменён")
        else:
            await update.message.reply_text("❌ Неверный номер")
        return

    text = "⛔ Какой таймер отменить?\n\n"
    for i, t in enumerate(timers, 1):
        text += f"{i} — {t.label or 'без названия'}\n"

    await update.message.reply_text(text)
