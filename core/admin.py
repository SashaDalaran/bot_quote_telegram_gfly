# ==================================================
# core/admin.py — Admin Permission Helpers
# ==================================================
#
# This module contains helper utilities related
# to administrator permission checks.
#
# Responsibilities:
# - Determine whether the current user has
#   administrative privileges in the chat
#
# IMPORTANT:
# - This module contains Telegram-specific logic
#   by design (chat types, member status).
# - It should NOT contain business rules.
#
# ==================================================

from telegram import Update
from telegram.ext import ContextTypes

# ==================================================
# Admin check
# ==================================================
#
# Returns True if the user should be treated as admin.
#
# Rules:
# - Private chat → always admin
# - Group / Supergroup → user must be admin or creator
# - Channel posts → no user context → always False
#
async def is_admin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:

    chat = update.effective_chat
    user = update.effective_user

    # --------------------------------------------------
    # Channel posts
    # --------------------------------------------------
    #
    # Channels do not have a user context,
    # so admin checks are not applicable.
    #
    if user is None:
        return False

    # --------------------------------------------------
    # Private chat
    # --------------------------------------------------
    #
    # In private chats, the user is always
    # considered an administrator.
    #
    if chat.type == "private":
        return True

    # --------------------------------------------------
    # Groups / Supergroups
    # --------------------------------------------------
    #
    # Check the user's membership status.
    #
    member = await context.bot.get_chat_member(chat.id, user.id)

    return member.status in ("administrator", "creator")
