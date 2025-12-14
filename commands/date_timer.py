# ==================================================
# commands/date_timer.py
# ==================================================

import re
from datetime import datetime, timedelta, timezone

from telegram import Update
from telegram.ext import ContextTypes

from core.timers import create_timer


DATE_RE = re.compile(
    r"^(\d{2}\.\d{2}\.\d{4})\s+(\d{2}:\d{2})\s*([+-]\d+)?\s*(.*)$"
)


async def date_timer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Использование:\n"
            "/timerdate 31.12.2025 23:59 +3 Новый год 🎆"
        )
        return

    text = " ".join(context.args)
    match = DATE_RE.match(text)

    if not match:
        await update.message.reply_text("Неверный формат даты.")
        return

    date_str, time_str, tz_str, label = match.groups()
    tz_hours = int(tz_str) if tz_str else 0

    # --- ПРАВИЛЬНЫЙ timezone ---
    local_tz = timezone(timedelta(hours=tz_hours))

    local_dt = datetime.strptime(
        f"{date_str} {time_str}", "%d.%m.%Y %H:%M"
    ).replace(tzinfo=local_tz)

    target_time = local_dt.astimezone(timezone.utc)

    if target_time <= datetime.now(timezone.utc):
        await update.message.reply_text("⛔ Это время уже прошло.")
        return

    # --- отправляем сообщение ---
    msg = await update.message.reply_text("⏳")

    # --- пиним ИМЕННО ЕГО ---
    await context.bot.pin_chat_message(
        chat_id=update.effective_chat.id,
        message_id=msg.message_id,
    )

    # --- создаём таймер ---
    create_timer(
        context=context,
        chat_id=update.effective_chat.id,
        target_time=target_time,
        message=label or "",
        pin_message_id=msg.message_id,
    )
