# ==================================================
# commands/simple_timer.py — /timer
# ==================================================

import logging
from datetime import datetime, timedelta, timezone

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.parser import parse_timer_args
from core.timers import create_timer

logger = logging.getLogger(__name__)


async def timer_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /timer 10m [message]
    Examples:
      /timer 5m
      /timer 1h 30m stretch
      /timer 45s tea
    """
    if not update.effective_chat or not update.effective_message:
        return

    try:
        parsed = parse_timer_args(update.effective_message.text or "")
    except Exception:
        await update.effective_message.reply_text(
            "Формат: /timer 10m [сообщение]\n"
            "Примеры: /timer 5m, /timer 1h 30m чай"
        )
        return

    now = datetime.now(timezone.utc)
    target_time = now + timedelta(seconds=parsed.seconds)

    text = f"⏰ Time left: {parsed.seconds} sec"
    if parsed.message:
        text += f"\n{parsed.message}"

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

    # IMPORTANT:
    # твой create_timer (по предыдущей ошибке) НЕ принимает message_id,
    # поэтому используем pin_message_id
    create_timer(
        context=context,
        chat_id=sent.chat_id,
        target_time=target_time,
        message=parsed.message,
        pin_message_id=sent.message_id,
    )
