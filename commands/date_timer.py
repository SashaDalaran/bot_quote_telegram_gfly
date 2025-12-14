# ==================================================
# commands/date_timer.py
# ==================================================

import logging
from datetime import datetime, timedelta, timezone

from telegram import Update
from telegram.ext import ContextTypes

from core.timers import create_timer

logger = logging.getLogger(__name__)


async def timerdate_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    /timerdate DD.MM.YYYY HH:MM [+TZ] [message] [--pin]

    Example:
    /timerdate 31.12.2025 23:59 +3 Новый год 🎆 --pin
    """

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "❌ Формат:\n"
            "/timerdate DD.MM.YYYY HH:MM [+TZ] сообщение [--pin]"
        )
        return

    args = context.args
    chat_id = update.effective_chat.id

    # ================= DATE + TIME =================
    date_str = args[0]
    time_str = args[1]

    tz_hours = 0
    message_parts: list[str] = []
    pin = False

    # ================= PARSE REST =================
    for part in args[2:]:
        if part.startswith("+") or part.startswith("-"):
            try:
                tz_hours = int(part)
            except ValueError:
                pass
        elif part == "--pin":
            pin = True
        else:
            message_parts.append(part)

    message = " ".join(message_parts) if message_parts else None

    # ================= PARSE DATETIME =================
    try:
        naive_dt = datetime.strptime(
            f"{date_str} {time_str}",
            "%d.%m.%Y %H:%M",
        )
    except ValueError:
        await update.message.reply_text(
            "❌ Неверный формат даты или времени.\n"
            "Используй DD.MM.YYYY HH:MM"
        )
        return

    # ================= APPLY TZ =================
    target_time = (
        naive_dt
        .replace(tzinfo=timezone.utc)
        - timedelta(hours=tz_hours)
    )

    # ================= VALIDATION =================
    now_utc = datetime.now(timezone.utc)
    if target_time <= now_utc:
        await update.message.reply_text(
            "❌ Указанная дата уже в прошлом."
        )
        return

    # ================= CREATE PLACEHOLDER =================
    sent = await update.message.reply_text(
        "⏳ Таймер создан. Идёт отсчёт…"
    )

    pin_message_id = None
    if pin:
        try:
            await context.bot.pin_chat_message(
                chat_id=chat_id,
                message_id=sent.message_id,
                disable_notification=True,
            )
            pin_message_id = sent.message_id
        except Exception:
            logger.exception("Failed to pin timer message")

    # ================= CREATE TIMER =================
    create_timer(
        context=context,
        chat_id=chat_id,
        target_time=target_time,
        message=message,
        pin_message_id=pin_message_id,
    )

    logger.info(
        "Date timer created: chat=%s target=%s tz=%s",
        chat_id,
        target_time,
        tz_hours,
    )
