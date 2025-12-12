import random
import logging

logger = logging.getLogger(__name__)

def load_quotes(path: str) -> list[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            quotes = [line.strip() for line in f if line.strip()]
        logger.info("Loaded %d quotes from %s", len(quotes), path)
        return quotes
    except FileNotFoundError:
        logger.warning("%s not found, quotes disabled", path)
        return []


def get_random_quote(quotes: list[str]) -> str | None:
    if not quotes:
        return None
    return random.choice(quotes)