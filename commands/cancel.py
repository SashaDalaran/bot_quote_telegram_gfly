# ==================================================
# commands/cancel.py
# ==================================================

from telegram import Update
from telegram.ext import ContextTypes

from core.timers import list_timers, cancel_timer


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    args = context.args

    timers = list_timers(context, chat_id)

    if not timers:
        await update.message.reply_text("❌ Нет активных таймеров")
        return

    # /cancel 2
    if args:
        try:
            idx = int(args[0]) - 1
        except ValueError:
            await update.message.reply_text("❌ Используй: /cancel <номер>")
            return

        if idx < 0 or idx >= len(timers):
            await update.message.reply_text("❌ Неверный номер таймера")
            return

        timer = timers[idx]
        cancel_timer(context, timer.job_name)

        await update.message.reply_text(
            f"✅ Таймер отменён:\n{timer.label or 'без описания'}"
        )
        return

    # /cancel → список
    lines = ["🛑 Выбери таймер для отмены:"]
    for i, t in enumerate(timers, start=1):
        lines.append(f"{i}. {t.label or 'без описания'}")

    lines.append("\nОтмени так: /cancel 2")

    await update.message.reply_text("\n".join(lines))
