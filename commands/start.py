# ==================================================
# commands/start.py — Start / Welcome Command
# ==================================================
#
# User-facing /start handler; sends a short welcome message and points users to /help.
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

# ==================================================
# Static welcome message
# ==================================================
#
# Centralized as a constant to avoid duplication
# and make future edits straightforward.
#
START_TEXT = (
    "🐸 <b>Just Quotes Bot</b>\n\n"
    "Welcome!\n"
    "I am a bot with quotes, timers, holidays and Murloc wisdom.\n\n"
    "📜 Use /help to see all available commands."
)

# ==================================================
# /start command
# ==================================================
#
# Sends a welcome message to the current chat.
#
async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Handle the /start command."""
    chat = update.effective_chat

    # Safety guard: should never happen, but keeps the command robust
    if chat is None:
        return

    # Universal send method:
    # works in private chats, groups and channels
    await context.bot.send_message(
        chat_id=chat.id,
        text=START_TEXT,
        parse_mode="HTML",
    )