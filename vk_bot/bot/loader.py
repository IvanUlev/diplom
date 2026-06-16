from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiohttp import ClientTimeout

from core import settings
from settings.proxy import proxy_manager


def create_bot_session() -> AiohttpSession:
    timeout = ClientTimeout(
        total=30,
        connect=10,
        sock_connect=10,
        sock_read=20
    )

    proxy_url = proxy_manager.get_next() if proxy_manager else None

    session = AiohttpSession(
        timeout=timeout,
        proxy=proxy_url,
    )

    if proxy_url:
        import logging
        logging.getLogger(__name__).info(f"Bot session proxy: {proxy_url}")

    return session


def create_bot() -> Bot:
    session = create_bot_session()

    return Bot(
        token=settings.API_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )


def create_dispatcher() -> Dispatcher:
    from settings.telegram_routers import user_router

    dp = Dispatcher()
    dp.include_router(user_router)

    return dp


bot = create_bot()
dp = create_dispatcher()