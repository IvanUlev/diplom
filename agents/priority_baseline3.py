import requests
from datetime import datetime
import logging

MODEL_NAME = "gemma-3-4b"
URL = "http://localhost:1234/v1/chat/completions"

DAYS = {
    "понедельник": 0,
    "понедельника": 0,
    "понедельнику": 0,
    "понедельником": 0,
    "понедельнике": 0,
    
    "вторник": 1,
    "вторника": 1,
    "вторнику": 1,
    "вторником": 1,
    "вторнике": 1,

    "среда": 2,
    "среду": 2,
    "среды": 2,
    "среде": 2,
    "средой": 2,

    "четверг": 3,
    "четверга": 3,
    "четвергу": 3,
    "четвергом": 3,
    "четверге": 3,

    "пятница": 4,
    "пятницу": 4,
    "пятницы": 4,
    "пятнице": 4,
    "пятницой": 4,

    "суббота": 5,
    "субботу": 5,
    "субботы": 5,
    "субботе": 5,
    "субботой": 5,

    "воскресенье": 6,
    "воскресенья": 6,
    "воскресеньем": 6,
    "воскресенью": 6,

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

    prompt = f"""
    Определи приоритет задачи.

    Сегодня: {today_weekday} (0 = понедельник, 6 = воскресенье)

    Приоритеты:
    - high — срочно, сегодня, завтра
    - medium — в течение нескольких дней (2–4 дня)
    - low — больше 5 дней или без срочности
    - укажите срок — если срок вообще не указан

    Правила:

    1. Если есть слова:
    "срочно", "сегодня", "завтра", "немедленно", "прямо сейчас"
    → high

    2. Если есть фразы:
    "вечером", "до вечера", "к утру", "до обеда" — считаем как сегодня, если нет других указаний.

    3. Если указаны дни недели:
    - разница 0–1 день → high
    - 2–4 дня → medium
    - 5+ дней → low

    4. Если есть слова:
    "на неделе", "скоро"
    → medium

    5. Если есть слова:
    "когда-нибудь", "не срочно", "потом", "позже", "в будущем", "когда будет время"
    → low

    6. Если в тексте НЕ говорится при период времени
    → укажите срок

    Примеры:

    "сделать сегодня" → high
    "сделать завтра" → high
    "сделать до вечера" → high
    "сделать к пятнице" → зависит от дня
    "сделать на неделе" → medium
    "сделать когда-нибудь" → low
    "купить молоко" → укажите срок
    "сходить в зал" → укажите срок

    Ответь строго одним вариантом:
    high
    medium
    low
    укажите срок

    Сообщение: "{text}"
    """

    try:
        r = requests.post(
            URL,
            json={
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0,
                "max_tokens": 5,
            },
            timeout=30,
        )

        data = r.json()
        content = data["choices"][0]["message"]["content"].strip().lower()

        if content.startswith("high"):
            return "high"
        if content.startswith("medium"):
            return "medium"
        if content.startswith("low"):
            return "low"
        if content.startswith("укажите срок"):
            return "укажите срок"

        return "укажите срок"

    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при запросе к модели: {e}")
        return "укажите срок"