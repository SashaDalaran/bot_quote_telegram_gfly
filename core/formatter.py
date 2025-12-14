# ==================================================
# core/formatter.py
# ==================================================

def format_remaining(seconds: int) -> str:
    """
    Преобразует секунды в строку вида:
    17д 7ч 41м 36с
    """
    seconds = max(0, int(seconds))

    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)

    parts = []

    if days:
        parts.append(f"{days}д")
    if hours:
        parts.append(f"{hours}ч")
    if minutes:
        parts.append(f"{minutes}м")

    parts.append(f"{secs}с")

    return " ".join(parts)


def choose_update_interval(seconds_left: int) -> int:
    """
    Умный выбор интервала обновления таймера
    """
    if seconds_left > 7 * 24 * 3600:      # больше недели
        return 3600                       # раз в час

    if seconds_left > 24 * 3600:          # больше суток
        return 600                        # раз в 10 минут

    if seconds_left > 6 * 3600:           # больше 6 часов
        return 300                        # раз в 5 минут

    if seconds_left > 3600:               # больше часа
        return 60                         # раз в минуту

    if seconds_left > 300:                # больше 5 минут
        return 10                         # раз в 10 секунд

    return 1                              # финал — каждую секунду
