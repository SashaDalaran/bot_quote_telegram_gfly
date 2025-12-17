# ==================================================
# services/banlu_service.py — Ban’Lu Domain Logic
# ==================================================
#
# This module contains all domain-specific logic
# related to Ban’Lu quotes.
#
# Responsibilities:
# - Load Ban’Lu quotes from a text file
# - Select a random quote
# - Format a Telegram-ready message
#
# IMPORTANT:
# - This module contains NO Telegram-specific code
#   (no bot, no context, no chat IDs).
# - It can be reused by commands, daily jobs,
#   or any other delivery mechanism.
#
# ==================================================

import random

from core.settings import BANLU_WOWHEAD_URL

# ==================================================
# Data loading
# ==================================================
#
# Loads Ban’Lu quotes from a UTF-8 encoded text file.
# Each non-empty line represents a single quote.
#
def load_banlu_quotes(path: str) -> list[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        # Fail gracefully if the quotes file is missing
        return []

# ==================================================
# Quote selection
# ==================================================
#
# Returns a random Ban’Lu quote from the provided list.
# Returns None if the list is empty.
#
def get_random_banlu_quote(quotes: list[str]) -> str | None:
    if not quotes:
        return None
    return random.choice(quotes)

# ==================================================
# Message formatting
# ==================================================
#
# Formats a Ban’Lu quote into a human-readable
# Telegram message.
#
# The message includes:
# - A short character description
# - The quote itself
# - A reference link (Wowhead)
#
def format_banlu_message(quote: str) -> str:
    return (
        "🐉 Ban’Lu — Companion of the Grand Master\n\n"
        f"💬 {quote}\n\n"
        f"🔗 Learn more: {BANLU_WOWHEAD_URL}"
    )
