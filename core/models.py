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
    All timestamps are stored in UTC.
    """
    chat_id: int
    target_time: datetime            # UTC
    message_id: int                  # message being edited
    message: Optional[str] = None
    pin_message_id: Optional[int] = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def job_name(self) -> str:
        ts = int(self.target_time.timestamp())
        return f"timer:{self.chat_id}:{ts}"
