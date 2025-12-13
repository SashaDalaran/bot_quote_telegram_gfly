# ==================================================
# services/holidays_service.py
# ==================================================

import json
import logging
from datetime import date, datetime
from pathlib import Path
from typing import List, Dict

from core.dynamic_holidays import get_dynamic_holidays

logger = logging.getLogger(__name__)

Holiday = Dict[str, object]
HOLIDAYS_PATH = Path("data/holidays")


def load_static_holidays(today: date) -> List[Holiday]:
    holidays: List[Holiday] = []

    if not HOLIDAYS_PATH.exists():
        logger.warning("Holidays folder not found: %s", HOLIDAYS_PATH)
        return holidays

    for file in sorted(HOLIDAYS_PATH.glob("*.json")):
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
        except Exception:
            logger.exception("Failed to read %s", file)
            continue

        for entry in data:
            mmdd = entry.get("date")
            if not mmdd:
                continue

            parsed = datetime.strptime(
                f"{today.year}-{mmdd}", "%Y-%m-%d"
            ).date()

            if parsed < today:
                parsed = parsed.replace(year=today.year + 1)

            holidays.append(
                {
                    "name": entry["name"],
                    "date": mmdd,
                    "parsed_date": parsed,
                    "countries": entry.get("countries", []),
                    "categories": entry.get("category") or entry.get("categories") or [],
                    "source": file.name,
                }
            )

    return holidays


def load_all_holidays(today: date | None = None) -> List[Holiday]:
    if today is None:
        today = date.today()

    holidays = load_static_holidays(today)

    for d in get_dynamic_holidays():
        holidays.append(
            {
                "name": d["name"],
                "date": d["date"],
                "parsed_date": datetime.strptime(
                    d["full_date"], "%Y-%m-%d"
                ).date(),
                "countries": d.get("countries", []),
                "categories": d.get("categories", []),
                "source": "dynamic",
            }
        )

    holidays.sort(key=lambda h: h["parsed_date"])
    return holidays


def get_today_holidays(today: date | None = None) -> List[Holiday]:
    """
    Return holidays that are today
    """
    if today is None:
        today = date.today()

    today_mmdd = today.strftime("%m-%d")
    holidays = load_all_holidays(today)

    return [h for h in holidays if h["date"] == today_mmdd]
