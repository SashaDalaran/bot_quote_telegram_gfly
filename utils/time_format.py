import os
import logging
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone, time
from typing import Dict, List, Optional, Tuple, Set

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ----------------- logging -----------------

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ----------------- config & globals -----------------

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CLEANUP_PASSWORD = os.getenv("CLEANUP_PASSWORD", "")

# имя файла с обычными цитатами из ENV (как в docker-compose)
QUOTES_FILE = os.getenv("QUOTES_FILE", "quotes.txt")

# обычные цитаты (для таймеров и !цитата)
QUOTES: List[str] = []

# цитаты Бань Лу из отдельного файла
BANLU_QUOTES: List[str] = []
BANLU_WOWHEAD_URL = "https://www.wowhead.com/ru/item=142225/бань-лу-спутник-великого-мастера"

# чаты, в которых бот уже что-то делал (для ежедневной рассылки)
KNOWN_CHATS: Set[int] = set()


def load_quotes(path: str) -> None:
    """Load general quotes from a simple text file, one quote per line."""
    global QUOTES
    try:
        with open(path, "r", encoding="utf-8") as f:
            QUOTES = [line.strip() for line in f if line.strip()]
        logger.info("Loaded %d quotes from %s", len(QUOTES), path)
    except FileNotFoundError:
        QUOTES = []
        logger.warning("%s not found, general quotes feature disabled", path)


def load_banlu_quotes(path: str = "quotersbanlu.txt") -> None:
    """Load Ban'lu quotes from file, one per line."""
    global BANLU_QUOTES
    try:
        with open(path, "r", encoding="utf-8") as f:
            BANLU_QUOTES = [line.strip() for line in f if line.strip()]
        logger.info("Loaded %d Ban'lu quotes from %s", len(BANLU_QUOTES), path)
    except FileNotFoundError:
        BANLU_QUOTES = []
        logger.warning("%s not found, Ban'lu feature disabled", path)


def get_random_quote() -> Optional[str]:
    if not QUOTES:
        return None
    return random.choice(QUOTES)


def get_random_banlu_quote() -> Optional[str]:
    if not BANLU_QUOTES:
        return None
    return random.choice(BANLU_QUOTES)


def format_banlu_message(quote: str) -> str:
    """Красивое оформление сообщения Бань Лу."""
    return (
        "🐉 Бань Лу — спутник Великого Мастера\n\n"
        f"💬 {quote}\n\n"
        f"🔗 Подробнее: {BANLU_WOWHEAD_URL}"
    )


def remember_chat(update: Update) -> None:
    """Помнить все чаты, где бот что-то делал (для ежедневной рассылки)."""
    chat = update.effective_chat
    if chat is not None:
        KNOWN_CHATS.add(chat.id)


# ----------------- timer storage -----------------


@dataclass
class TimerEntry:
    chat_id: int
    target_time: datetime  # always in UTC
    pin_message_id: int
    message: Optional[str] = None
    quote: Optional[str] = None
    job_name: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RepeatEntry:
    chat_id: int
    interval: int
    message: Optional[str]
    job_name: str = ""


# chat_id -> list of timers / repeats / pinned messages
TIMERS: Dict[int, List[TimerEntry]] = {}
REPEATS: Dict[int, List[RepeatEntry]] = {}
PINNED_BY_BOT: Dict[int, List[int]] = {}  # chat_id -> [message_ids]


# ----------------- helpers -----------------


def parse_duration(text: str) -> int:
    """
    Parse duration strings like:
    '5' (minutes), '10s', '1h30m', '2h', '90m', '1h15m30s'
    Returns seconds.
    """
    text = text.strip().lower()
    if not text:
        raise ValueError("Empty duration")

    # plain number = minutes
    if text.isdigit():
        minutes = int(text)
        if minutes <= 0:
            raise ValueError("Duration must be > 0")
        return minutes * 60

    total = 0
    number = ""
    for ch in text:
        if ch.isdigit():
            number += ch
            continue

        if not number:
            raise ValueError("Bad duration format")

        value = int(number)
        number = ""

        if ch == "d":
            total += value * 86400
        elif ch == "h":
            total += value * 3600
        elif ch == "m":
            total += value * 60
        elif ch == "s":
            total += value
        else:
            raise ValueError(f"Unknown duration unit: {ch}")

    if number:
        # left-over number with no unit -> minutes
        value = int(number)
        total += value * 60

    if total <= 0:
        raise ValueError("Duration must be > 0")

    return total


def parse_datetime_with_tz(args: List[str]) -> Tuple[datetime, int, int]:
    """
    Parse absolute date/time from args:
    [DD.MM.YYYY, HH:MM, [TZ], ...message_words]

    TZ examples:
      UTC+3, GMT+1, UTC-2, GMT-0

    Returns (target_utc_datetime, msg_start_index, tz_offset_hours)
    Raises ValueError on error.
    """
    if len(args) < 2:
        raise ValueError("Not enough arguments for date/time timer")

    date_str = args[0]
    time_str = args[1]

    try:
        naive = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")
    except ValueError as e:
        raise ValueError("Bad date/time format, use DD.MM.YYYY HH:MM") from e

    tz_offset_hours = 0
    msg_start = 2

    if len(args) >= 3 and (args[2].upper().startswith("UTC") or args[2].upper().startswith("GMT")):
        tz_token = args[2].upper()
        msg_start = 3

        # UTC+3 or GMT-1
        offset_part = tz_token.replace("UTC", "").replace("GMT", "")
        offset_part = offset_part.strip() or "+0"

        sign = 1
        if offset_part.startswith("+"):
            sign = 1
            offset_part = offset_part[1:]
        elif offset_part.startswith("-"):
            sign = -1
            offset_part = offset_part[1:]

        try:
            value = int(offset_part)
        except ValueError as e:
            raise ValueError("Bad timezone format, use UTC+3 / GMT+1") from e

        tz_offset_hours = sign * value

    tz = timezone(timedelta(hours=tz_offset_hours))
    aware = naive.replace(tzinfo=tz)
    target_utc = aware.astimezone(timezone.utc)
    return target_utc, msg_start, tz_offset_hours


def choose_update_interval(seconds_left: int) -> int:
    """
    Smart update intervals:
      > 10m  -> 60s
      3-10m  -> 5s
      1-3m   -> 2s
      < 1m   -> 1s
    """
    if seconds_left > 10 * 60:
        return 60
    if seconds_left > 3 * 60:
        return 5
    if seconds_left > 1 * 60:
        return 2
    return 1


def format_remaining_time(seconds: int) -> str:
    """Format remaining seconds as 'Xd. Yh Zm Ws' (with Russian abbrevs)."""
    if seconds < 0:
        seconds = 0

    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    parts: List[str] = []
    if days:
        parts.append(f"{days} дн.")
    if hours or days:
        parts.append(f"{hours} ч.")
    if minutes or hours or days:
        parts.append(f"{minutes} мин.")
    parts.append(f"{seconds} сек.")

    return " ".join(parts)


def pretty_time_short(seconds: int) -> str:
    """Short representation used in confirmation messages."""
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    if days:
        return f"{days}d {hours}h {minutes}m"
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def remember_pin(chat_id: int, message_id: int) -> None:
    PINNED_BY_BOT.setdefault(chat_id, []).append(message_id)


def remove_timer_entry(chat_id: int, pin_message_id: int) -> None:
    if chat_id not in TIMERS:
        return
    TIMERS[chat_id] = [
        t for t in TIMERS[chat_id] if t.pin_message_id != pin_message_id
    ]
    if not TIMERS[chat_id]:
        del TIMERS[chat_id]


def get_command_args(update: Update, context: ContextTypes.DEFAULT_TYPE) -> List[str]:
    """
    Универсальный парсер аргументов:
    - в приватах/группах используем context.args (CommandHandler уже нарезал);
    - в каналах и на всякий случай парсим текст вручную.
    """
    if getattr(context, "args", None):
        return context.args

    msg = update.effective_message
    if not msg:
        return []

    text = msg.text or msg.caption
    if not text:
        return []

    text = text.strip()
    if not text:
        return []

    parts = text.split()
    if len(parts) <= 1:
        return []
    return parts[1:]


# ----------------- job callbacks -----------------


async def countdown_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    if job is None:
        return

    entry: TimerEntry = job.data
    chat_id = entry.chat_id
    pin_id = entry.pin_message_id

    now_utc = datetime.now(timezone.utc)
    remaining = int((entry.target_time - now_utc).total_seconds())

    if remaining <= 0:
        # Final update and notify
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=pin_id,
                text="⏰ Time is up!",
            )
        except Exception as e:
            logger.warning("Failed to edit final countdown message: %s", e)

        try:
            await context.bot.send_message(chat_id=chat_id, text="⏰ Time is up!")
        except Exception as e:
            logger.warning("Failed to send 'Time is up' message: %s", e)

        remove_timer_entry(chat_id, pin_id)
        return

    # Build updated text
    text_lines = [f"⏰ Time left: {format_remaining_time(remaining)}"]

    if entry.message:
        text_lines.append(entry.message)

    if entry.quote:
        text_lines.append(f"💬 {entry.quote}")

    new_text = "\n".join(text_lines)

    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=pin_id,
            text=new_text,
        )
    except Exception as e:
        logger.warning("Cannot edit countdown message: %s", e)

    # schedule next tick with smart interval
    delay = choose_update_interval(remaining)
    context.job_queue.run_once(
        countdown_tick,
        delay,
        data=entry,
        name=entry.job_name,
    )


async def repeat_tick(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    if job is None:
        return
    entry: RepeatEntry = job.data
    text = entry.message or f"⏰ Repeat timer: {pretty_time_short(entry.interval)}"
    try:
        await context.bot.send_message(chat_id=entry.chat_id, text=text)
    except Exception as e:
        logger.warning("Failed to send repeat timer message: %s", e)


async def banlu_daily_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ежедневная автоматическая цитата Бань Лу для всех известных чатов."""
    if not KNOWN_CHATS:
        return

    quote = get_random_banlu_quote()
    if not quote:
        logger.warning("No Ban'lu quotes loaded, daily job skipped")
        return

    text = format_banlu_message(quote)

    for chat_id in list(KNOWN_CHATS):
        try:
            await context.bot.send_message(chat_id=chat_id, text=text)
        except Exception as e:
            logger.warning("Failed to send daily Ban'lu quote to %s: %s", chat_id, e)


# ----------------- command handlers -----------------


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    remember_chat(update)
    msg = update.effective_message
    if msg is None:
        return

    await msg.reply_text(
        "Hello! I am timer bot.\n"
        "Use /timer 5 (5 minutes)\n"
        "Use /timer 10s (10 seconds)\n"
        "Use /help for all commands."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    remember_chat(update)
    msg = update.effective_message
    if msg is None:
        return

    text = (
        "Commands:\n"
        "/timer <time> [message] - one-time timer with pinned countdown\n"
        "Duration formats:\n"
        "  /timer 5        (5 minutes)\n"
        "  /timer 10s      (10 seconds)\n"
        "  /timer 1h30m    (1 hour 30 minutes)\n"
        "\n"
        "Absolute date/time:\n"
        "  /timer DD.MM.YYYY HH:MM [TZ] [message]\n"
        "  examples:\n"
        "    /timer 01.01.2026 00:00 \\\"Happy New Year\\\"\n"
        "    /timer 01.01.2026 00:00 GMT+1 \\\"Happy New Year\\\"\n"
        "    /timer 01.01.2026 00:00 UTC+3 Raid pull\n"
        "\n"
        "Smart updates:\n"
        "  >10m  -> update once per minute\n"
        "  3-10m -> every 5s\n"
        "  1-3m  -> every 2s\n"
        "  <1m   -> every 1s\n"
        "\n"
        "/repeat <time> [message] - repeat timer (no pin)\n"
        "/cancel - stop all one-time timers\n"
        "/cancelrepeat - stop all repeat timers\n"
        "/timers - show active timers\n"
        "/clearpins <password> - remove pins created by this bot (this chat)\n"
        "\n"
        "!цитата - send random quote from quotes.txt\n"
        "/banlu  - random Ban'lu quote (quotersbanlu.txt)\n"
        "Every day at 10:00 MSK Ban'lu quote is sent to all known chats.\n"
    )
    await msg.reply_text(text)


async def timer_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    remember_chat(update)
    msg = update.effective_message
    if msg is None:
        return

    args = get_command_args(update, context)
    if not args:
        await msg.reply_text("Usage: /timer <time> [message]")
        return

    chat_id = update.effective_chat.id
    now_utc = datetime.now(timezone.utc)

    try:
        # absolute date/time if first arg looks like DD.MM.YYYY and second like HH:MM
        if len(args) >= 2 and "." in args[0] and ":" in args[1]:
            target_time_utc, msg_start, _tz = parse_datetime_with_tz(args)
            remaining = int((target_time_utc - now_utc).total_seconds())
            if remaining <= 0:
                await msg.reply_text("Target time must be in the future.")
                return
            message = " ".join(args[msg_start:]).strip()
        else:
            duration_seconds = parse_duration(args[0])
            target_time_utc = now_utc + timedelta(seconds=duration_seconds)
            remaining = duration_seconds
            message = " ".join(args[1:]).strip()
    except ValueError as e:
        await msg.reply_text(f"Bad format: {e}")
        return

    if message:
        message = message.strip('"')

    # choose quote ONCE for this timer
    quote = get_random_quote()

    # initial pinned message
    text_lines = [f"⏰ Time left: {format_remaining_time(remaining)}"]
    if message:
        text_lines.append(message)
    if quote:
        text_lines.append(f"💬 {quote}")

    pin_text = "\n".join(text_lines)

    sent = await context.bot.send_message(chat_id=chat_id, text=pin_text)
    await context.bot.pin_chat_message(
        chat_id=chat_id,
        message_id=sent.message_id,
        disable_notification=True,
    )
    remember_pin(chat_id, sent.message_id)

    # store timer
    job_name = f"timer-{chat_id}-{sent.message_id}"
    entry = TimerEntry(
        chat_id=chat_id,
        target_time=target_time_utc,
        pin_message_id=sent.message_id,
        message=message or None,
        quote=quote,
        job_name=job_name,
    )
    TIMERS.setdefault(chat_id, []).append(entry)

    delay = choose_update_interval(remaining)
    context.application.job_queue.run_once(
       countdown_tick,
        delay,
        data=entry,
        name=job_name,
    )

    await msg.reply_text(f"⏰ Timer set for {pretty_time_short(remaining)}.")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    remember_chat(update)
    msg = update.effective_message
    if msg is None:
        return

    chat_id = update.effective_chat.id
    if chat_id not in TIMERS or not TIMERS[chat_id]:
        await msg.reply_text("No timers to cancel.")
        return

    for entry in TIMERS[chat_id]:
        jobs = context.application.job_queue.get_jobs_by_name(entry.job_name)
        for job in jobs:
            job.schedule_removal()

    TIMERS.pop(chat_id, None)
    await msg.reply_text("✅ All one-time timers cancelled.")


async def repeat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    remember_chat(update)
    msg = update.effective_message
    if msg is None:
        return

    args = get_command_args(update, context)
    if not args:
        await msg.reply_text("Usage: /repeat <time> [message]")
        return

    chat_id = update.effective_chat.id
    try:
        interval = parse_duration(args[0])
    except ValueError as e:
        await msg.reply_text(f"Bad format: {e}")
        return

    message = " ".join(args[1:]).strip() or None
    job_name = f"repeat-{chat_id}-{len(REPEATS.get(chat_id, [])) + 1}"

    entry = RepeatEntry(
        chat_id=chat_id,
        interval=interval,
        message=message,
        job_name=job_name,
    )
    REPEATS.setdefault(chat_id, []).append(entry)

    context.application.job_queue.run_repeating(
        repeat_tick,
        interval=interval,
        first=interval,
        name=job_name,
        data=entry,
    )

    await msg.reply_text(
        f"🔁 Repeat timer set every {pretty_time_short(interval)}."
    )


async def cancel_repeat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    remember_chat(update)
    msg = update.effective_message
    if msg is None:
        return

    chat_id = update.effective_chat.id
    if chat_id not in REPEATS or not REPEATS[chat_id]:
        await msg.reply_text("No repeat timers to cancel.")
        return

    for entry in REPEATS[chat_id]:
        jobs = context.application.job_queue.get_jobs_by_name(entry.job_name)
        for job in jobs:
            job.schedule_removal()

    REPEATS.pop(chat_id, None)
    await msg.reply_text("✅ All repeat timers cancelled.")


async def timers_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    remember_chat(update)
    msg = update.effective_message
    if msg is None:
        return

    chat_id = update.effective_chat.id
    one_time = len(TIMERS.get(chat_id, []))
    repeats = len(REPEATS.get(chat_id, []))
    await msg.reply_text(
        f"⏱ One-time timers: {one_time}\n"
        f"🔁 Repeating timers: {repeats}"
    )


async def clear_pins_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    remember_chat(update)
    msg = update.effective_message
    if msg is None:
        return

    args = get_command_args(update, context)
    if not args:
        await msg.reply_text("Usage: /clearpins <password>")
        return

    password = args[0]
    if not CLEANUP_PASSWORD or password != CLEANUP_PASSWORD:
        await msg.reply_text("❌ Wrong password.")
        return

    chat_id = update.effective_chat.id
    total_removed = 0

    # only this chat's pins
    if chat_id in PINNED_BY_BOT:
        ids = PINNED_BY_BOT[chat_id]
        for mid in ids:
            try:
                await context.bot.unpin_chat_message(chat_id=chat_id, message_id=mid)
                total_removed += 1
            except Exception as e:
                logger.warning(
                    "Failed to unpin message %s in chat %s: %s", mid, chat_id, e
                )
        PINNED_BY_BOT[chat_id] = []

    await msg.reply_text(f"✅ Removed {total_removed} pins in this chat.")


async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    remember_chat(update)
    msg = update.effective_message
    if msg is None:
        return

    quote = get_random_quote()
    if not quote:
        await msg.reply_text("Цитаты не найдены 🤷‍♂️")
        return

    await msg.reply_text(f"💬 {quote}")


async def banlu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ручная команда проверки цитаты Бань Лу."""
    remember_chat(update)
    msg = update.effective_message
    if msg is None:
        return

    quote = get_random_banlu_quote()
    if not quote:
        await msg.reply_text("Цитаты Бань Лу не найдены 🤷‍♂️")
        return

    await msg.reply_text(format_banlu_message(quote))


# ----------------- main -----------------


def main() -> None:
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN env var is not set")

    load_quotes(QUOTES_FILE)
    load_banlu_quotes()

    app = ApplicationBuilder().token(TOKEN).build()

    # фильтры по типам чатов
    priv_or_groups = filters.ChatType.PRIVATE | filters.ChatType.GROUPS
    channels = filters.ChatType.CHANNEL

    # команды в приватах и группах — через CommandHandler
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
    app.add_handler(CommandHandler("banlu", banlu_command, filters=priv_or_groups))

    # те же команды в КАНАЛАХ — ловим как текст через Regex
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

    # !цитата — простой текст во всех типах чатов
    app.add_handler(
        MessageHandler(
            filters.Regex(r"^!цитата\b"),
            quote_command,
        )
    )

    # Ежедневная цитата Бань Лу в 10:00 по Москве (UTC+3)
    msk_tz = timezone(timedelta(hours=3))
    app.job_queue.run_daily(
        banlu_daily_job,
        time=time(hour=10, minute=0, tzinfo=msk_tz),
        name="banlu_daily",
    )

    app.run_polling()


if __name__ == "__main__":
    main()