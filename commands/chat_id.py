# commands/chat_id.py

from telegram import Update
from telegram.ext import ContextTypes

from core.admin import is_admin


async def chat_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("⛔ Only admins can use this command.")
        return

    chat = update.effective_chat

    await update.message.reply_text(
        f"🆔 chat_id: `{chat.id}`\n"
        f"📌 type: `{chat.type}`\n"
        f"🏷 title: `{chat.title}`",
        parse_mode="Markdown",
    )
