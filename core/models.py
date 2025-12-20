from dataclasses import dataclass
from datetime import datetime

@dataclass
class TimerEntry:
    chat_id: int
    message_id: int
    target_time: datetime
    message: str | None = None
    last_text: str | None = None
