import json
import logging
from datetime import date
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

Holiday = Dict[str, object]


def load_holidays_from_file(path: str) -> List[Holiday]:
    """
    Загружает праздники из JSON-файла.
    Ожидается список объектов.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("Holidays JSON must be a list")

        logger.info("Loaded %d holidays from %s", len(data), path)
        return data

    except FileNotFoundError:
        logger.warning("Holidays file not found: %s", path)
        return []
    except Exception as e:
        logger.exception("Failed to load holidays from %s: %s", path, e)
        return []


def is_holiday_today(holiday: Holiday, today: date) -> bool:
    """
    Проверяет, попадает ли праздник на указанную дату.
    Формат даты в JSON: MM-DD
    """
    raw_date = holiday.get("date")
    if not isinstance(raw_date, str):
        return False

    try:
        month, day = map(int, raw_date.split("-"))
        return today.month == month and today.day == day
    except Exception:
        return False


def filter_holidays_for_today(
    holidays: List[Holiday],
    today: Optional[date] = None,
    country: Optional[str] = None,
) -> List[Holiday]:
    """
    Возвращает список праздников на сегодня.
    Можно фильтровать по стране.
    """
    if today is None:
        today = date.today()

    result: List[Holiday] = []

    for holiday in holidays:
        if not is_holiday_today(holiday, today):
            continue

        if country:
            countries = holiday.get("countries", [])
            if isinstance(countries, list):
                if country not in countries and "world" not in countries:
                    continue

        result.append(holiday)

    return result


def group_holidays_by_category(
    holidays: List[Holiday],
) -> Dict[str, List[Holiday]]:
    """
    Группирует праздники по категориям.
    """
    grouped: Dict[str, List[Holiday]] = {}

    for holiday in holidays:
        categories = holiday.get("category", [])
        if not isinstance(categories, list):
            continue

        for cat in categories:
            grouped.setdefault(cat, []).append(holiday)

    return grouped
