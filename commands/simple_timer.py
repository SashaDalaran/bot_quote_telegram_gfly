# ==================================================
# commands/simple_timer.py — Telegram Simple Timer
# ==================================================

import asyncio
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from core.duration import parse_duration  # если нет — скажи, дам


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
    except Exception as e:
        await update.message.reply_text(f"❌ Invalid duration: {e}")
        return

    await update.message.reply_text(
        f"⏱ **Timer started!**\n"
        f"Duration: `{seconds}` sec\n"
        f"Message: {text}",
        parse_mode="Markdown",
    )

    await asyncio.sleep(seconds)

    await update.message.reply_text(f"⏰ {text}")


def setup(application):
    application.add_handler(CommandHandler("timer", timer_command))
