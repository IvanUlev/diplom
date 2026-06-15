from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def register_telegram_message(
    session: AsyncSession,
    chat_id: int,
    message_id: int,
    telegram_user_id: int | None,
    message_text: str | None,
) -> bool:
    result = await session.execute(
        text(
            """
            INSERT INTO telegram_processed_messages
                (chat_id, message_id, telegram_user_id, message_text, status)
            VALUES
                (:chat_id, :message_id, :telegram_user_id, :message_text, 'processing')
            ON CONFLICT (chat_id, message_id) DO NOTHING
            RETURNING id
            """
        ),
        {
            "chat_id": chat_id,
            "message_id": message_id,
            "telegram_user_id": telegram_user_id,
            "message_text": message_text,
        },
    )

    await session.commit()
    return result.scalar_one_or_none() is not None


async def mark_telegram_message_done(
    session: AsyncSession,
    chat_id: int,
    message_id: int,
    status: str,
    jira_key: str | None = None,
    jira_url: str | None = None,
) -> None:
    await session.execute(
        text(
            """
            UPDATE telegram_processed_messages
            SET
                status = :status,
                jira_key = :jira_key,
                jira_url = :jira_url,
                updated_at = now()
            WHERE chat_id = :chat_id
              AND message_id = :message_id
            """
        ),
        {
            "chat_id": chat_id,
            "message_id": message_id,
            "status": status,
            "jira_key": jira_key,
            "jira_url": jira_url,
        },
    )

    await session.commit()