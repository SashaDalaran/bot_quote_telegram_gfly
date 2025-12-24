# commands/simple_timer.py

from datetime import datetime, timedelta, timezone

from telegram import Update
from telegram.ext import ContextTypes

from core.formatter import format_remaining_time
from core.parser import parse_duration
from core.timers import create_timer


async def timer_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    try:
        seconds, msg = parse_duration(context.args)
    except Exception:
        await update.message.reply_text("Usage: /timer 10s [message]  (also 5m, 2h, 1h30m, ...)")
        return

    target_time = datetime.now(timezone.utc) + timedelta(seconds=seconds)

    text = f"⏰ Time left: {format_remaining_time(seconds)}"
    if msg:
        text += f"\n{msg}"

    sent = await update.message.reply_text(text)

    create_timer(
        context=context,
        chat_id=update.effective_chat.id,
        target_time=target_time,
        message=msg,
        message_id=sent.message_id,          # ✅ ВАЖНО: это сообщение БОТА
        pin_message_id=update.message.message_id,
    )
