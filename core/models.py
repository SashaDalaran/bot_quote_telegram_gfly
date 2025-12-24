# ==================================================
# core/models.py — shared dataclasses
# ==================================================

from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass
class TimerEntry:
    chat_id: int
    message_id: int | None
    target_time: datetime
    message: str | None = None
    pin_message_id: int | None = None
    last_text: str | None = None
    _uid: str = ""

    def __post_init__(self) -> None:
        if not self._uid:
            self._uid = uuid.uuid4().hex[:8]

    @property
    def job_name(self) -> str:
        # name виден в логах APScheduler как "timer:chat:msg:uid"
        mid = self.message_id if self.message_id is not None else 0
        return f"timer:{self.chat_id}:{mid}:{self._uid}"
