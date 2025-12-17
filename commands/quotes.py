# ==================================================
# commands/quotes.py — Random Quote Command
# ==================================================
#
# This module defines a simple user-facing command
# for displaying a random quote.
#
# Command:
# - /quote → sends a random quote from the loaded dataset
#
# Responsibilities:
# - Retrieve cached quotes from bot_data
# - Delegate quote selection to the service layer
# - Send a formatted reply to the user
#
# IMPORTANT:
# - This module does NOT load quote files
# - Quote loading and selection logic lives in services
#
# ==================================================

from telegram import Update
from telegram.ext import ContextTypes

from services.quotes_service import get_random_quote

# ==================================================
# /quote command
# ==================================================
#
# Sends a random quote to the chat.
#
async def quote_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    # Quotes are expected to be preloaded
    # and stored in bot_data at application startup
    quotes = context.bot_data.get("quotes", [])

    quote = get_random_quote(quotes)

    if not quote:
        await update.message.reply_text("❌ No quotes found")
        return

    await update.message.reply_text(f"💬 {quote}")
