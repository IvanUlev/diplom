import asyncio
import logging
import os
import random

import vk_api
from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll, VkEventType

from services.task_pipeline import process_message


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VK_API_TOKEN = os.getenv("VK_API_TOKEN")

processed_messages = set()


def send_vk_message(vk, user_id: int, text: str) -> None:
    vk.messages.send(
        user_id=user_id,
        message=text,
        random_id=random.getrandbits(31),
    )


def handle_message(event, vk) -> None:
    text = event.text.strip() if event.text else ""

    if not text:
        return

    message_id = getattr(event, "message_id", None)
    event_key = (event.user_id, message_id, text)

    if event_key in processed_messages:
        logger.info(f"Duplicate VK message skipped: {event_key}")
        return

    processed_messages.add(event_key)

    logger.info(f"VK message from user_id={event.user_id}: {text}")

    vk_user = {
        "id": event.user_id,
        "username": None,
        "full_name": f"VK user {event.user_id}",
    }

    try:
        result = asyncio.run(
            process_message(
                text,
                telegram_user=vk_user,
            )
        )

        if result["status"] == "no_task":
            send_vk_message(vk, event.user_id, "Задача не найдена.")
            return

        if result["status"] in ("extract_error", "validation_error", "invalid_task"):
            send_vk_message(vk, event.user_id, "Не удалось корректно сформировать задачу.")
            return

        if result["status"] == "created":
            task = result["task"]
            jira_issue = result["jira_issue"]

            send_vk_message(
                vk,
                event.user_id,
                (
                    "Задача создана в Jira.\n\n"
                    f"Название: {task.get('title')}\n"
                    f"Описание: {task.get('description')}\n"
                    f"Дедлайн: {task.get('deadline')}\n"
                    f"Приоритет: {task.get('priority')}\n"
                    f"Ссылка: {jira_issue['url']}"
                ),
            )
            return

        send_vk_message(vk, event.user_id, "Неизвестный результат обработки.")

    except Exception as exc:
        logger.exception(f"Ошибка при обработке VK-сообщения: {exc}")
        send_vk_message(
            vk,
            event.user_id,
            "Ошибка при создании задачи. Проверь LM Studio, Jira и .env.",
        )


def main() -> None:
    if not VK_API_TOKEN:
        raise RuntimeError("VK_API_TOKEN не задан в .env")

    vk_session = vk_api.VkApi(token=VK_API_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    logger.info("VK bot started")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            handle_message(event, vk)


if __name__ == "__main__":
    main()