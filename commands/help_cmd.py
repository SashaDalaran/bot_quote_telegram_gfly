# ==================================================
# commands/help_cmd.py — Help & Command Reference
# ==================================================
#
# This module defines the /help command.
#
# Responsibilities:
# - Display a structured list of available commands
# - Show additional admin-only commands conditionally
# - Provide usage examples for timers
#
# IMPORTANT:
# - The help message is sent in HTML parse mode
# - Admin commands are shown only to chat administrators
#
# ==================================================

from telegram import Update
from telegram.ext import ContextTypes

from core.admin import is_admin

# ==================================================
# /help command
# ==================================================
#
# Displays the help menu with available commands.
#
async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    chat = update.effective_chat

    # --------------------------------------------------
    # Base help message (available to all users)
    # --------------------------------------------------
    #
    # HTML is used for better readability and structure.
    #
    text = (
        "📜 <b>Available commands</b>\n\n"

        "🔹 <b>General</b>\n"
        "/start — welcome message\n"
        "/help — show this menu\n"
        "/quote — random quote\n"
        "/murloc_ai — murloc wisdom 🐸\n\n"

        "⏱ <b>Timers</b>\n"
        "/timer — simple countdown timer\n"
        "Examples:\n"
        "/timer 10s tea\n"
        "/timer 5m\n"
        "/timer 1h20m Boss pull\n\n"

        "/timerdate — timer for a specific date\n"
        "Format:\n"
        "/timerdate DD.MM.YYYY HH:MM +TZ text [--pin]\n\n"
        "Examples:\n"
        "/timerdate 31.12.2025 23:59 +3 Happy New Year 🎆\n"
        "/timerdate 31.12.2025 23:59 +3 Happy New Year 🎆 --pin\n\n"

        "📌 <b>Option</b>\n"
        "--pin — pin the timer message in chat\n\n"

        "🎉 <b>Holidays</b>\n"
        "/holidays — today’s holidays\n\n"

        "ℹ️ <i>Commands work in private chats and groups.\n"
        "Channels are used for automatic publications.</i>\n"
    )

    # --------------------------------------------------
    # Admin-only commands
    # --------------------------------------------------
    #
    # These commands are shown only if the user
    # has administrator privileges in the chat.
    #
    if await is_admin(update, context):
        text += (
            "\n🛡 <b>Administrator</b>\n"
            "/cancel — cancel timers in this chat\n"
            "/cancelall — cancel all timers\n"
            "/chat_id — show chat ID\n"
        )

    # --------------------------------------------------
    # Send help message
    # --------------------------------------------------
    await context.bot.send_message(
        chat_id=chat.id,
        text=text,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
