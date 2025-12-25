# ==================================================
# core/__init__.py — Core Package
# ==================================================
#
# Package marker for core modules.
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
