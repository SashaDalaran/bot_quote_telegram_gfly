import logging
from datetime import time

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

from core.settings import (
    TELEGRAM_BOT_TOKEN,
    QUOTES_FILE,
    BANLU_QUOTES_FILE,
    MSK_TZ,
)



from services.quotes_service import load_quotes
from services.banlu_service import load_banlu_quotes

# ===== commands =====
from commands.start import start
from commands.help import help_command
from commands.timer import (
    timer_command,
    cancel_command,
    repeat_command,
    cancel_repeat_command,
    timers_command,
    clear_pins_command,
)
from commands.quotes import quote_command
from commands.banlu import banlu_command

# ===== daily jobs =====
from daily.banlu.banlu_daily import banlu_daily_job
from daily.holidays.holidays_daily import holidays_daily_job


# ----------------- logging -----------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    # ---- load data once ----
    quotes = load_quotes(QUOTES_FILE)
    banlu_quotes = load_banlu_quotes(BANLU_QUOTES_FILE)

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # shared state
    app.bot_data["quotes"] = quotes
    app.bot_data["banlu_quotes"] = banlu_quotes

    # ---- filters ----
    priv_or_groups = filters.ChatType.PRIVATE | filters.ChatType.GROUPS
    channels = filters.ChatType.CHANNEL

    # ---- commands ----
    app.add_handler(CommandHandler("start", start, filters=priv_or_groups))
    app.add_handler(CommandHandler("help", help_command, filters=priv_or_groups))

    app.add_handler(CommandHandler("quote", quote_command, filters=priv_or_groups))
    app.add_handler(CommandHandler("banlu", banlu_command, filters=priv_or_groups))

    app.add_handler(CommandHandler("timer", timer_command, filters=priv_or_groups))
    app.add_handler(CommandHandler("cancel", cancel_command, filters=priv_or_groups))
    app.add_handler(CommandHandler("repeat", repeat_command, filters=priv_or_groups))
    app.add_handler(CommandHandler("cancelrepeat", cancel_repeat_command))
    app.add_handler(CommandHandler("timers", timers_command))
    app.add_handler(CommandHandler("clearpins", clear_pins_command))

    # ---- channel commands ----
    app.add_handler(MessageHandler(channels & filters.Regex(r"^/start"), start))
    app.add_handler(MessageHandler(channels & filters.Regex(r"^/help"), help_command))
    app.add_handler(MessageHandler(channels & filters.Regex(r"^/banlu"), banlu_command))

    # ---- daily jobs ----
    job_queue = app.job_queue

    # 10:00 — Ban’Lu
    job_queue.run_daily(
        banlu_daily_job,
        time=time(hour=10, minute=0),
        name="daily_banlu",
    )

    # 10:01 — Holidays
    job_queue.run_daily(
        holidays_daily_job,
        time=time(hour=10, minute=1),
        name="daily_holidays",
    )

    logger.info("Telegram bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
