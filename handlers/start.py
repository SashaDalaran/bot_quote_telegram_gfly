from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I am timer bot.\n"
        "Use /timer 5 (5 minutes)\n"
        "Use /help for all commands."
    )
