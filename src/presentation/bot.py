"""Создание и настройка экземпляра бота."""

from aiogram import Bot, Dispatcher
from dishka.integrations.aiogram import setup_dishka

from config.settings import settings
from src.ioc.container import make_container
from src.presentation.handlers.callbacks import entry_callback_router
from src.presentation.handlers.commands import (
    categories_router,
    help_router,
    list_router,
    search_router,
    start_router,
    stats_router,
    status_router,
    tags_router,
)
from src.presentation.handlers.messages import save_router
from src.presentation.middlewares.debounce import DebounceMiddleware
from src.presentation.middlewares.error_handler import ErrorHandlerMiddleware
from src.presentation.middlewares.rate_limiter import RateLimitMiddleware


def create_bot() -> tuple[Bot, Dispatcher]:
    """Создаёт и настраивает бота с зарегистрированными хендлерами."""
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # Регистрируем роутеры
    dp.include_router(start_router)
    dp.include_router(help_router)
    dp.include_router(status_router)
    dp.include_router(categories_router)
    dp.include_router(stats_router)
    dp.include_router(save_router)
    dp.include_router(search_router)
    dp.include_router(list_router)
    dp.include_router(tags_router)
    dp.include_router(entry_callback_router)

    return bot, dp


def setup_di(dp: Dispatcher) -> None:
    """Настраивает DI middleware."""
    container = make_container()
    setup_dishka(container=container, router=dp, auto_inject=True)


def setup_middlewares(dp: Dispatcher, redis: object) -> None:
    """Настраивает middleware."""
    # Rate limiting (отсекаем спам)
    dp.message.middleware(RateLimitMiddleware(redis, max_messages=10, window=60))  # type: ignore[arg-type]
    
    # Debouncing (склеиваем сообщения)
    dp.message.middleware(DebounceMiddleware(redis, delay=2.0))  # type: ignore[arg-type]
    
    # Error handling
    dp.message.middleware(ErrorHandlerMiddleware())
    dp.callback_query.middleware(ErrorHandlerMiddleware())
