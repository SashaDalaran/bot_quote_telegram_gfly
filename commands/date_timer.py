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

    raw = update.effective_message.text or ""
    tokens = raw.split()
    pin = False
    if "--pin" in tokens:
        pin = True
        tokens = [t for t in tokens if t != "--pin"]
    cleaned = " ".join(tokens)

    try:
        target_time, message = parse_timerdate_args(
            cleaned,
            assume_tz=_TBILISI_TZ,
        )
    except Exception:
        await update.effective_message.reply_text(
            "Формат: /timerdate <дата> <время> [TZ] [сообщение]\n"
            "Дата: YYYY-MM-DD или DD.MM.YYYY\n"
            "TZ (необязательно): +3, +03, +03:00, -5 ...\n"
            "Примеры:\n"
            "• /timerdate 2025-12-31 23:59 Новый год!\n"
            "• /timerdate 31.12.2025 23:59 +3 Happy New Year 🎆"
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

    # optional pin
    if pin:
        try:
            await context.bot.pin_chat_message(
                chat_id=sent.chat_id,
                message_id=sent.message_id,
                disable_notification=True,
            )
        except Exception as e:
            logger.warning("Pin failed: %s", e)

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
