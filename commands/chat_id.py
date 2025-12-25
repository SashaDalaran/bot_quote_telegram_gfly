# ==================================================
# commands/chat_id.py — Chat ID Utility Command
# ==================================================
#
# User-facing /chat_id handler; prints the current chat ID (useful for channel configuration).
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

from core.admin import is_admin

# ==================================================
# /chat_id command
# ==================================================
#
# Replies with the current chat ID.
#
async def chat_id_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    # Admin-only: avoid leaking chat IDs to regular members in group chats.
    """Handle the /chat_id command."""
    if not await is_admin(update, context):
        await update.message.reply_text("⛔ This command is available to administrators only.")
        return

    chat = update.effective_chat

    await update.message.reply_text(
        f"Chat ID:\n{chat.id}",
        parse_mode=None,  # IMPORTANT: disable formatting explicitly
    )