# ==================================================
# commands/date_timer.py — /timerdate
# ==================================================

import logging
from datetime import datetime, timezone, timedelta

_TBILISI_TZ = timezone(timedelta(hours=4))  # Asia/Tbilisi (UTC+4)

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.parser import parse_timerdate_args
from core.timers import create_timer

logger = logging.getLogger(__name__)


async def timerdate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /timerdate YYYY-MM-DD HH:MM [message]
    Example:
      /timerdate 2025-12-31 23:59 Happy New Year!
    """
    if not update.effective_chat or not update.effective_message:
        return

    try:
        target_time, message = parse_timerdate_args(update.effective_message.text or "", assume_tz=_TBILISI_TZ)
    except Exception:
        await update.effective_message.reply_text(
            "Формат: /timerdate YYYY-MM-DD HH:MM [сообщение]\n"
            "Пример: /timerdate 2025-12-31 23:59 Новый год!"
        )
        return

    now = datetime.now(timezone.utc)
    if target_time <= now:
        await update.effective_message.reply_text("Эта дата уже в прошлом 😅")
        return

    remaining = int((target_time - now).total_seconds())
    text = f"⏰ Time left: {remaining} sec"
    if message:
        text += f"\n{message}"

    sent = await update.effective_message.reply_text(text)

    # attach cancel button
    try:
        kb = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Cancel", callback_data=f"cancel_timer:{sent.message_id}")]]
        )
        await context.bot.edit_message_reply_markup(
            chat_id=sent.chat_id,
            message_id=sent.message_id,
            reply_markup=kb,
        )
    except Exception as e:
        logger.warning("Failed to set cancel button: %s", e)

    create_timer(
        context=context,
        chat_id=sent.chat_id,
        target_time=target_time,
        message=message,
        message_id=sent.message_id,  # ✅ это сообщение будем edit'ить
    )
