from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class TimerEntry:
    """
    One-time timer with countdown.
    All timestamps MUST be in UTC.
    """
    chat_id: int
    target_time: datetime          # UTC datetime
    pin_message_id: int
    message: Optional[str] = None
    quote: Optional[str] = None
    job_name: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RepeatEntry:
    """
    Repeating timer entry.
    """
    chat_id: int
    interval: int                  # seconds
    message: Optional[str] = None
    job_name: str = ""
