from telegram import Update
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Commands:\n"
        "/timer <time> [message]\n"
        "/repeat <time> [message]\n"
        "/cancel\n"
        "/cancelrepeat\n"
        "/timers\n"
        "/banlu\n"
        "!цитата\n"
    )
