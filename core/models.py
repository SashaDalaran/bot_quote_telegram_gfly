from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

@dataclass(slots=True)
class TimerEntry:
    chat_id: int
    message_id: int              # ⚠️ ЭТО И ЕСТЬ PINNED MESSAGE
    target_time: datetime
    message: Optional[str] = None
    last_text: Optional[str] = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def job_name(self) -> str:
        ts = int(self.target_time.timestamp())
        return f"timer:{self.chat_id}:{ts}"
