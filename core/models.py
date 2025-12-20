# core/models.py
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TimerEntry:
    chat_id: int
    target_time: datetime
    message: str | None
    job_name: str
