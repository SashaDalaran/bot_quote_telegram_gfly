# ==================================================
# services/birthday_format.py — Guild Events Formatter
# ==================================================
#
# Formats "Guild events" message (Challenges / Heroes / Birthdays)
# into a Telegram-friendly text block.
#
# Rules requested by user:
# - All emojis (except section headings 🏆 / 🦸) must come from
#   services/holidays_flags.py mappings.
# - No emoji de-duplication: if data provides both "category" and
#   "countries" tokens, we intentionally use both.
# - Show progress for ranged events:
#   remaining days + "day X of N".
#
# ==================================================

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Tuple

from services.birthday_service import _norm_token  # reuse normalization (avoid duplicates)
from services.holidays_flags import CATEGORY_EMOJIS, COUNTRY_FLAGS, UI_EMOJIS


# ------------------------------
# Date helpers
# ------------------------------

_MONTH_ABBR = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}


def _format_short_date(d: date) -> str:
    return f"{d.day:02d} {_MONTH_ABBR[d.month]}"


def _format_range(start: date, end: date) -> str:
    # Example: Dec 19–Jan 20
    return f"{_MONTH_ABBR[start.month]} {start.day}–{_MONTH_ABBR[end.month]} {end.day}"


def _ru_days_word(n: int) -> str:
    # день / дня / дней
    n = abs(int(n))
    if 11 <= (n % 100) <= 14:
        return "дней"
    last = n % 10
    if last == 1:
        return "день"
    if 2 <= last <= 4:
        return "дня"
    return "дней"


@dataclass(frozen=True)
class RangeProgress:
    start: date
    end: date
    day_index: int
    total_days: int
    remaining_days: int


def _range_dates(date_str: str, today: date) -> Optional[Tuple[date, date]]:
    """Parse 'MM-DD:MM-DD' into actual start/end dates around 'today'.

    Handles year wrap (e.g. 12-19:01-20).
    """
    if ":" not in date_str:
        return None

    start_str, end_str = date_str.split(":", 1)
    sm, sd = map(int, start_str.split("-"))
    em, ed = map(int, end_str.split("-"))

    wraps = (em, ed) < (sm, sd)

    # choose a year so that today is inside the window
    if wraps:
        if today.month > sm or (today.month == sm and today.day >= sd):
            start_y = today.year
            end_y = today.year + 1
        else:
            start_y = today.year - 1
            end_y = today.year
    else:
        start_y = today.year
        end_y = today.year

    return date(start_y, sm, sd), date(end_y, em, ed)


def _range_progress(date_str: str, today: date) -> Optional[RangeProgress]:
    rng = _range_dates(date_str, today)
    if not rng:
        return None

    start, end = rng
    if not (start <= today <= end):
        return None

    day_index = (today - start).days + 1
    total_days = (end - start).days + 1
    remaining_days = total_days - day_index

    return RangeProgress(
        start=start,
        end=end,
        day_index=day_index,
        total_days=total_days,
        remaining_days=remaining_days,
    )


# ------------------------------
# Emoji resolvers
# ------------------------------


def _first_token(values: List[str]) -> str:
    return values[0] if values else ""


def _emoji_for_category(categories: List[str]) -> str:
    key = _norm_token(_first_token(categories))
    return CATEGORY_EMOJIS.get(key, "")


def _emoji_for_country(countries: List[str]) -> str:
    key = _norm_token(_first_token(countries))
    return COUNTRY_FLAGS.get(key, "")


# ------------------------------
# Name parsing
# ------------------------------


def _split_owner_task(name: str) -> Tuple[str, str]:
    """Challenge line: 'OWNER TASK...' -> ('OWNER', 'TASK...')."""
    parts = name.strip().split()
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:]).replace("  ", " ")


def _split_owner_desc(name: str) -> Tuple[str, str]:
    """Hero line: 'OWNER - desc' or 'OWNER desc' -> ('OWNER', 'desc')."""
    s = name.strip()
    if " - " in s:
        left, right = s.split(" - ", 1)
        return left.strip(), right.strip()
    if "-" in s:
        left, right = s.split("-", 1)
        return left.strip(), right.strip()
    parts = s.split()
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:]).strip()


# ------------------------------
# Public API
# ------------------------------


def format_birthday_message(payload: Dict[str, Any], today: date) -> str:
    """Render a single message for the 'Guild events' channel."""

    title = payload.get("title", "Guild events")
    challenges: List[Dict[str, Any]] = payload.get("challenges", [])
    heroes: List[Dict[str, Any]] = payload.get("heroes", [])
    birthdays: List[Dict[str, Any]] = payload.get("birthdays", [])

    cal = UI_EMOJIS.get("guild_events_header", "📅")
    cake = UI_EMOJIS.get("birthdays_header", "🎂")
    range_emoji = UI_EMOJIS.get("date_range", "🗓️")

    lines: List[str] = []
    lines.append(f"{cal} {title} — {_format_short_date(today)}")
    lines.append("")

    # -------------------
    # Guild Challenge
    # -------------------
    lines.append("🏆 Guild Challenge")
    if not challenges:
        lines.append("↳ челленджей нет")
    else:
        for ev in challenges:
            name = str(ev.get("name", "")).strip()
            categories = ev.get("category", []) or []
            countries = ev.get("countries", []) or []

            owner, task = _split_owner_task(name)
            owner_emoji = _emoji_for_country(countries)
            task_emoji = _emoji_for_category(categories)

            if owner:
                lines.append(f"{owner_emoji} {owner}".strip())
            if task:
                lines.append(f"↳ {task_emoji} {task}".strip())

            prog = _range_progress(str(ev.get("date", "")), today)
            if prog:
                lines.append(f"↳ интервал челенджа {range_emoji} {_format_range(prog.start, prog.end)}")
                lines.append(
                    f"↳ Сейчас идет {prog.day_index}-й день челенджа, осталось {prog.remaining_days} {_ru_days_word(prog.remaining_days)} "
                    f"(день {prog.day_index} из {prog.total_days})"
                )
            lines.append("")

    # -------------------
    # Heroes
    # -------------------
    lines.append("🦸 Heroes")
    if not heroes:
        lines.append("↳ герои не найдены")
    else:
        for ev in heroes:
            name = str(ev.get("name", "")).strip()
            categories = ev.get("category", []) or []
            countries = ev.get("countries", []) or []

            hero, _desc = _split_owner_desc(name)
            hero_emoji = _emoji_for_country(countries)
            status_emoji = _emoji_for_category(categories)

            if hero:
                lines.append(f"{hero_emoji} {hero}".strip())
            # This phrase is intentionally normalized for the 'accept/complete' hero format
            lines.append(f"↳ {status_emoji} Челлендж принят, но не выполнен".strip())

            prog = _range_progress(str(ev.get("date", "")), today)
            if prog:
                lines.append(
                    f"↳ Промежуток отбывания в роли @ПЕДРИЛЛА {range_emoji} {_format_range(prog.start, prog.end)}"
                )
                lines.append(
                    f"↳ осталось в роли @ПЕДРИЛЛА {prog.remaining_days} {_ru_days_word(prog.remaining_days)} "
                    f"(день {prog.day_index} из {prog.total_days})"
                )
            lines.append("")

    # -------------------
    # Birthdays
    # -------------------
    lines.append(f"{cake} Birthdays")
    if not birthdays:
        lines.append("↳ дни рождения не найдены")
    else:
        for ev in birthdays:
            name = str(ev.get("name", "")).strip()
            categories = ev.get("category", []) or []
            countries = ev.get("countries", []) or []

            cat_emoji = _emoji_for_category(categories)
            flag_emoji = _emoji_for_country(countries)
            country_key = _norm_token(_first_token(countries))

            lines.append(f"{cat_emoji} {name}".strip())
            if country_key == "murloc":
                lines.append(f"{flag_emoji} Mrgl Mrgl!")
            else:
                lines.append(f"{flag_emoji} {country_key}".strip())

    # Trim trailing blanks
    while lines and lines[-1] == "":
        lines.pop()

    return "\n".join(lines)
