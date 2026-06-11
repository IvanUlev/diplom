import requests
import time
from utils.helpers import safe_json_load

URL = "http://localhost:1234/v1/chat/completions"
MODEL_NAME = "google/gemma-3-4b"


def build_validator_prompt(task: dict) -> str:
    return f"""
Ты — агент-валидатор задачи для Jira.

Оцени качество извлечённых данных задачи.

Задача:
{task}

Критерии оценки:
- title короткий, конкретный и отражает суть задачи
- description содержит только информацию из исходного текста и не содержит выдуманных деталей
- deadline корректный: дата/дата+время или "нет срока"
- priority соответствует сроку и срочности задачи
- задача логична и выполнима

Оцени качество от 1 до 10.

Верни строго JSON без пояснений:

{{
  "score": 0,
  "is_valid": true,
  "comment": ""
}}
"""


def call_llm(prompt: str) -> dict:
    start_time = time.time()

    response = requests.post(
        URL,
        json={
            "model": MODEL_NAME,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
            "max_tokens": 150,
        },
        timeout=30,
    )

    latency = time.time() - start_time

    response.raise_for_status()
    data = response.json()

    content = data["choices"][0]["message"]["content"]
    parsed = safe_json_load(content)

    return {
        "result": parsed,
        "latency": latency,
        "tokens": data.get("usage"),
        "raw": content
    }


def validate_task(task: dict, extractor_func, original_text: str, max_retries: int = 3) -> dict:
    current_task = task
    total_latency = 0
    total_tokens = 0
    attempts = []

    for i in range(max_retries):
        try:
            prompt = build_validator_prompt(current_task)
            llm_response = call_llm(prompt)

            total_latency += llm_response["latency"]

            if llm_response["tokens"]:
                total_tokens += llm_response["tokens"].get("total_tokens", 0)

            result = llm_response["result"]

            score = int(result.get("score", 0))
            is_valid = bool(result.get("is_valid", False))
            comment = str(result.get("comment", ""))

            attempts.append({
                "attempt": i + 1,
                "score": score,
                "is_valid": is_valid,
                "comment": comment,
                "raw": llm_response["raw"]
            })

            if is_valid and score >= 7:
                return {
                    "status": "success",
                    "task": current_task,
                    "score": score,
                    "attempts": attempts,
                    "latency": total_latency,
                    "tokens": total_tokens
                }

            current_task = extractor_func(original_text)

        except Exception as e:
            return {
                "status": "error",
                "details": str(e),
                "task": current_task,
                "attempts": attempts,
                "latency": total_latency,
                "tokens": total_tokens
            }

    return {
        "status": "failed",
        "task": current_task,
        "attempts": attempts,
        "latency": total_latency,
        "tokens": total_tokens
    }