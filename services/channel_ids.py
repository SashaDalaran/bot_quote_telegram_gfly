import logging
import os
from typing import List

logger = logging.getLogger(__name__)


def parse_chat_ids(env_key: str) -> List[int]:
    """Parse comma-separated chat IDs from a single env var.

    Expected format:
      BANLU_CHANNEL_ID="-100123"  (single)
      HOLIDAYS_CHANNEL_ID="-100123,-100456"  (multiple)

    Returns a list of int chat IDs. If env var is missing/empty -> [].
    """
    raw = os.getenv(env_key, "").strip()
    if not raw:
        logger.warning("%s is not set; skipping send.", env_key)
        return []

    parts = [p.strip() for p in raw.split(",") if p.strip()]
    ids: List[int] = []

    for p in parts:
        try:
            ids.append(int(p))
        except ValueError:
            logger.warning("Invalid chat id '%s' in %s; skipping it.", p, env_key)

    if not ids:
        logger.warning("No valid chat IDs found in %s; skipping send.", env_key)

    return ids
