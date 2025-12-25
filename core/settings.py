# ==================================================
# core/settings.py — Application Configuration
# ==================================================
#
# Central configuration: loads environment variables and defines shared constants used across the bot.
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
import os
from datetime import timezone, timedelta

# ==================================================
# Required secrets
# ==================================================
#
# TELEGRAM_BOT_TOKEN
# - Telegram bot authentication token
# - MUST be provided via environment variables
#
# The application fails immediately if the token
# is missing to avoid undefined runtime behavior.
#

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

# ==================================================
# Data file paths
# ==================================================
#
# Paths to local data files used by services.
#
# These values can be overridden via environment
# variables if needed (e.g. in production).
#

QUOTES_FILE = os.getenv("QUOTES_FILE", "data/quotes.txt")
BANLU_QUOTES_FILE = os.getenv(
    "BANLU_QUOTES_FILE",
    "data/quotersbanlu.txt",
)

# ==================================================
# External resources
# ==================================================
#
# Public reference links used in formatted messages.
#

BANLU_WOWHEAD_URL = "https://www.wowhead.com/item=142225"  # Ban'Lu (Grandmaster's Companion)

# ==================================================
# Timezone configuration
# ==================================================
#
# Default application timezone.
#
# MSK (UTC+3) is used consistently for:
# - scheduled daily jobs
# - holiday calculations
# - user-facing timestamps
#
# NOTE:
# - All internal timers still operate in UTC
#

MSK_TZ = timezone(timedelta(hours=3))