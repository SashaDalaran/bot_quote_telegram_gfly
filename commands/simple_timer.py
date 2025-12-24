# commands/simple_timer.py

from datetime import datetime, timedelta, timezone
from telegram import Update
from telegram.ext import ContextTypes

from core.parser import parse_duration
from core.timers import create_timer


async def timer_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    raw = " ".join(context.args or []).strip()
    seconds, message = parse_duration(raw)

    if seconds is None:
        await update.message.reply_text("Usage: /timer 10s message  OR  /timer 5m  OR  /timer 1h30m")
        return

    # 1) send bot message that we will edit
    status_msg = await update.message.reply_text("⏰ Timer started")

    # optional: pin the bot message (same one we edit)
    try:
        await context.bot.pin_chat_message(
            chat_id=update.effective_chat.id,
            message_id=status_msg.message_id,
            disable_notification=True,
        )
    except Exception:
        # ignore if no rights / private chat etc.
        pass

    # 2) create timer (store bot message_id!)
    now = datetime.now(timezone.utc)
    target_time = now + timedelta(seconds=seconds)

    await create_timer(
        context=context,
        chat_id=update.effective_chat.id,
        target_time=target_time,
        message=message,
        message_id=status_msg.message_id,
    )
