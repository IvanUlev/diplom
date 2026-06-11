import requests
import re
from datetime import datetime
import logging

MODEL_NAME = "gemma-3-4b"
URL = "http://localhost:1234/v1/chat/completions"

DAYS = {
    "понедельник": 0,"понедельника": 0,"понедельнику": 0,"понедельником": 0,"понедельнике": 0,
    
    "вторник": 1,"вторника": 1,"вторнику": 1,"вторником": 1,"вторнике": 1,

    "среда": 2,"среду": 2,"среды": 2,"среде": 2,"средой": 2,

    "четверг": 3,"четверга": 3,"четвергу": 3,"четвергом": 3,"четверге": 3,

    "пятница": 4,"пятницу": 4,"пятницы": 4,"пятнице": 4,"пятницой": 4,

    "суббота": 5,"субботу": 5,"субботы": 5,"субботе": 5,"субботой": 5,

    "воскресенье": 6,"воскресенья": 6,"воскресеньем": 6,"воскресенью": 6,

}

MONTHS = {

    "января": 1, "январь": 1, "январю": 1,"январем": 1, "январём": 1, "январе": 1,

    "февраля": 2, "февраль": 2, "февралю": 2, "февралем": 2, "феврале": 2,"февралём": 2,

    "марта": 3, "март": 3, "марту": 3,"мартом": 3, "марте": 3,

    "апреля": 4, "апрель": 4, "апрелю": 4,"апрелем": 4, "апреле": 4,

    "мая": 5, "май": 5, "маю": 5,"маем": 5, "мае": 5,

    "июня": 6, "июнь": 6, "июню": 6,"июнем": 6, "июне": 6,

    "июля": 7, "июль": 7, "июлю": 7,"июлем": 7, "июле": 7,

    "августа": 8, "август": 8, "августу": 8,"августом": 8, "августе": 8,

    "сентября": 9, "сентябрь": 9, "сентябрю": 9,"сентябрем": 9, "сентябрём": 9, "сентябре": 9,

    "октября": 10, "октябрь": 10, "октябрю": 10,"октябрем": 10, "октябрём": 10, "октябре": 10,

    "ноября": 11, "ноябрь": 11, "ноябрю": 11,"ноябрем": 11, "ноябрём": 11, "ноябре": 11,

    "декабря": 12, "декабрь": 12, "декабрю": 12,"декабрем": 12, "декабрём": 12, "декабре": 12,

}

SEASONS = {
    "зима": 1, "зиме": 1, "зимой": 1, "зиму": 1, "зимы": 1,"начало зимы":12, "середина зимы":1, "конец зимы":2,

    "весна": 4, "весне": 4, "весной": 4, "весну": 4, "весны": 4,"начало весны":3,"середина весны":4,"конец весны":5,

    "лето": 7, "лету": 7, "летом": 7, "лету": 7, "летах": 7,"начало лета":6,"середина лета":7,"конец лета":8,

    "осень": 10, "осени":10, "осенью": 10, "осень": 10, "осени": 10,"начало осени":9,"середина осени":10,"конец осени":11,

}
def parse_date(text: str):
    
    match = re.search(r"(\d{1,2})\s*(\w+)", text)
    if match:
        day = int(match.group(1))
        month_word = match.group(2)

        if month_word in MONTHS:
            month = MONTHS[month_word]
            return build_date(day, month)

    match = re.search(r"(\d{1,2})\.(\d{1,2})(?:\.(\d{4}))?", text)
    if match:
        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3)) if match.group(3) else None

        return build_date(day, month, year)

    return None

def build_date(day, month, year=None):
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    if year is None:
        year = today.year

    try:
        target = datetime(year, month, day)
    except:
        return None

    if target < today:
        try:
            target = datetime(year + 1, month, day)
        except:
            return None

    diff = (target - today).days
    return diff

def parse_relative_time(text: str):
    # через 5 часов / через 1 час / через 3 часа
    match = re.search(r"через\s+(\d+)\s*час(а|ов)?", text)
    if match:
        hours = int(match.group(1))
        if hours <= 24:
            return "high"
        elif hours <= 72:
            return "medium"
        else:
            return "low"

    # через 2 дня / через 1 день
    match = re.search(r"через\s+(\d+)\s*д(ень|ня|ней)?", text)
    if match:
        days = int(match.group(1))
        if days <= 1:
            return "high"
        elif days <= 4:
            return "medium"
        else:
            return "low"

    return None

def parse_season(text: str):
    for season, season_month in SEASONS.items():
        if season in text:
            season_date = build_date(1, season_month)  # Берем начало сезона
            if season_date is not None:
                if season_date <= 1:
                    return "high"
                elif season_date <= 4:
                    return "medium"
                else:
                    return "low"
    return None


def get_priority(text: str, today_weekday: int | None = None) -> str:
    text = text.lower().strip()

    if today_weekday is None:
        today_weekday = datetime.today().weekday()

    rel = parse_relative_time(text)
    if rel is not None:
        return rel

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
            
    for season, season_month in SEASONS.items():
        if season in text:
            season_date = build_date(1, season_month)  # Берем начало сезона
            if season_date is not None:
                if season_date <= 1:
                    return "high"
                elif season_date <= 4:
                    return "medium"
                else:
                    return "low"

    diff = parse_date(text)

    if diff is not None:
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
    - уточните срок — если срок вообще не указан

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
    → уточните срок

    Примеры:

    "сделать сегодня" → high
    "сделать завтра" → high
    "сделать до вечера" → high
    "сделать к пятнице" → зависит от дня
    "сделать на неделе" → medium
    "сделать когда-нибудь" → low
    "купить молоко" → уточните срок
    "сходить в зал" → уточните срок
    "исправить код" → уточните срок
    "написать клиенту письмо" → уточните срок


    Ответь строго одним вариантом:
    high
    medium
    low
    уточните срок

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
        if content.startswith("уточните срок"):
            return "уточните срок"

        return "уточните срок"

    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при запросе к модели: {e}")
        return "уточните срок"