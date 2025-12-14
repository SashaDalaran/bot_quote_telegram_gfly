# ==================================================
# commands/simple_timer.py
# ==================================================

from datetime import datetime, timedelta, timezone
from telegram import Update
from telegram.ext import ContextTypes

from core.parser import parse_duration
from core.timers import create_timer
from core.formatter import format_remaining_time


async def timer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❌ Usage:\n"
            "/timer 10s text\n"
            "/timer 5m\n"
            "/timer 1h20m Boss pull"
        )
        return

    duration_raw = context.args[0]
    message = " ".join(context.args[1:]) or "⏰ Time is up!"

    try:
        seconds = parse_duration(duration_raw)
        if seconds <= 0:
            raise ValueError("Duration must be > 0")
    except Exception as e:
        await update.message.reply_text(f"❌ Invalid duration: {e}")
        return

    target_time = datetime.now(timezone.utc) + timedelta(seconds=seconds)

    sent = await update.message.reply_text(
        f"⏱ <b>Timer started!</b>\n"
        f"Duration: {format_remaining_time(seconds)}\n"
        f"Message: {message}",
        parse_mode="HTML",
    )

    create_timer(
        context=context,
        chat_id=update.effective_chat.id,
        target_time=target_time,
        message=message,
        message_id=sent.message_id,
        pin_message_id=None,
    )
