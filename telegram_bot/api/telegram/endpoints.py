import asyncio
from fastapi import Request

from aiogram import types

from core import settings
from bot.loader import bot, dp
from settings.logger import logger
from api.router import router_telegram


@router_telegram.post(settings.webhook_path)
async def handle_webhook(request: Request):
    """Обработчик входящих обновлений от Telegram"""
    try:
        data = await request.json()
        update = types.Update(**data)
        asyncio.create_task(dp.feed_update(bot=bot, update=update))
        return {"ok": True}
    except Exception as e:
        logger.error(f"Ошибка обработки вебхука: {e}")
        return {"ok": False, "error": str(e)}