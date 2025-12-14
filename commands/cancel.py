from telegram import Update
from telegram.ext import ContextTypes

from core.timers import (
    list_timers,
    cancel_timer,
    cancel_all_timers,
)
from core.admin import is_admin


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    args = context.args

    timers = list_timers(context, chat_id)

    # ---------- нет таймеров ----------
    if not timers:
        await update.message.reply_text("❌ Нет активных таймеров.")
        return

    # ---------- /cancel ----------
    if not args:
        lines = ["❌ **Выбери таймер для отмены:**\n"]

        for i, timer in enumerate(timers, start=1):
            # предполагаем, что у таймера есть display()
            lines.append(f"{i}️⃣ {timer.display()}")

        lines.append("\n➡️ Используй: `/cancel <номер>`")

        await update.message.reply_text(
            "\n".join(lines),
            parse_mode="Markdown",
        )
        return

    # ---------- /cancel <n> ----------
    try:
        index = int(args[0]) - 1
    except ValueError:
        await update.message.reply_text("⚠️ Номер должен быть числом.")
        return

    if index < 0 or index >= len(timers):
        await update.message.reply_text("⚠️ Таймера с таким номером нет.")
        return

    timer = timers[index]

    canceled = cancel_timer(
        context=context,
        job_name=timer.job_name,
    )

    if not canceled:
        await update.message.reply_text("⚠️ Таймер уже завершён или не найден.")
        return

    await update.message.reply_text(
        "🗑 **Таймер отменён:**\n"
        f"{timer.display()}",
        parse_mode="Markdown",
    )


async def cancelall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ⚠️ оставляем как админскую «опасную» команду
    if not await is_admin(update, context):
        await update.message.reply_text("⛔ Only admins can cancel all timers.")
        return

    removed = cancel_all_timers(
        context=context,
        chat_id=update.effective_chat.id,
    )

    if removed == 0:
        await update.message.reply_text("❌ No active timers found.")
    else:
        await update.message.reply_text(f"🗑 Canceled {removed} timer(s).")
