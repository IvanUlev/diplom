import requests
from utils.helpers import safe_json_load

url = "http://localhost:1234/v1/chat/completions"
MODEL_NAME = "gemma-3-4b"


def extract_data(text: str) -> dict:
    prompt = f"""
Извлеки данные задачи.

Верни строго JSON без пояснений:

{{
  "title": "",
  "description": ""
}}

Правила:
- не выдумывай факты
- если деталей нет, оставь пустую строку
- title должен быть коротким, конкретным и пригодным для Jira
- description может быть пустым

Сообщение: "{text}"
"""

    try:
        response = requests.post(
            url,
            json={
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 120,
            },
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        parsed = safe_json_load(content)

        return {
            "title": str(parsed.get("title", "")).strip(),
            "description": str(parsed.get("description", "")).strip(),
        }

    except Exception as e:
        return {
            "error": "extract_failed",
            "details": str(e),
        }