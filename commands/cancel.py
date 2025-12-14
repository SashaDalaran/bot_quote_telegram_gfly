# ==================================================
# commands/cancel.py
# ==================================================

from telegram import Update
from telegram.ext import ContextTypes

from core.timers import (
    cancel_timer,
    cancel_all_timers,
    list_timers,
)


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id

    if not context.args:
        timers = list_timers(chat_id)

        if not timers:
            await update.message.reply_text("⛔ Нет активных таймеров")
            return

        lines = ["Выбери таймер для отмены:"]
        for i, t in enumerate(timers, start=1):
            lines.append(f"{i} — {t.label}")

        await update.message.reply_text("\n".join(lines))
        return

    try:
        index = int(context.args[0]) - 1
    except ValueError:
        await update.message.reply_text("❌ Укажи номер таймера")
        return

    timers = list_timers(chat_id)

    if index < 0 or index >= len(timers):
        await update.message.reply_text("❌ Неверный номер таймера")
        return

    timer = timers[index]
    cancel_timer(timer.id)

    await update.message.reply_text(f"✅ Таймер отменён:\n{timer.label}")


async def cancelall_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    count = cancel_all_timers(chat_id)
    await update.message.reply_text(f"🧹 Отменено таймеров: {count}")
