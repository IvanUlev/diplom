import re
from datetime import datetime, timedelta

DAYS = {
    "понедельник": 0,"понедельника": 0,"понедельнику": 0,"понедельником": 0,"понедельнике": 0,
    
    "вторник": 1,"вторника": 1,"вторнику": 1,"вторником": 1,"вторнике": 1,

    "среда": 2,"среду": 2,"среды": 2,"среде": 2,"средой": 2,

    "четверг": 3,"четверга": 3,"четвергу": 3,"четвергом": 3,"четверге": 3,

    "пятница": 4,"пятницу": 4,"пятницы": 4,"пятнице": 4,"пятницой": 4,

    "суббота": 5,"субботу": 5,"субботы": 5,"субботе": 5,"субботой": 5,

    "воскресенье": 6,"воскресенья": 6,"воскресеньем": 6,"воскресенью": 6,

}

TIME_OF_DAY = [
    "вечер", "вечером", "до вечера",
    "утро", "утром", "к утру",
    "обед", "в обед", "до обеда",
    "после обеда", "после работы"
]

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

    "лето": 7, "лету": 7, "летом": 7, "летах": 7,"начало лета":6,"середина лета":7,"конец лета":8,

    "осень": 10, "осени":10, "осенью": 10, "осень": 10, "осени": 10,"начало осени":9,"середина осени":10,"конец осени":11,

}

HIGH_TRIGGERS = ["срочно", "сегодня", "завтра", "немедленно", "прямо сейчас","важно","очень важно","сейчас"]
MEDIUM_TRIGGERS = ["на неделе", "скоро"]
LOW_TRIGGERS = ["когда-нибудь", "не срочно", "потом", "позже", "в будущем", "когда будет время"]

def get_today():
    return datetime.now().strftime("%Y-%m-%d")
def parse_datetime(text: str) -> str | None:
    text = text.lower()
    now = datetime.now()

    target = now
    found_date = False

    hour = None
    minute = 0

    season_date = parse_season(text)
    if season_date:
        return season_date
    
    #сегодня / завтра
    if "сегодня" in text:
        target = now
        found_date = True

    elif "завтра" in text:
        target = now + timedelta(days=1)
        found_date = True

    #время вида 19:00
    match = re.search(r"(?:в|на|к)\s+(\d{1,2})[:](\d{2})", text)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))

    #время суток
    elif "вечер" in text:
        hour = 19
    elif "утро" in text:
        hour = 9
    elif "обед" in text:
        hour = 15

    #через N дней
    day_match = re.search(r"через\s+(\d+)\s*д", text)
    if day_match:
        days = int(day_match.group(1))
        target = now + timedelta(days=days + 1)
        found_date = True

    #дата вида 13.04.2026 или 23.05
    date_match = re.search(r"\b(\d{1,2})[.](\d{1,2})(?:[.](\d{4}))?\b", text)
    if date_match:
        day = int(date_match.group(1))
        month = int(date_match.group(2))
        year = int(date_match.group(3)) if date_match.group(3) else now.year

        target = datetime(year, month, day)

        if target < now:
            target = datetime(year + 1, month, day)

        found_date = True

    #дата вида 12 апреля
    word_date_match = re.search(r"\b(\d{1,2})\s+([а-яё]+)\b", text)
    if word_date_match:
        day = int(word_date_match.group(1))
        month_word = word_date_match.group(2)

        if month_word in MONTHS:
            month = MONTHS[month_word]
            target = datetime(now.year, month, day)

            if target < now:
                target = datetime(now.year + 1, month, day)

            found_date = True

    #дни недели
    for key, idx in DAYS.items():
        if key in text:
            diff = idx - now.weekday()
            if diff < 0:
                diff += 7
            target = now + timedelta(days=diff)
            found_date = True
            break

    if not found_date and hour is None:
        return None

    
    #если вообще ничего
    if target == now and hour is None:
        return None

    if hour is not None:
        target = target.replace(hour=hour, minute=minute, second=0, microsecond=0)
        return target.strftime("%Y-%m-%d %H:%M")
    else:
        return target.strftime("%Y-%m-%d")
    

def parse_season(text: str):
    now = datetime.now()

    for season, month in SEASONS.items():
        if season in text:

            if "начало" in season:
                day = 1
            elif "середина" in season:
                day = 15
            elif "конец" in season:
                day = 25
            else:
                day = 1

            year = now.year
            target = datetime(year, month, day)

            if target < now:
                target = datetime(year + 1, month, day)

            return target.strftime("%Y-%m-%d")

    return None
def get_priority(deadline: str, text: str) -> str:
    """
    Определяет приоритет задачи на основе текста.
    Логика:
    - сначала триггерные слова
    - потом относительное время
    - потом дни недели
    - потом fallback
    """

    text = text.lower().strip()
    today = datetime.today()

    #LOW триггеры
    if any(w in text for w in LOW_TRIGGERS):
        return "low"
    
    #HIGH триггеры
    if any(w in text for w in HIGH_TRIGGERS):
        return "high"

    #MEDIUM триггеры
    if any(w in text for w in MEDIUM_TRIGGERS):
        return "medium"

    #через N дней
    match = re.search(r"через\s+(\d+)\s*д", text)
    if match:
        days = int(match.group(1))

        if days <= 1:
            return "high"
        elif 2 <= days <= 4:
            return "medium"
        else:
            return "low"

    #дни недели
    for key, day_index in DAYS.items():
        if key[:5] in text:
            today_index = today.weekday()

            diff = day_index - today_index
            if diff < 0:
                diff += 7

            if diff <= 1:
                return "high"
            elif 2 <= diff <= 4:
                return "medium"
            else:
                return "low"
    #сезоны       
    season_date = parse_season(text)
    if season_date:
        return "low"
    
    #"вечером", "до вечера" и т.д. → сегодня
    if any(w in text for w in TIME_OF_DAY):
        return "high"

    #если нет срока
    return "нет срока"