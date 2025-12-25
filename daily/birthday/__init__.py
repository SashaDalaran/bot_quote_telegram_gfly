# ==================================================
# daily/birthday/__init__.py — Guild Events Daily Package
# ==================================================
#
# Package marker for guild events daily job.
#
# Layer: Daily
#
# Responsibilities:
# - Schedule recurring jobs via JobQueue
# - Load/format content via services
# - Send messages to configured channels with minimal side effects
#
# Boundaries:
# - Daily jobs are orchestration: avoid putting domain logic here—keep it in services/core.
#
# ==================================================
from .birthday_daily import setup_birthday_daily

__all__ = ["setup_birthday_daily"]