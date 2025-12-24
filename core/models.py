# core/models.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TimerEntry:
    chat_id: int
    # message id of BOT message we edit for countdown
    message_id: int
    target_time: datetime
    # job name in PTB JobQueue / APScheduler
    job_name: str

    # optional text under the timer (user's message)
    message: Optional[str] = None

    # legacy field (keep to avoid breaking old code)
    text: Optional[str] = None

    # optional message id of USER command message (if you want to pin/unpin it)
    pin_message_id: Optional[int] = None

    # to avoid editing the same text again
    last_text: Optional[str] = None
