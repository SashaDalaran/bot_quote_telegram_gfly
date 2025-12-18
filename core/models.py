# ==================================================
# core/models.py — Timer data models
# ==================================================

from dataclasses import dataclass
from datetime import datetime
import uuid


# --------------------------------------------------
# One-time timer
# --------------------------------------------------
@dataclass
class TimerEntry:
    chat_id: int
    message_id: int
    target_time: datetime
    message: str | None = None
    job_name: str = ""

    def __post_init__(self):
        if not self.job_name:
            self.job_name = f"timer_{uuid.uuid4().hex}"


# --------------------------------------------------
# Repeating timer (used by timer_service)
# --------------------------------------------------
@dataclass
class RepeatEntry:
    chat_id: int
    message_id: int
    interval_seconds: int
    message: str | None = None
    job_name: str = ""

    def __post_init__(self):
        if not self.job_name:
            self.job_name = f"repeat_{uuid.uuid4().hex}"