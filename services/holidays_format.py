from typing import List, Dict
from daily.holidays.holidays_flags import COUNTRY_FLAGS, CATEGORY_EMOJIS

Holiday = Dict[str, object]


def format_holidays_message(holidays: List[Holiday]) -> str:
    lines = ["🎉 Today’s Holidays", ""]

    for h in holidays:
        name = h.get("name", "—")
        categories = h.get("categories", [])
        countries = h.get("countries", [])

        # --- страна / флаг ---
        if countries:
            country_key = countries[0]
            flag = COUNTRY_FLAGS.get(country_key, "🌍")
        else:
            flag = "🌍"

        # --- название праздника ---
        lines.append(f"{flag} {name}")

        # --- категория ---
        if categories:
            category = categories[0]
            emoji = CATEGORY_EMOJIS.get(category, "🔖")
            lines.append(f"{emoji} {category}")

        lines.append("")  # пустая строка между праздниками

    return "\n".join(lines).strip()
