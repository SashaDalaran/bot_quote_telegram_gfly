# ==================================================
# commands/date_timer.py — /timerdate command
# ==================================================

from datetime import datetime, timezone

from telegram import Update
from telegram.ext import ContextTypes

from core.parser import parse_datetime_with_tz
from core.timers import create_timer


async def timerdate_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    msg = update.effective_message
    if msg is None:
        return

    args = context.args
    if not args:
        await msg.reply_text(
            "Usage:\n"
            "/timerdate DD.MM.YYYY HH:MM +TZ text [--pin]"
        )
        return

    try:
        target_time, msg_start, _ = parse_datetime_with_tz(args)
    except ValueError as e:
        await msg.reply_text(f"❌ Bad format: {e}")
        return

    now = datetime.now(timezone.utc)
    remaining = int((target_time - now).total_seconds())

    if remaining <= 0:
        await msg.reply_text("❌ Target time must be in the future.")
        return

    # текст без флагов
    message_parts = [
        a for a in args[msg_start:]
        if not a.startswith("--")
    ]
    message = " ".join(message_parts) if message_parts else None

    should_pin = "--pin" in args
    chat_id = update.effective_chat.id

    create_timer(
        context=context,
        chat_id=chat_id,
        target_time=target_time,
        text=message,
        pin=should_pin,
    )

    await msg.reply_text("⏳ Date timer started.")
