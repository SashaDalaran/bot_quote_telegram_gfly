# ==================================================
# core/formatter.py
# ==================================================

def choose_update_interval(sec_left: int) -> float:
    """
    Smart countdown refresh rate.
    """
    if sec_left > 10 * 60:
        return 30
    if sec_left > 3 * 60:
        return 5
    if sec_left > 60:
        return 2
    if sec_left > 10:
        return 1
    if sec_left > 3:
        return 0.5
    return 0.25
