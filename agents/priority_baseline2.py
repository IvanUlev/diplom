from datetime import datetime

HIGH_TRIGGERS = ["срочно", "сегодня", "завтра", "немедленно", "прямо сейчас","до утреннего релиза"]
MEDIUM_TRIGGERS = ["на неделе", "скоро"]
LOW_TRIGGERS = ["когда-нибудь", "не срочно", "потом", "позже", "в будущем", "когда будет время"]

DAYS = {
    "понедельник": 0,
    "понедельника": 0,
    "понедельнику": 0,

    "вторник": 1,
    "вторника": 1,
    "вторнику": 1,

    "среда": 2,
    "среду": 2,
    "среды": 2,

    "четверг": 3,
    "четверга": 3,

    "пятница": 4,
    "пятницу": 4,
    "пятницы": 4,

    "суббота": 5,
    "субботу": 5,

    "воскресенье": 6,
    "воскресенья": 6,
}


def get_priority(text: str, today_weekday: int | None = None) -> str:
    text = text.lower().strip()

    if today_weekday is None:
        today_weekday = datetime.today().weekday()

    for day, day_index in DAYS.items():
        if day in text:
            diff = day_index - today_weekday
            if diff < 0:
                diff += 7

            if diff <= 1:
                return "high"
            elif diff <= 4:
                return "medium"
            else:
                return "low"

    for word in HIGH_TRIGGERS:
        if word in text:
            return "high"

    for word in LOW_TRIGGERS:
        if word in text:
            return "low"

    for word in MEDIUM_TRIGGERS:
        if word in text:
            return "medium"

    return "not defined"


def evaluate_priority_dataset(dataset: list[dict]) -> dict:
    correct = 0
    details = []

    for item in dataset:
        pred = get_priority(
            item["text"],
            today_weekday=item.get("today_weekday")
        )
        ok = pred == item["priority"]
        if ok:
            correct += 1

        details.append({
            "text": item["text"],
            "today_weekday": item.get("today_weekday"),
            "true": item["priority"],
            "pred": pred,
            "ok": ok,
        })

    total = len(dataset)
    accuracy = correct / total if total else 0

    data = {
        "total": total,
        "correct": correct,
        "accuracy": accuracy,
        "details": details,
    }

    return data
