# commands/start.py

from telegram import Update
from telegram.ext import ContextTypes

START_TEXT = (
    "🐸 <b>Just Quotes Bot</b>\n\n"
    "Добро пожаловать!\n"
    "Я бот с цитатами, таймерами и мурлокской мудростью.\n\n"
    "📜 Используй /help чтобы увидеть все команды."
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    # ⚠️ Если по какой-то причине нет чата — просто выходим
    if chat is None:
        return

    # Универсальный способ — работает в ЛС, группе и канале
    await context.bot.send_message(
        chat_id=chat.id,
        text=(
            "🐸 <b>Just Quotes Bot</b>\n\n"
            "Добро пожаловать!\n"
            "Я бот с цитатами, таймерами и мурлокской мудростью.\n\n"
            "📜 Используй /help чтобы увидеть все команды."
        ),
        parse_mode="HTML",
    )
