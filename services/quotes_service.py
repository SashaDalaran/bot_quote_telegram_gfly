# ==================================================
# services/quotes_service.py — Quotes Service
# ==================================================
#
# Loads and selects quotes from datasets used by the /quote command and daily jobs.
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
    """Service function: load quotes."""
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
    """Service function: get random quote."""
    if not quotes:
        return None
    return random.choice(quotes)