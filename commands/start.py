from telegram import Update
from telegram.ext import ContextTypes

START_TEXT = (
    "🐸 **Just Quotes Bot**\n\n"
    "Добро пожаловать!\n"
    "Я бот с цитатами, таймерами и мурлокской мудростью.\n\n"
    "📜 Используй /help чтобы увидеть все команды."
)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        START_TEXT,
        parse_mode="Markdown"
    )
