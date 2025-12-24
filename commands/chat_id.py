# ==================================================
# commands/chat_id.py — Chat ID Utility Command
# ==================================================
#
# This module defines a simple utility command
# used to display the current chat ID.
#
# Command:
# - /chat_id → replies with the numeric chat ID
#
# Use cases:
# - Bot configuration
# - Channel / group setup
# - Environment variable preparation
#
# IMPORTANT:
# - parse_mode is explicitly disabled
#   to ensure the chat ID is displayed
#   as plain text without formatting issues.
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
    # Админ‑only: чтобы в группах ID не выдавался всем подряд
    if not await is_admin(update, context):
        await update.message.reply_text("⛔ Эта команда доступна только администраторам.")
        return

    chat = update.effective_chat

    await update.message.reply_text(
        f"Chat ID:\n{chat.id}",
        parse_mode=None,  # IMPORTANT: disable formatting explicitly
    )
