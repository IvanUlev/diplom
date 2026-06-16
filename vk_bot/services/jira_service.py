import httpx

from core import settings


def _make_jira_description(task: dict, telegram_user: dict | None = None) -> dict:
    user_text = ""

    if telegram_user:
        user_id = telegram_user.get("id") or "не указан"
        username = telegram_user.get("username") or "не указан"
        full_name = telegram_user.get("full_name") or "не указано"

        user_text = (
            f"Автор сообщения в Telegram:\n"
            f"ID: {user_id}\n"
            f"Username: @{username if username != 'не указан' else username}\n"
            f"Имя: {full_name}\n\n"
        )

    text = (
        f"{user_text}"
        f"{task.get('description', '')}\n\n"
        f"Дедлайн: {task.get('deadline') or 'нет срока'}\n"
        f"Приоритет: {task.get('priority') or 'нет срока'}"
    )

    return {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": text
                    }
                ]
            }
        ]
    }


async def create_jira_issue(task: dict, telegram_user: dict | None = None) -> dict:
    url = f"{settings.JIRA_BASE_URL.rstrip('/')}/rest/api/3/issue"

    payload = {
        "fields": {
            "project": {
                "key": settings.JIRA_PROJECT_KEY
            },
            "summary": task["title"],
            "description": _make_jira_description(task, telegram_user),
            "issuetype": {
                "name": settings.JIRA_ISSUE_TYPE
            }
        }
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            url,
            json=payload,
            auth=(settings.JIRA_EMAIL, settings.JIRA_API_TOKEN),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        )

    response.raise_for_status()
    data = response.json()

    issue_key = data["key"]

    return {
        "key": issue_key,
        "url": f"{settings.JIRA_BASE_URL.rstrip('/')}/browse/{issue_key}"
    }