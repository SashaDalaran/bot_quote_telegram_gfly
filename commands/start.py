# ==================================================
# commands/start.py — Start / Welcome Command
# ==================================================
#
# This module defines the /start command.
#
# Responsibilities:
# - Display a welcome message
# - Introduce the bot’s main features
# - Guide the user to the /help command
#
# IMPORTANT:
# - HTML parse mode is used intentionally
# - The command works in private chats, groups and channels
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
    "Добро пожаловать!\n"
    "Я бот с цитатами, таймерами и мурлокской мудростью.\n\n"
    "📜 Используй /help чтобы увидеть все команды."
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
