# core/models.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TimerEntry:
    chat_id: int
    message_id: int
    target_time: datetime
    job_name: str

    # то, что показываем под таймером
    message: Optional[str] = None

    # старое поле (на всякий)
    text: Optional[str] = None

    # чтобы не редактировать одно и то же
    last_text: Optional[str] = None
