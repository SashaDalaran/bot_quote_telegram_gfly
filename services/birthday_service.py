import json
import os
import re
from datetime import date
from typing import Any, Dict, List, Optional, Tuple


def _birthday_file_path() -> str:
    # project root at runtime => data/birthday.json
    return os.path.join("data", "birthday.json")


def _strip_loose_json_list(text: str) -> str:
    """Turn a 'loose JSON' list into valid JSON.

    Accepts files like:
      # comment
      { ... },
      { ... },

    i.e. no surrounding [] and optional trailing commas.
    """
    # Remove full-line comments and empty lines
    lines: List[str] = []
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            continue
        if not line.strip():
            continue
        lines.append(line)

    cleaned = "\n".join(lines).strip()
    if not cleaned:
        return "[]"

    # If it's not already a JSON array, wrap it.
    if not cleaned.lstrip().startswith("["):
        cleaned = "[\n" + cleaned + "\n]"

    # Remove trailing commas before array close
    cleaned = re.sub(r",\s*\]", "]", cleaned)
    # Also remove trailing commas at EOF (just in case)
    cleaned = re.sub(r",\s*$", "", cleaned)
    return cleaned


def load_birthday_events(path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load events from data/birthday.json.

    Expected per-item schema (same spirit as holidays JSON):
      {
        "date": "MM-DD" | "MM-DD:MM-DD",
        "name": str,
        "category": [str, ...],
        "countries": [str, ...]
      }
    """
    path = path or _birthday_file_path()
    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    try:
        data = json.loads(_strip_loose_json_list(raw))
    except Exception:
        # If something is off, fail safe (no crash of the bot)
        return []

    if not isinstance(data, list):
        return []

    out: List[Dict[str, Any]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        if not item.get("date") or not item.get("name"):
            continue
        # Ensure lists exist
        item.setdefault("category", [])
        item.setdefault("countries", [])
        out.append(item)
    return out


def _parse_mmdd(mmdd: str) -> Optional[Tuple[int, int]]:
    mmdd = mmdd.strip()
    if not re.fullmatch(r"\d{2}-\d{2}", mmdd):
        return None
    m, d = mmdd.split("-")
    month = int(m)
    day = int(d)
    if not (1 <= month <= 12 and 1 <= day <= 31):
        return None
    return month, day


def _to_doy(month: int, day: int) -> int:
    # Use a non-leap year anchor.
    return date(2001, month, day).timetuple().tm_yday


def _is_today_in_range(today_mmdd: str, start_mmdd: str, end_mmdd: str) -> bool:
    t = _parse_mmdd(today_mmdd)
    s = _parse_mmdd(start_mmdd)
    e = _parse_mmdd(end_mmdd)
    if not t or not s or not e:
        return False

    t_doy = _to_doy(*t)
    s_doy = _to_doy(*s)
    e_doy = _to_doy(*e)

    if s_doy <= e_doy:
        return s_doy <= t_doy <= e_doy
    # Wraps over New Year: e.g. 12-19:01-20
    return (t_doy >= s_doy) or (t_doy <= e_doy)


def event_active_on(event_date: str, today: Optional[date] = None) -> bool:
    today = today or date.today()
    today_mmdd = today.strftime("%m-%d")
    event_date = (event_date or "").strip()

    if ":" in event_date:
        start, end = [p.strip() for p in event_date.split(":", 1)]
        return _is_today_in_range(today_mmdd, start, end)
    return event_date == today_mmdd


def _norm_cat(cat: str) -> str:
    # Handle Cyrillic 'С' in 'Сhallenge'
    return (cat or "").strip().lower().replace("с", "c")


def _event_kind(event: Dict[str, Any]) -> str:
    """Map an event to one of the 3 user-facing buckets.

    Rules tuned to your chosen file format:
      1) Date range ("MM-DD:MM-DD") => either challenge or hero.
         - If category contains 'challenge' (incl. Cyrillic 'Сhallenge') => challenges
         - Otherwise => heroes
      2) Single date ("MM-DD") => birthdays
    """

    date_str = str(event.get("date", ""))
    is_range = ":" in date_str

    cats = event.get("category") or []
    if isinstance(cats, str):
        cats = [cats]
    norm = {_norm_cat(c) for c in cats if isinstance(c, str)}

    if is_range:
        return "challenges" if "challenge" in norm else "heroes"
    return "birthdays"


def get_today_birthday_payload(today: Optional[date] = None) -> Dict[str, List[Dict[str, Any]]]:
    """Return payload grouped into: challenges, heroes, birthdays."""
    today = today or date.today()
    events = load_birthday_events()

    payload: Dict[str, List[Dict[str, Any]]] = {
        "challenges": [],
        "heroes": [],
        "birthdays": [],
    }

    for ev in events:
        if not event_active_on(str(ev.get("date", "")), today=today):
            continue
        kind = _event_kind(ev)
        payload.setdefault(kind, []).append(ev)

    return payload
