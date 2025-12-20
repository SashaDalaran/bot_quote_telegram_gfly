# core/models.py
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TimerEntry:
    chat_id: int
    message_id: int
    target_time: datetime
    text: str | None = None
    pin: bool = False
    last_text: str | None = None
