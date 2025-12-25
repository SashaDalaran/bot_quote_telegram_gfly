# ==================================================
# services/banlu_service.py — Ban'Lu Quotes Service
# ==================================================
#
# Loads Ban'Lu quotes and provides helpers for daily posting.
#
# Layer: Services
#
# Responsibilities:
# - Encapsulate domain logic and data access
# - Keep formatting rules consistent across commands and daily jobs
# - Provide stable functions consumed by commands/daily scripts
#
# Boundaries:
# - Services may use core utilities, but should avoid importing command modules.
# - Services should not perform Telegram network calls directly (commands/daily own messaging).
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
    """Service function: load banlu quotes."""
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
    """Service function: get random banlu quote."""
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
    """Service function: format banlu message."""
    return (
        "🐉 Ban’Lu — Companion of the Grand Master\n\n"
        f"💬 {quote}\n\n"
        f"🔗 Learn more: {BANLU_WOWHEAD_URL}"
    )