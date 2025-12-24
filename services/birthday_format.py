from services.holidays_flags import COUNTRY_FLAGS, CATEGORY_EMOJIS

def format_challenge_message(events: list[dict]) -> str:
    emoji = CATEGORY_EMOJIS.get("Сhallenge", "🔥")
    return f"{emoji} **ЧЕЛЕНДЖ МУРЛОКОВ В АКТИВЕ!**"


def format_hero_message(event: dict) -> str:
    flag = COUNTRY_FLAGS.get(event["countries"][0], "🏆")
    emoji = CATEGORY_EMOJIS.get("Accept", "🏆")
    return f"{emoji} {flag} **ГЕРОЙ МУРЛОКОВ:** {event['name']}"


def format_birthday_message(events: list[dict]) -> str:
    emoji = CATEGORY_EMOJIS.get("Birthday", "🎂")
    names = ", ".join(e["name"] for e in events)
    return f"{emoji} **ДНИ РОЖДЕНИЯ МУРЛОКОВ СЕГОДНЯ:**\n{names}"
