# commands/date_timer.py

from datetime import datetime, timezone
from telegram import Update
from telegram.ext import ContextTypes

from core.timers import create_timer


async def timerdate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    dt = datetime.strptime(
        " ".join(context.args[:2]),
        "%d.%m.%Y %H:%M",
    ).replace(tzinfo=timezone.utc)

    label = " ".join(context.args[2:])
    msg = await update.message.reply_text("⏳ Таймер установлен")

    create_timer(context, chat_id, dt, label, msg.message_id)
