from telegram import Update
from telegram.ext import ContextTypes

from core.timers import (
    list_timers,
    cancel_timer,
    cancel_all_timers,
)


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id

    # /cancel 2
    if context.args:
        try:
            index = int(context.args[0]) - 1
        except ValueError:
            await update.message.reply_text("❌ Укажи номер таймера")
            return

        timers = list_timers(context, chat_id)

        if not timers:
            await update.message.reply_text("⏳ Нет активных таймеров")
            return

        if index < 0 or index >= len(timers):
            await update.message.reply_text("❌ Неверный номер")
            return

        timer = timers[index]
        cancel_timer(context, timer["job_name"])

        await update.message.reply_text(
            f"🛑 Таймер отменён:\n{timer['label']}"
        )
        return

    # /cancel (без аргументов)
    timers = list_timers(context, chat_id)

    if not timers:
        await update.message.reply_text("⏳ Нет активных таймеров")
        return

    lines = ["Выбери таймер для отмены:\n"]
    for i, t in enumerate(timers, start=1):
        lines.append(f"{i} — {t['label']}")

    lines.append("\nОтправь:\n/cancel <номер>")

    await update.message.reply_text("\n".join(lines))


async def cancelall_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id

    cancel_all_timers(context, chat_id)

    await update.message.reply_text("🧹 Все таймеры отменены")
