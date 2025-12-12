from telegram import Update
from telegram.ext import ContextTypes
from services.quotes_service import get_random_quote

async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quotes = context.bot_data.get("quotes", [])
    quote = get_random_quote(quotes)

    if not quote:
        await update.message.reply_text("Цитаты не найдены 🤷‍♂️")
        return

    await update.message.reply_text(f"💬 {quote}")
