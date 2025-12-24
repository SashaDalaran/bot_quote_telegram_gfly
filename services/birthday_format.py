import html
from datetime import date
from typing import Dict, List, Optional

from services.holidays_flags import CATEGORY_EMOJIS, COUNTRY_FLAGS


# Common Cyrillic lookalikes that can sneak into tags like "Сhallenge".
_CYR_TO_LAT = str.maketrans({
    "С": "C",
    "с": "c",
    "О": "O",
    "о": "o",
    "А": "A",
    "а": "a",
    "Е": "E",
    "е": "e",
    "Р": "P",
    "р": "p",
    "Н": "H",
    "н": "h",
    "К": "K",
    "к": "k",
    "Т": "T",
    "т": "t",
    "М": "M",
    "м": "m",
    "В": "B",
    "в": "b",
    "Х": "X",
    "х": "x",
})


def _norm_token(value: str) -> str:
    s = str(value).strip().translate(_CYR_TO_LAT)
    s = " ".join(s.split())
    return s.lower()


def _md_to_human(mmdd: str) -> str:
    """Convert MM-DD to 'Mon DD' (English short) without a year."""
    months = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]
    try:
        m, d = mmdd.split("-")
        m_i = int(m)
        d_i = int(d)
        if 1 <= m_i <= 12 and 1 <= d_i <= 31:
            return f"{months[m_i - 1]} {d_i}"
    except Exception:
        pass
    return mmdd


def _range_label(date_str: str) -> str:
    if ":" not in date_str:
        return ""
    start, end = date_str.split(":", 1)
    return f"{_md_to_human(start)}–{_md_to_human(end)}"


def _emojize(values: List[str], mapping: Dict[str, str]) -> str:
    out = []
    for v in values or []:
        key = _norm_token(v)
        emoji = mapping.get(key)
        if emoji:
            out.append(emoji)
    return "".join(out)


def _event_line(ev: dict) -> str:
    name = html.escape(str(ev.get("name", ""))).strip()
    categories = ev.get("category") or []
    countries = ev.get("countries") or []

    cat_emoji = _emojize([str(c) for c in categories], CATEGORY_EMOJIS)
    country_emoji = _emojize([str(c) for c in countries], COUNTRY_FLAGS)

    # Avoid ugly duplicates like "⚡️⚡️" when both maps resolve to the same emoji.
    if cat_emoji and country_emoji:
        prefix = cat_emoji if cat_emoji == country_emoji else f"{cat_emoji}{country_emoji}"
    else:
        prefix = cat_emoji or country_emoji
    prefix = f"{prefix} ".strip()

    date_str = str(ev.get("date", ""))
    rng = _range_label(date_str)
    suffix = f" <i>({html.escape(rng)})</i>" if rng else ""

    # Bullet style aligned with other daily messages
    if prefix:
        return f"• {prefix} <b>{name}</b>{suffix}"
    return f"• <b>{name}</b>{suffix}"


def format_birthday_message(payload: dict, today: Optional[date] = None) -> str:
    """Create a single message with 3 sections:

    - Guild Challenges (range events)
    - Heroes (range events)
    - Guild Birthdays (single-day)
    """
    today = today or date.today()
    date_header = today.strftime("%d %b")

    challenges = payload.get("challenges", []) or []
    heroes = payload.get("heroes", []) or []
    birthdays = payload.get("birthdays", []) or []

    if not (challenges or heroes or birthdays):
        return f"📅 <b>Guild events — {date_header}</b>\n\nNo events for today."

    parts: List[str] = [f"📅 <b>Guild events — {date_header}</b>"]

    if challenges:
        parts.append("\n🏆 <b>Guild Challenge</b>")
        parts.extend(_event_line(ev) for ev in challenges)

    if heroes:
        parts.append("\n🦸 <b>Heroes</b>")
        parts.extend(_event_line(ev) for ev in heroes)

    if birthdays:
        parts.append("\n🎂 <b>Birthdays</b>")
        parts.extend(_event_line(ev) for ev in birthdays)

    return "\n".join(parts).strip()
