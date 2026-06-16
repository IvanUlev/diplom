import asyncio

from agents.detector import detect_task
from agents.extractor_new import extract_data
from agents.validator_new import validate_task
from services.jira_service import create_jira_issue


async def process_message(message_text: str, telegram_user: dict | None = None) -> dict:
    det = await asyncio.to_thread(detect_task, message_text)

    if not det.get("is_task"):
        return {
            "status": "no_task",
            "detector": det
        }

    ext = await asyncio.to_thread(extract_data, message_text)

    if "error" in ext:
        return {
            "status": "extract_error",
            "details": ext
        }

    val = await asyncio.to_thread(
        validate_task,
        ext,
        extract_data,
        message_text
    )

    if val.get("status") not in ("success", "failed"):
        return {
            "status": "validation_error",
            "details": val
        }

    final_task = val.get("task")

    if not final_task:
        return {
            "status": "invalid_task",
            "details": val
        }

    jira_issue = await create_jira_issue(final_task, telegram_user=telegram_user)

    return {
        "status": "created",
        "task": final_task,
        "jira_issue": jira_issue,
        "detector": det,
        "extractor": ext,
        "validator": val
    }