# ==================================================
# daily/holidays/__init__.py — Holidays Daily Package
# ==================================================
#
# Package marker for holidays daily job.
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
