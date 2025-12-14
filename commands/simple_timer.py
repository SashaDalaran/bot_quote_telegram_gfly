# ==================================================
# commands/simple_timer.py
# ==================================================

from datetime import datetime, timedelta, timezone
from telegram import Update
from telegram.ext import ContextTypes

from core.timers import create_timer


async def timer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Формат: /timer 10s текст")
        return

    raw = context.args[0].lower()
    message = " ".join(context.args[1:]) or None

    seconds = 0
    if raw.endswith("s"):
        seconds = int(raw[:-1])
    elif raw.endswith("m"):
        seconds = int(raw[:-1]) * 60
    elif raw.endswith("h"):
        seconds = int(raw[:-1]) * 3600
    else:
        await update.message.reply_text("Неверный формат времени.")
        return

    target_time = datetime.now(timezone.utc) + timedelta(seconds=seconds)

    msg = await update.message.reply_text(
        f"⏳ <b>Осталось:</b> {seconds} сек.",
        parse_mode="HTML",
    )

    create_timer(
        context,
        chat_id=update.effective_chat.id,
        target_time=target_time,
        message_id=msg.message_id,
        message=message,
        pin_message_id=None,
    )
