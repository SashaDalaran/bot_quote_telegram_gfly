# ==================================================
# core/models.py — Timer data models
# ==================================================

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid


# --------------------------------------------------
# One-time timer
# --------------------------------------------------
@dataclass
class TimerEntry:
    chat_id: int
    message_id: int
    target_time: datetime
    message: Optional[str] = None

    pin: bool = False
    pinned_message_id: Optional[int] = None

    last_text: Optional[str] = None
    job_name: str = ""

    def __post_init__(self):
        if not self.job_name:
            self.job_name = f"timer_{uuid.uuid4().hex}"


# --------------------------------------------------
# Repeat timer (ЗАГЛУШКА, чтобы сервис не падал)
# --------------------------------------------------
@dataclass
class RepeatEntry:
    chat_id: int
    interval: int
    message: Optional[str] = None
    job_name: str = ""

    def __post_init__(self):
        if not self.job_name:
            self.job_name = f"repeat_{uuid.uuid4().hex}"
