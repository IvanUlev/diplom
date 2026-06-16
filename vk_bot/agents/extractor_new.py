import requests
import time
import re
from utils.helpers import safe_json_load
from agents.priority_tool import get_priority, parse_datetime

URL = "http://26.74.0.23:1234/v1/chat/completions"
MODEL_NAME = "google/gemma-3-4b"


def extract_data(text: str) -> dict:
    text = text.strip()
    

    prompt = f"""/no_think
    Извлеки данные задачи.

    Верни строго JSON:

    {{
    "title": "",
    "description": "",
    "deadline": ""
    }}

    Правила:
    - title — короткий, конкретный (как для Jira)
    - description:
    -должен кратко описывать задачу
    -можно использовать слова из исходного текста
    - description НЕ должен содержать срок задачи
    -НЕ включай в description: даты, дни недели, время и т.д.
    -НЕ оставляй пустым
    -НЕ выдумывай факты, которых нет
    - deadline — срок как в тексте ("через 3 дня", "в пятницу", "2 января")
    - если срока нет → ""

    ВАЖНО (очень строго):

    1. Если указано только время суток:
    "вечером", "утром", "в обед", "после обеда", "после работы", "после завтрака"
    И НЕТ конкретной даты (день недели, дата, "через N дней")

    → это означает СЕГОДНЯ

    2. Если есть сочетание:
    "вечером субботы", "утром понедельника", "в обед через 2 дня"

    → используй дату (суббота, через 2 дня), а не сегодня

    3. Если срока нет → верни ""

    4. В тексте могут быть орфографические ошибки — исправь их мысленно

    5. Если в тексте несколько времён, выбери то, которое относится к выполнению задачи, а не к содержимому задачи.


    - deadline — срок как в тексте, НЕ вычисляй дату.
    - Если есть "в течение дня", "в течении дня", "в течение месяца", "в течении месяца", "до конца недели", "к концу недели", "в конце недели", "до конца месяца", "к концу месяца", "на днях" — верни эту фразу в deadline.
    - Если есть "сегодня", "сейчас", "прямо сейчас", "послезавтра", "после завтра" — верни это в deadline.
    - Если есть "через N секунд", "через N минут", "через N часов", "через N дней" — верни это в deadline.
    - Если есть "конец недели", "конец рабочей недели" — верни всю фразу.
    - Если есть времена года или месяцы "под конец весны", "к середине лета", "к началу осени" — верни всю фразу.
    
    Пример:
    "поставить на завтра будильник на 6:00 сегодня в 19:00" → deadline: "сегодня в 19:00"

    НЕ выдумывай информацию

    Сообщение: "{text}"
    """

    start_time = time.time()

    try:
        response = requests.post(
            URL,
            json={
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 150,
            },
            timeout=30,
        )

        latency = time.time() - start_time

        response.raise_for_status()
        data = response.json()
        #content = data["choices"][0]["message"]["content"]





        message = data["choices"][0]["message"]

        content = (
            message.get("content")
            or ""
        )

        content = re.sub(r"<think>.*?</think>", "", content, flags=re.S).strip()

        content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )


        parsed = safe_json_load(content)

        title = str(parsed.get("title", "")).strip()
        description = str(parsed.get("description", "")).strip()
        raw_deadline = str(parsed.get("deadline", "")).strip().lower()
        if raw_deadline:
            description = description.replace(raw_deadline, "").strip(" ,.-")

        #DEADLINE
        deadline = None

        deadline = parse_datetime(raw_deadline or text)

        if deadline is None:
            deadline = "нет срока"
        else:
            deadline = str(deadline)

        #PRIORITY
        priority = get_priority(deadline, text)

        return {
            "title": title,
            "description": description,
            "deadline": deadline,
            "priority": priority,
            "latency": latency,
            "tokens": data.get("usage"),
            "raw": content
        }

    except Exception as e:
        return {
            "error": "extract_failed",
            "details": str(e),
        }