from fastapi import FastAPI
from contextlib import asynccontextmanager
from settings import logger, NoWebhookFilter
from aiogram import types

from fastapi.middleware.cors import CORSMiddleware

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

import logging

from core import settings

def create_limiter() -> Limiter:
    """Создаёт rate limiter"""
    return Limiter(
        key_func=get_remote_address, 
        default_limits=[settings.RATE_LIMIT]
    )

def setup_middlewares(app: FastAPI) -> None:
    """Настраивает middleware"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_URL],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(SlowAPIMiddleware)


def setup_routes(app: FastAPI) -> None:
    """Подключает роуты API"""
    from api.router import router
    app.include_router(router)


def setup_exception_handlers(app: FastAPI, limiter: Limiter) -> None:
    """Настраивает обработчики ошибок"""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle приложения"""
    from bot.loader import bot, dp
    from bot.commands import setup_bot_commands
    from middlewares.db import DataBaseSession
    from database.engine import session_maker

    logging.getLogger("uvicorn.access").addFilter(NoWebhookFilter())

    logger.info("Запуск приложения...")

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.set_webhook(
        settings.webhook_full_url,
        allowed_updates=settings.ALLOWED_UPDATES,
        drop_pending_updates=True
    )
    await setup_bot_commands(bot)
    await bot.set_chat_menu_button(
        menu_button=types.MenuButtonWebApp(
            text="Открыть", 
            web_app=types.WebAppInfo(url=settings.FRONTEND_URL)
            ))

    yield

    logger.info("Завершение приложения...")
    await bot.delete_webhook()
    await bot.session.close()

    logger.info("Приложение остановлено")


def create_app() -> FastAPI:
    """Фабрика приложения"""
    app = FastAPI(
        title="Example",
        lifespan=lifespan
    )
    
    limiter = create_limiter()
    
    setup_middlewares(app)
    setup_routes(app)
    setup_exception_handlers(app, limiter)
    
    return app