import requests

url = "http://localhost:1234/v1/chat/completions"
MODEL_NAME = "gemma-3-4b"


def detect_task(text: str) -> bool:
    prompt = f"""
Определи, является ли сообщение задачей.

Задача — это конкретное обязательное действие с явным объектом или результатом.
Даже короткая команда считается задачей только если понятно, что нужно сделать.

НЕ задача:
- обсуждение (обсудить, подумать)
- неопределённые фразы без конкретного объекта ("разберись с этим", "посмотри")
- разговор ("как дела?", "что делаешь?")
- предложение или вариант действия ("давай", "может")

Примеры:
"Сделать отчёт" -> true
"Пофиксить баг" -> true
"Пойдём гулять" -> false
"Давай созвонимся" -> false
"Обсудить дизайн" -> false

Ответь строго одним словом:
true
или
false

Сообщение: "{text}"
"""

    try:
        response = requests.post(
            url,
            json={
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0,
                "max_tokens": 5,
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        content = data["choices"][0]["message"]["content"].strip().lower()

        if content == "true":
            return True
        if content == "false":
            return False

        # fallback: если модель ответила лишним текстом
        if content.startswith("true"):
            return True
        if content.startswith("false"):
            return False

        return False

    except Exception:
        return False