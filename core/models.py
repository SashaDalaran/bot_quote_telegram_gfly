# ==================================================
# core/models.py
# ==================================================

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass(slots=True)
class TimerEntry:
    """
    One-time timer with countdown.
    All timestamps MUST be in UTC.
    """
    chat_id: int
    target_time: datetime                  # UTC datetime
    pin_message_id: Optional[int] = None
    message: Optional[str] = None
    quote: Optional[str] = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def job_name(self) -> str:
        ts = int(self.target_time.timestamp())
        return f"timer:{self.chat_id}:{ts}"


@dataclass(slots=True)
class RepeatEntry:
    """
    Repeating timer entry.
    """
    chat_id: int
    interval: int                          # seconds
    message: Optional[str] = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def job_name(self) -> str:
        return f"repeat:{self.chat_id}:{self.interval}"
