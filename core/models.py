# core/models.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TimerEntry:
    chat_id: int
    message_id: int
    target_time: datetime  # MUST be UTC datetime
    message: Optional[str] = None

    # identification for JobQueue
    job_name: Optional[str] = None

    # optimization: don't re-edit same text
    last_text: Optional[str] = None
