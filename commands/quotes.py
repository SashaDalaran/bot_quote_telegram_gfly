# ==================================================
# commands/quotes.py — Random Quote Command
# ==================================================
#
# User-facing /quote handler; returns a random quote from the preloaded dataset.
#
# Layer: Commands
#
# Responsibilities:
# - Validate/parse user input (minimal)
# - Delegate work to services/core
# - Send user-facing responses via Telegram API
#
# Boundaries:
# - Commands do not implement business logic; they orchestrate user interaction.
# - Keep commands thin and deterministic; move reusable logic to services/core.
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
    """Handle the /quote command."""
    quotes = context.bot_data.get("quotes", [])

    quote = get_random_quote(quotes)

    if not quote:
        await update.message.reply_text("❌ No quotes found")
        return

    await update.message.reply_text(f"💬 {quote}")