# ==================================================
# core/models.py — Timer Domain Models
# ==================================================

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# ==================================================
# One-time timer
# ==================================================

@dataclass
class TimerEntry:
    chat_id: int
    target_time: datetime
    message_id: int
    message: Optional[str] = None

    last_text: Optional[str] = None
    job_name: str = field(init=False)

    def __post_init__(self):
        self.job_name = f"timer:{self.chat_id}:{self.message_id}"


# ==================================================
# Repeating timer
# ==================================================

@dataclass
class RepeatEntry:
    chat_id: int
    interval: int  # seconds
    message: Optional[str] = None

    job_name: str = field(init=False)

    def __post_init__(self):
        self.job_name = f"repeat:{self.chat_id}:{id(self)}"
