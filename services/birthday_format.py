import html
import re
from datetime import date
from typing import Dict, List, Optional, Tuple

# This module formats the "Guild events" daily message (challenges / heroes / birthdays).


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
        return f"{months[m_i-1]} {d_i}"
    except Exception:
        return mmdd


def _range_label(date_str: str) -> str:
    """'12-19:01-20' -> 'Dec 19–Jan 20' """
    if ":" not in date_str:
        return _md_to_human(date_str)
    start, end = date_str.split(":", 1)
    return f"{_md_to_human(start)}–{_md_to_human(end)}"


def _parse_mmdd(mmdd: str) -> Optional[Tuple[int, int]]:
    try:
        m, d = mmdd.split("-")
        return int(m), int(d)
    except Exception:
        return None


def _resolve_range_to_dates(date_str: str, today: date) -> Optional[Tuple[date, date]]:
    """Resolve a MM-DD:MM-DD range to concrete dates around 'today'.

    Handles year wrap (e.g. Dec->Jan).
    """
    if ":" not in date_str:
        return None
    start_s, end_s = date_str.split(":", 1)
    s = _parse_mmdd(start_s)
    e = _parse_mmdd(end_s)
    if not s or not e:
        return None

    sm, sd = s
    em, ed = e

    # Non-wrapping within the same year (e.g. Mar->Apr)
    if (sm, sd) <= (em, ed):
        start = date(today.year, sm, sd)
        end = date(today.year, em, ed)
        return start, end

    # Wrapping over new year (e.g. Dec->Jan)
    if (today.month, today.day) >= (sm, sd):
        start = date(today.year, sm, sd)
        end = date(today.year + 1, em, ed)
    else:
        start = date(today.year - 1, sm, sd)
        end = date(today.year, em, ed)
    return start, end


def _normalize_text(text: str) -> str:
    """Cosmetic normalizer for short status strings."""
    t = " ".join(str(text).split())
    # 4 К / 4 K -> 4К / 4K
    t = re.sub(r"(\d)\s*([KК])\b", r"\1\2", t)
    return t


def _ru_days(n: int) -> str:
    n = abs(int(n))
    if 11 <= (n % 100) <= 14:
        return "дней"
    last = n % 10
    if last == 1:
        return "день"
    if 2 <= last <= 4:
        return "дня"
    return "дней"


def _progress(today: date, start: date, end: date) -> Tuple[int, int, int]:
    """Return (day_number, total_days, remaining_days_excluding_today)."""
    total = (end - start).days + 1
    day_num = (today - start).days + 1
    remaining = (end - today).days
    # Guard against weird off-range math if called outside the interval
    if day_num < 1:
        day_num = 1
    if day_num > total:
        day_num = total
    if remaining < 0:
        remaining = 0
    return day_num, total, remaining


def _split_owner_task(name: str) -> Tuple[str, str]:
    """Best-effort split: 'OWNER - TASK' or 'OWNER TASK...'"""
    raw = _normalize_text(name)
    # dash variants
    for sep in [" - ", " — ", " – "]:
        if sep in raw:
            left, right = raw.split(sep, 1)
            return left.strip(), right.strip()
    parts = raw.split(" ", 1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return raw.strip(), ""


def _extract_role(text: str) -> Tuple[str, str]:
    """Extract first @role token from text."""
    parts = text.split()
    role = ""
    kept = []
    for p in parts:
        if not role and p.startswith("@"):
            role = p
            continue
        kept.append(p)
    return role, " ".join(kept).strip()


def format_birthday_message(payload: Dict[str, List[dict]], today: Optional[date] = None) -> str:
    """Format 'Guild events' message from payload produced by services.birthday_service."""
    if today is None:
        today = date.today()

    header = today.strftime("%d %b")
    lines: List[str] = [f"📅 <b>Guild events — {html.escape(header)}</b>", ""]

    # --- Challenges ---
    challenges = payload.get("challenges") or []
    if challenges:
        lines.append("🏆 <b>Guild Challenge</b>")
        for i, ev in enumerate(challenges):
            name = _normalize_text(ev.get("name", ""))
            owner, task = _split_owner_task(name)
            owner = html.escape(owner)
            task = html.escape(task) if task else ""

            lines.append(f"⚡️ {owner}")
            if task:
                lines.append(f"↳ ⚡️ {task}")

            date_str = str(ev.get("date", "")).strip()
            label = html.escape(_range_label(date_str))
            lines.append(f"↳ интервал челенджа 🗓️ {label}")

            resolved = _resolve_range_to_dates(date_str, today)
            if resolved:
                start, end = resolved
                day_num, total, remaining = _progress(today, start, end)
                lines.append(
                    f"↳ Сейчас идёт день {day_num} из {total} — осталось {remaining} {_ru_days(remaining)}"
                )

            if i != len(challenges) - 1:
                lines.append("")
        lines.append("")  # space after section

    # --- Heroes ---
    heroes = payload.get("heroes") or []
    if heroes:
        lines.append("🦸 <b>Heroes</b>")
        for i, ev in enumerate(heroes):
            name = _normalize_text(ev.get("name", ""))
            role, cleaned = _extract_role(name)
            who, desc = _split_owner_task(cleaned)
            who = html.escape(who)
            desc = html.escape(desc) if desc else ""

            lines.append(f"🤡 {who}")
            if desc:
                lines.append(f"↳ 💩 {desc}")

            date_str = str(ev.get("date", "")).strip()
            label = html.escape(_range_label(date_str))
            role_part = f"в роли {html.escape(role)} " if role else ""
            lines.append(f"↳ Промежуток отбывания {role_part}🗓️ {label}")

            resolved = _resolve_range_to_dates(date_str, today)
            if resolved:
                start, end = resolved
                day_num, total, remaining = _progress(today, start, end)
                lines.append(
                    f"↳ Осталось {remaining} {_ru_days(remaining)} (день {day_num} из {total})"
                )

            if i != len(heroes) - 1:
                lines.append("")
        lines.append("")  # space after section

    # --- Birthdays ---
    birthdays = payload.get("birthdays") or []
    if birthdays:
        lines.append("🎂 <b>Birthdays</b>")
        for i, ev in enumerate(birthdays):
            name = html.escape(str(ev.get("name", "")).strip())
            lines.append(f"🥳 {name}")
            # Optional murloc flavour line (if the event marks Murloc)
            countries = [str(x) for x in (ev.get("countries") or [])]
            if any(c.lower() == "murloc" for c in countries):
                lines.append("🐸 Mrgl Mrgl!")
            if i != len(birthdays) - 1:
                lines.append("")
        lines.append("")  # space after section

    # Clean up trailing empty lines
    while lines and lines[-1] == "":
        lines.pop()

    return "\n".join(lines)
