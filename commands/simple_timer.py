from telegram import Update
from telegram.ext import ContextTypes

from core.timers import create_timer
from core.parser import parse_timer

async def timer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    seconds, text = parse_timer(context.args)
    if seconds <= 0:
        await update.message.reply_text("Invalid time.")
        return

    await create_timer(
        context=context,
        chat_id=update.effective_chat.id,
        seconds=seconds,
        message=text,
    )
