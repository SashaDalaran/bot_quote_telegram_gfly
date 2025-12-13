import logging

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

from config.settings import (
    TELEGRAM_BOT_TOKEN,
    QUOTES_FILE,
    BANLU_QUOTES_FILE,
)

from services.quotes_service import load_quotes
from services.banlu_service import load_banlu_quotes

from handlers.start import start
from handlers.help import help_command
from handlers.timer import (
    timer_command,
    cancel_command,
    repeat_command,
    cancel_repeat_command,
    timers_command,
    clear_pins_command,
)
from handlers.quotes import quote_command
from handlers.banlu import banlu_command


# ----------------- logging -----------------

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ----------------- main -----------------

def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    # ---- load data once (как в Discord) ----
    quotes = load_quotes(QUOTES_FILE)
    banlu_quotes = load_banlu_quotes(BANLU_QUOTES_FILE)

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # shared data for services (аналог bot state в Discord)
    app.bot_data["quotes"] = quotes
    app.bot_data["banlu_quotes"] = banlu_quotes

    # ---- filters ----
    priv_or_groups = filters.ChatType.PRIVATE | filters.ChatType.GROUPS
    channels = filters.ChatType.CHANNEL

    # ---- commands (private + groups) ----
    app.add_handler(CommandHandler("start", start, filters=priv_or_groups))
    app.add_handler(CommandHandler("help", help_command, filters=priv_or_groups))

    app.add_handler(CommandHandler("timer", timer_command, filters=priv_or_groups))
    app.add_handler(CommandHandler("cancel", cancel_command, filters=priv_or_groups))
    app.add_handler(CommandHandler("repeat", repeat_command, filters=priv_or_groups))
    app.add_handler(
        CommandHandler("cancelrepeat", cancel_repeat_command, filters=priv_or_groups)
    )
    app.add_handler(CommandHandler("timers", timers_command, filters=priv_or_groups))
    app.add_handler(
        CommandHandler("clearpins", clear_pins_command, filters=priv_or_groups)
    )

    # ---- banlu (аналог Discord command) ----
    app.add_handler(CommandHandler("banlu", banlu_command, filters=priv_or_groups))

    # ---- commands in channels (regex) ----
    app.add_handler(
        MessageHandler(channels & filters.Regex(r"^/start(\b|@)"), start)
    )
    app.add_handler(
        MessageHandler(channels & filters.Regex(r"^/help(\b|@)"), help_command)
    )
    app.add_handler(
        MessageHandler(channels & filters.Regex(r"^/timer(\b|@)"), timer_command)
    )
    app.add_handler(
        MessageHandler(channels & filters.Regex(r"^/banlu(\b|@)"), banlu_command)
    )

    # ---- text triggers ----
    app.add_handler(
        MessageHandler(filters.Regex(r"^!цитата\b"), quote_command)
    )

    logger.info("Telegram bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
