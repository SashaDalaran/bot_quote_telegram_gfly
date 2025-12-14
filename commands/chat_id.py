# ==================================================
# commands/chat_id.py
# ==================================================

from telegram import Update
from telegram.ext import ContextTypes


async def chat_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    await update.message.reply_text(
        f"Chat ID:\n{chat.id}",
        parse_mode=None,  # ❗ ВАЖНО
    )
