from datetime import datetime, timedelta, timezone
from telegram import Update
from telegram.ext import ContextTypes

from core.timers import create_timer
from core.parser import parse_duration


async def timer_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not context.args:
        await update.message.reply_text(
            "❌ Format: /timer 30s | 5m | 1h | 1h30m"
        )
        return

    try:
        seconds = parse_duration(context.args[0])
    except ValueError as e:
        await update.message.reply_text(f"❌ {e}")
        return

    target_time = datetime.now(timezone.utc) + timedelta(seconds=seconds)
    text = " ".join(context.args[1:]) if len(context.args) > 1 else None

    msg = await update.message.reply_text("⏳ Timer started...")

    create_timer(
        context=context,
        chat_id=update.effective_chat.id,
        target_time=target_time,
        text=text,
        pin_message_id=msg.message_id,
    )
