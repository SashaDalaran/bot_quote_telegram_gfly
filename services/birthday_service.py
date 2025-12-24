from datetime import date

def is_today_in_date(date_str: str, today: date) -> bool:
    """
    Поддерживает:
    - MM-DD
    - MM-DD:MM-DD (включая переход через НГ)
    """
    if ":" not in date_str:
        month, day = map(int, date_str.split("-"))
        return today.month == month and today.day == day

    start_str, end_str = date_str.split(":")
    sm, sd = map(int, start_str.split("-"))
    em, ed = map(int, end_str.split("-"))

    start = date(today.year, sm, sd)
    end = date(today.year, em, ed)

    # диапазон через Новый год
    if end < start:
        return today >= start or today <= end

    return start <= today <= end
