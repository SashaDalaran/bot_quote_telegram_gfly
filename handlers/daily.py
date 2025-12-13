from telegram import Update
from telegram.ext import ContextTypes
from services.banlu_service import (
    get_random_banlu_quote,
    format_banlu_message,
)

async def banlu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quotes = context.bot_data.get("banlu_quotes", [])
    quote = get_random_banlu_quote(quotes)

    if not quote:
        await update.message.reply_text("Цитаты Бань Лу не найдены 🤷‍♂️")
        return

    await update.message.reply_text(format_banlu_message(quote))
