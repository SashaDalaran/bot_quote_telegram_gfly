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
    All timestamps are UTC.
    """
    chat_id: int
    target_time: datetime
    message: Optional[str] = None
    pin_message_id: Optional[int] = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def job_name(self) -> str:
        ts = int(self.target_time.timestamp())
        return f"timer:{self.chat_id}:{ts}"
