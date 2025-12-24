# core/models.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class TimerEntry:
    chat_id: int
    message_id: int
    target_time: datetime
    message: str = ""
    job_name: str = ""
    last_text: str = ""
