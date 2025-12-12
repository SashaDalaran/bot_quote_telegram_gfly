import os
from datetime import timezone, timedelta

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CLEANUP_PASSWORD = os.getenv("CLEANUP_PASSWORD", "")

QUOTES_FILE = os.getenv("QUOTES_FILE", "data/quotes.txt")
BANLU_QUOTES_FILE = "data/quotersbanlu.txt"

BANLU_WOWHEAD_URL = "https://www.wowhead.com/ru/item=142225/бань-лу-спутник-великого-мастера"

MSK_TZ = timezone(timedelta(hours=3))
