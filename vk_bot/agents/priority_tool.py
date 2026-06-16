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
NUM_PATTERNS = {
    r"один|одна|одно|одну": 1,

    r"два|две": 2,

    r"три": 3,
    r"четыр": 4,
    r"пят": 5,
    r"шест": 6,
    r"сем": 7,
    r"восем": 8,
    r"девят": 9,
    r"десят": 10,

    r"пару|пара": 2,
}


def parse_number(value: str) -> int | None:
    value = value.lower().strip()

    if value.isdigit():
        return int(value)

    for pattern, number in NUM_PATTERNS.items():
        if re.search(pattern, value):
            return number

    return None

def normalize_numbers(text: str) -> str:
    text = text.lower()

    for pattern, number in NUM_PATTERNS.items():
        text = re.sub(
            rf"\b({pattern})\b",
            str(number),
            text
        )

    return text

def last_day_of_month(month: int) -> int:
    if month in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    if month == 2:
        return 28
    return 30


def get_month_from_text(text: str):
    for month_word, month_num in MONTHS.items():
        if month_word in text:
            return month_num
    return None

def parse_datetime(text: str) -> str | None:
    text = text.lower().replace("ё", "е")
    text = normalize_numbers(text)
    text = re.sub(r"(\d)([а-яА-Я])", r"\1 \2", text)
    now = datetime.now()

    target = now
    found_date = False

    hour = None
    minute = 0

    # сейчас / прямо сейчас
    if "прямо сейчас" in text or re.search(r"\bсейчас\b", text):
        target = now
        found_date = True

    # послезавтра / после завтра
    elif "послезавтра" in text or "после завтра" in text:
        target = now + timedelta(days=2)
        found_date = True
        
    
    #сегодня / завтра
    elif "сегодня" in text:
        target = now
        found_date = True

    elif "завтра" in text:
        target = now + timedelta(days=1)
        found_date = True

    # следующим утром / следующим днем / следующим вечером / следующим обедом
    next_time_match = re.search(
        r"следующ\w*\s+(утр\w*|дн\w*|вечер\w*|обед\w*)",
        text
    )

    if next_time_match:
        part = next_time_match.group(1)

        target = now + timedelta(days=1)

        if part.startswith("утр"):
            hour = 9
        elif part.startswith("обед") or part.startswith("дн"):
            hour = 15
        elif part.startswith("вечер"):
            hour = 19

        found_date = True

    # к полуночи -> сегодня 23:59
    elif "к полуночи" in text or "до полуночи" in text:
        target = now
        hour = 23
        minute = 59
        found_date = True

    # в течение / в течении дня -> сегодня 23:59
    if re.search(r"в\s+течени[еи]\s+дн", text):
        target = now.replace(hour=23, minute=59, second=0, microsecond=0)
        found_date = True

    # в течение / в течении месяца -> конец текущего месяца
    elif re.search(r"в\s+течени[еи]\s+месяц", text):
        day = last_day_of_month(now.month)
        target = datetime(now.year, now.month, day)
        found_date = True

    # на днях -> через 2 дня
    elif re.search(r"на\s+днях", text):
        target = now + timedelta(days=2)
        found_date = True

    # до / к концу месяца
    if re.search(r"(до|к|в|на)?\s*кон(ец|ца|цу|це)?\s+месяц", text):
        day = last_day_of_month(now.month)
        target = datetime(now.year, now.month, day, 23, 59)
        found_date = True
    
    # начало следующего месяца
    if re.search(r"начал\w*\s+следующ\w*\s+месяц", text):
        month = now.month + 1
        year = now.year

        if month > 12:
            month = 1
            year += 1

        target = datetime(year, month, 1)
        found_date = True

    # до 10 утра / к 6 вечера
    time_word_match = re.search(
        r"(?:до|к)\s+(\d{1,2})\s*(утра|вечера|дня)?",
        text)
    
    

    if time_word_match:
        h = int(time_word_match.group(1))
        period = time_word_match.group(2)

        if period == "вечера" and h < 12:
            h += 12

        hour = h
        minute = 0

    word_hour_match = re.search(
        r"(?:к|до|часам к|к часам)\s+(\d+|один|одну|одно|два|две|три|четыре|пять|шесть|семь|восемь|девять|десять)\s*(утра|вечера|дня)?",
        text
    )

    if word_hour_match:
        raw_h = word_hour_match.group(1)
        h = parse_number(raw_h)
        period = word_hour_match.group(2)

        if h is not None:
            if period == "вечера" and h < 12:
                h += 12

            hour = h
            minute = 0
            found_date = True


    # через N секунд / минут / часов / дней / недель / месяцев
    relative_match = re.search(
        r"через\s+(?:(\d+|один|одну|одно|два|две|три|четыре|пять|шесть|семь|восемь|девять|десять|пару|пара)\s+)?"
        r"(секунд\w*|сек\w*|минут\w*|минуту|мин\w*|час\w*|дн\w*|день|недел\w*|месяц\w*|год\w*)",
        text
    )

    relative_has_time = False

    if relative_match:
        amount_raw = relative_match.group(1)
        unit = relative_match.group(2)

        amount = parse_number(amount_raw) if amount_raw else 1

        if amount is not None:
            if unit.startswith("сек"):
                target = now + timedelta(seconds=amount)
                relative_has_time = True

            elif unit.startswith("мин"):
                target = now + timedelta(minutes=amount)
                relative_has_time = True

            elif unit.startswith("час"):
                target = now + timedelta(hours=amount)
                relative_has_time = True

            elif unit.startswith("дн") or unit == "день":
                target = now + timedelta(days=amount)

            elif unit.startswith("недел"):
                target = now + timedelta(days=amount * 7)

            elif unit.startswith("месяц"):
                month = now.month + amount
                year = now.year

                while month > 12:
                    month -= 12
                    year += 1

                day = min(now.day, last_day_of_month(month))
                target = datetime(year, month, day)

            elif unit.startswith("год"):
                target = datetime(now.year + amount, now.month, now.day)

            found_date = True

    # конец рабочей недели
    if re.search(r"(до|к|в|на)?\s*кон(ец|цу|ца|це)?\s+рабоч\w*\s+недел", text):
        diff = 4 - now.weekday()
        if diff < 0:
            diff += 7
        target = now + timedelta(days=diff)
        found_date = True

    # конец недели
    elif re.search(r"(до|к|в|на)?\s*кон(ец|цу|ца|це)?\s+недел", text):
        diff = 6 - now.weekday()
        if diff < 0:
            diff += 7
        target = now + timedelta(days=diff)
        found_date = True

    # сезоны
    season_date = parse_season(text)
    if season_date:
        return season_date
    
    #время вида 19:00
    match = re.search(r"(?:в|на|к|до)?\s*(?:сегодня|завтра)?\s*(?:в\s*)?(\d{1,2})[:](\d{2})", text)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))

    #время суток
    elif "после работы" in text:
        hour = 19
    elif "вечер" in text:
        hour = 19
    elif "утро" in text:
        hour = 9
    elif "обед" in text:
        hour = 15

        if not found_date:
            target = now



    #дата вида 13.04.2026 или 23.05
    date_match = re.search(r"\b(\d{1,2})[.](\d{1,2})(?:[.](\d{4}))?\b", text)
    if date_match:
        day = int(date_match.group(1))
        month = int(date_match.group(2))
        year = int(date_match.group(3)) if date_match.group(3) else now.year

        target = datetime(year, month, day)

        if target.date() < now.date():
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

            if target.date() < now.date():
                target = datetime(now.year + 1, month, day)

            found_date = True

    # начало / середина / конец месяца
    part = None
    if re.search(r"начал", text):
        part = "start"
    elif re.search(r"середин", text):
        part = "middle"
    elif re.search(r"кон(ец|цу|ца|це|цом)|под\s+кон", text):
        part = "end"

    month = get_month_from_text(text)

    if part and month:
        if part == "start":
            day = 1
        elif part == "middle":
            day = 15
        else:
            day = last_day_of_month(month)

        target = datetime(now.year, month, day, 23, 59)

        if target.date() < now.date():
            target = datetime(now.year + 1, month, day)

        found_date = True

    # просто месяц: к июню / до июня / в июне
    month_only_match = re.search(r"(?:к|до|в)\s+[а-яе]+", text)

    if month_only_match and month and not part:
        target = datetime(now.year, month, 1)

        if target.date() < now.date():
            target = datetime(now.year + 1, month, 1)

        found_date = True

    # голый месяц: июнь / июня / июлю
    if month and not found_date and not part:
        target = datetime(now.year, month, 1)

        if target.date() < now.date():
            target = datetime(now.year + 1, month, 1)

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
    
    # время вида 900 / 1730
    compact_time = re.search(r"\b(\d{3,4})\b", text)

    if compact_time:
        value = compact_time.group(1)

        if len(value) == 3:
            h = int(value[0])
            m = int(value[1:])
        else:
            h = int(value[:2])
            m = int(value[2:])

        if 0 <= h <= 23 and 0 <= m <= 59:
            hour = h
            minute = m

    
    #если вообще ничего
    if hour is not None:
        target = target.replace(hour=hour, minute=minute, second=0, microsecond=0)
        return target.strftime("%Y-%m-%d %H:%M")

    if relative_has_time:
        return target.strftime("%Y-%m-%d %H:%M")

    return target.strftime("%Y-%m-%d")
    

def parse_season(text: str):
    text = text.lower().replace("ё", "е")
    now = datetime.now()

    season_patterns = {
        r"весн": {
            "start": (3, 1),
            "middle": (4, 15),
            "end": (5, 31),
        },
        r"лет": {
            "start": (6, 1),
            "middle": (7, 15),
            "end": (8, 31),
        },
        r"осен": {
            "start": (9, 1),
            "middle": (10, 15),
            "end": (11, 30),
        },
        r"зим": {
            "start": (12, 1),
            "middle": (1, 15),
            "end": (2, 28),
        },
    }

    if re.search(r"начал", text):
        part = "start"
    elif re.search(r"середин", text):
        part = "middle"
    elif re.search(r"кон(ец|цу|ца|це|цом)|под\s+кон", text):
        part = "end"
    else:
        return None

    for season_root, dates in season_patterns.items():
        if re.search(season_root, text):
            month, day = dates[part]

            target = datetime(now.year, month, day)

            if target.date() < now.date():
                target = datetime(now.year + 1, month, day)

            return target.strftime("%Y-%m-%d")

    return None
  
def get_priority(deadline: str, text: str) -> str:
    text = text.lower().strip()

    if any(w in text for w in LOW_TRIGGERS):
        return "low"
    
    if any(w in text for w in HIGH_TRIGGERS):
        return "high"

    if any(w in text for w in MEDIUM_TRIGGERS):
        return "medium"

    if not deadline or deadline == "нет срока":
        return "нет срока"

    try:
        now = datetime.now()

        if " " in deadline:
            target = datetime.strptime(deadline, "%Y-%m-%d %H:%M")
        else:
            target = datetime.strptime(deadline, "%Y-%m-%d")
            target = target.replace(hour=23, minute=59)

        diff_hours = (target - now).total_seconds() / 3600

        if diff_hours <= 48:
            return "high"
        elif diff_hours <= 120:
            return "medium"
        else:
            return "low"

    except Exception:
        return "нет срока"