# ==================================================
# commands/date_timer.py
# ==================================================

from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from core.timers import create_timer


async def timerdate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /timerdate 31.12.2025 23:59 [+3] Текст
    """

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "Использование:\n"
            "/timerdate DD.MM.YYYY HH:MM [+TZ] [текст]"
        )
        return

    try:
        date_str = context.args[0]
        time_str = context.args[1]

        tz_offset = 0
        text_start = 2

        # опциональный +3 / -2
        if len(context.args) > 2 and context.args[2].startswith(("+", "-")):
            tz_offset = int(context.args[2])
            text_start = 3

        label = " ".join(context.args[text_start:])

        target = datetime.strptime(
            f"{date_str} {time_str}",
            "%d.%m.%Y %H:%M"
        )

        if tz_offset:
            target = target.replace(
                hour=target.hour - tz_offset
            )

    except Exception:
        await update.message.reply_text("❌ Неверный формат даты")
        return

    sent = await update.message.reply_text("⏳ Таймер создан")

    create_timer(
        context=context,
        chat_id=update.effective_chat.id,
        target_time=target,
        message=label,
        pin_message_id=sent.message_id,
    )
