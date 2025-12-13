# commands/help_cmd.py

from telegram import Update
from telegram.ext import ContextTypes


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "📜 Доступные команды:\n\n"
        "/start — приветствие\n"
        "/help — список команд\n"
        "/quote — случайная цитата\n"
        "/timer — таймер\n"
        "/holidays — праздники\n"
        "/murloc_ai — мурлокская мудрость 🐸",
    )
