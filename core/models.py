from dataclasses import dataclass
from datetime import datetime


@dataclass
class TimerEntry:
    chat_id: int
    message: str
    target_time: datetime
    message_id: int
    pin: bool = False
