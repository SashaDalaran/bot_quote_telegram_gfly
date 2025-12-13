ъ# ==================================================
# commands/simple_timer.py — Telegram Simple Timer
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
    text = " ".join(context.args[1:]) or "⏰ Time is up!"

    try:
        seconds = parse_duration(duration_raw)
        if seconds <= 0:
            raise ValueError("Duration must be > 0")
    except Exception as e:
        await update.message.reply_text(f"❌ Invalid duration: {e}")
        return

    target_time = datetime.now(timezone.utc) + timedelta(seconds=seconds)

    info_msg = await update.message.reply_text(
        f"⏱ **Timer started!**\n"
        f"Duration: `{format_remaining_time(seconds)}`\n"
        f"Message: {text}",
        parse_mode="Markdown",
    )

    await create_timer(
        context=context,
        chat_id=update.effective_chat.id,
        target_time=target_time,
        message=text,
        pin_message_id=info_msg.message_id,
    )
