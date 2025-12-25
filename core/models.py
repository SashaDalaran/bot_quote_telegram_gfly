# ==================================================
# core/models.py — Shared Data Models
# ==================================================
#
# Dataclasses / typed structures shared between layers (timers, holidays, guild events).
#
# Layer: Core
#
# Responsibilities:
# - Provide reusable, testable logic and infrastructure helpers
# - Avoid direct Telegram API usage (except JobQueue callback signatures where required)
# - Expose stable APIs consumed by services and commands
#
# Boundaries:
# - Core must remain independent from user interaction details.
# - Core should not import commands (top layer) to avoid circular dependencies.
#
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
        """Core utility:   post init  ."""
        if not self._uid:
            self._uid = uuid.uuid4().hex[:8]

    @property
    def job_name(self) -> str:
        # name visible in APScheduler logs, e.g. "timer:chat:msg:uid"
        """Core utility: job name."""
        mid = self.message_id if self.message_id is not None else 0
        return f"timer:{self.chat_id}:{mid}:{self._uid}"