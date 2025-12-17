# ==================================================
# services/quotes_service.py — Quotes Domain Service
# ==================================================
#
# This module contains domain-level logic
# related to generic quotes.
#
# Responsibilities:
# - Load quotes from a text file
# - Provide a helper to select a random quote
#
# IMPORTANT:
# - This module contains NO Telegram-specific code.
# - It operates only on plain text data.
# - Quotes delivery and formatting are handled elsewhere.
#
# ==================================================

import random
import logging

logger = logging.getLogger(__name__)

# ==================================================
# Data loading
# ==================================================
#
# Loads quotes from a UTF-8 encoded text file.
# Each non-empty line represents a single quote.
#
# Logs the number of loaded quotes for visibility.
#
def load_quotes(path: str) -> list[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            quotes = [line.strip() for line in f if line.strip()]

        logger.info("Loaded %d quotes from %s", len(quotes), path)
        return quotes

    except FileNotFoundError:
        # Fail gracefully if the quotes file is missing
        logger.warning("%s not found, quotes feature disabled", path)
        return []

# ==================================================
# Quote selection
# ==================================================
#
# Returns a random quote from the provided list.
# Returns None if the list is empty.
#
def get_random_quote(quotes: list[str]) -> str | None:
    if not quotes:
        return None
    return random.choice(quotes)
