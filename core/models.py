# ==================================================
# core/models.py — Core Data Models
# ==================================================
#
# This module defines core data structures used
# across the application.
#
# Responsibilities:
# - Represent internal state in a structured form
# - Provide small, safe helpers tied to the data itself
#
# IMPORTANT:
# - Models must remain lightweight
# - No Telegram API calls
# - No business logic beyond trivial helpers
#
# ==================================================

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

# ==================================================
# Timer models
# ==================================================
#
# Represents a single one-time countdown timer.
#
# Design notes:
# - All timestamps are stored in UTC
# - The model is immutable in intent (no setters)
# - slots=True is used to:
#   • reduce memory usage
#   • prevent accidental dynamic attributes
#
@dataclass(slots=True)
class TimerEntry:
    """
    One-time countdown timer.

    Attributes:
        chat_id (int):
            Telegram chat ID where the timer is running.

        target_time (datetime):
            Absolute moment when the timer finishes.
            Must be timezone-aware (UTC).

        message_id (int):
            Telegram message ID that is updated by the countdown.

        message (Optional[str]):
            Optional label or description attached to the timer.

        pin_message_id (Optional[int]):
            Optional pinned message ID associated with the timer.

        created_at (datetime):
            Timer creation timestamp (UTC).
    """

    chat_id: int
    target_time: datetime
    message_id: int
    message: Optional[str] = None
    pin_message_id: Optional[int] = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # ==================================================
    # Derived properties
    # ==================================================
    #
    # Generates a unique and deterministic job name
    # for JobQueue scheduling.
    #
    # Format:
    #   timer:<chat_id>:<unix_timestamp>
    #
    @property
    def job_name(self) -> str:
        ts = int(self.target_time.timestamp())
        return f"timer:{self.chat_id}:{ts}"
