# ==================================================
# core/models.py
# ==================================================

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass(slots=True)
class TimerEntry:
    """
    One-time countdown timer.
    All timestamps are UTC.
    """
    chat_id: int
    target_time: datetime              # UTC
    message: str
    pin_message_id: Optional[int] = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
