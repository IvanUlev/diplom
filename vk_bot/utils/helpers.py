import json
import re


def clean_json(content: str) -> str:
    content = content.strip()
    content = re.sub(r"```json|```", "", content).strip()
    return content


def safe_json_load(text: str):
    """
    Пытается распарсить JSON.
    Если модель вернула немного лишнего текста, пытаемся вытащить первый JSON-объект.
    """
    text = clean_json(text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise