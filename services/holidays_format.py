# ==================================================
# services/holidays_format.py
# ==================================================

from typing import List, Dict

Holiday = Dict[str, object]


def format_holidays_message(holidays: List[Holiday]) -> str:
    """
    Format holidays list into Telegram message
    """
    lines = ["🎉 *Праздники сегодня:*", ""]

    for h in holidays:
        name = h.get("name", "—")
        categories = ", ".join(h.get("categories", []))
        countries = ", ".join(h.get("countries", []))

        line = f"• **{name}**"
        if categories:
            line += f" _( {categories} )_"
        if countries:
            line += f"\n  🌍 {countries}"

        lines.append(line)

    return "\n".join(lines)
