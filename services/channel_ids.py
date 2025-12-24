import logging
import os
from typing import Iterable, List, Optional


logger = logging.getLogger(__name__)


def parse_chat_ids(primary_key: str, fallback_keys: Optional[Iterable[str]] = None) -> List[int]:
    """Parse comma-separated chat/channel IDs from env.

    Examples:
      - One ID:   "-1001234567890"
      - Many IDs: "-1001,-1002,-1003"

    Returns an empty list if no env var is set.
    """

    raw = (os.getenv(primary_key) or "").strip()
    if not raw and fallback_keys:
        for k in fallback_keys:
            raw = (os.getenv(k) or "").strip()
            if raw:
                break

    if not raw:
        return []

    ids: List[int] = []
    raw = raw.replace(";", ",")
    for part in [p.strip() for p in raw.split(",") if p.strip()]:
        try:
            ids.append(int(part))
        except ValueError:
            logger.warning("Invalid chat id in %s: %r", primary_key, part)

    # De-dup while keeping order
    seen = set()
    out: List[int] = []
    for i in ids:
        if i not in seen:
            out.append(i)
            seen.add(i)
    return out
