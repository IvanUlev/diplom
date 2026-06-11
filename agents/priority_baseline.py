from datetime import datetime

HIGH_TRIGGERS = ["срочно", "сегодня", "завтра", "немедленно", "прямо сейчас"]
LOW_TRIGGERS = ["когда-нибудь", "не срочно", "потом", "позже", "в будущем", "когда будет время"]

DAYS = {
    "понедельник": 0,
    "вторник": 1,
    "среда": 2,
    "четверг": 3,
    "пятница": 4,
    "суббота": 5,
    "воскресенье": 6,
}


def get_priority(text: str, today_weekday: int | None = None) -> str:
    text = text.lower().strip()

    for word in HIGH_TRIGGERS:
        if word in text:
            return "high"

    for word in LOW_TRIGGERS:
        if word in text:
            return "low"

    if today_weekday is None:
        today_weekday = datetime.today().weekday()

    for day, day_index in DAYS.items():
        if day in text:
            diff = day_index - today_weekday

            if diff < 0:
                diff += 7

            if diff <= 1:
                return "high"
            elif diff <= 3:
                return "medium"
            else:
                return "low"

    return "medium"