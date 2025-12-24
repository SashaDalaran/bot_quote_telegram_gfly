# ==================================================
# services/holidays_format.py — Holidays Message Formatter
# ==================================================

from typing import List, Dict, Any
from services.holidays_flags import COUNTRY_FLAGS, CATEGORY_EMOJIS

Holiday = Dict[str, Any]


def _normalize_key(value: Any) -> str:
    """
    Normalize keys for lookup:
    - Fix Cyrillic 'С/с' -> Latin 'C/c'
    - lowercase
    - snake_case
    - '&' -> 'and'
    """
    if not isinstance(value, str):
        return ""

    s = value.strip()
    s = s.replace("С", "C").replace("с", "c")  # critical fix
    s = s.replace("&", "and")
    s = s.lower()

    # snake_case without regex (no extra deps)
    out = []
    prev_us = False
    for ch in s:
        if ch.isalnum():
            out.append(ch)
            prev_us = False
        else:
            if not prev_us:
                out.append("_")
                prev_us = True

    key = "".join(out).strip("_")

    # collapse multiple underscores
    while "__" in key:
        key = key.replace("__", "_")

    return key


def _as_list(obj: Holiday, *keys: str) -> List[str]:
    """Fetch list[str] from obj by keys; supports list or single string."""
    for k in keys:
        v = obj.get(k)
        if isinstance(v, list):
            return [str(x) for x in v if str(x).strip()]
    for k in keys:
        v = obj.get(k)
        if isinstance(v, str) and v.strip():
            return [v.strip()]
    return []


def format_holidays_message(holidays: List[Holiday]) -> str:
    lines: List[str] = ["🎉 Today’s Holidays", ""]

    for holiday in holidays:
        name = str(holiday.get("name", "—"))

        # support both "categories" and "category"
        categories = _as_list(holiday, "categories", "category")
        countries = _as_list(holiday, "countries", "country")

        # Country flag (first only)
        if countries:
            country_raw = countries[0]
            flag = COUNTRY_FLAGS.get(_normalize_key(country_raw), "🌍")
        else:
            flag = "🌍"

        lines.append(f"{flag} {name}")

        # Category emoji (first only)
        if categories:
            category_raw = categories[0]
            emoji = CATEGORY_EMOJIS.get(_normalize_key(category_raw), "🔖")
            # Keep the original label for readability (still English in your datasets)
            lines.append(f"{emoji} {category_raw}")

        lines.append("")

    return "\n".join(lines).strip()
