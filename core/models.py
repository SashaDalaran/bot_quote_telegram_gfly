# core/models.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TimerEntry:
    chat_id: int
    message_id: int
    target_time: datetime
    job_name: str          # ← ВОТ ЭТО ОБЯЗАТЕЛЬНО
    text: str | None = None
