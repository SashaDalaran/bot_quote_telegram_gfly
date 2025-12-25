# ==================================================
# core/admin.py — Admin Checks
# ==================================================
#
# Utilities to detect whether a user is an admin in the current chat.
#
# Layer: Core
#
# Responsibilities:
# - Provide reusable, testable logic and infrastructure helpers
# - Avoid direct Telegram API usage (except JobQueue callback signatures where required)
# - Expose stable APIs consumed by services and commands
#
# Boundaries:
# - Core must remain independent from user interaction details.
# - Core should not import commands (top layer) to avoid circular dependencies.
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

    """Core utility: is admin."""
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