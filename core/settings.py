import os
from datetime import timezone, timedelta

# ============================
# Secrets
# ============================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

# ============================
# Data files
# ============================

QUOTES_FILE = os.getenv("QUOTES_FILE", "data/quotes.txt")
BANLU_QUOTES_FILE = "data/quotes_banlu.txt"

# ============================
# External links
# ============================

BANLU_WOWHEAD_URL = (
    "https://www.wowhead.com/ru/item=142225/"
    "бань-лу-спутник-великого-мастера"
)

# ============================
# Timezone
# ============================

MSK_TZ = timezone(timedelta(hours=3))
