"""Создание и настройка экземпляра бота."""

from aiogram import Bot, Dispatcher
from dishka.integrations.aiogram import setup_dishka

from config.settings import settings
from src.presentation.di_container import make_container
from src.presentation.handlers.entry import router as entry_router
from src.presentation.handlers.list import router as list_router
from src.presentation.handlers.save import router as save_router
from src.presentation.handlers.search import router as search_router
from src.presentation.handlers.start import router as start_router
from src.presentation.middlewares.error_handler import ErrorHandlerMiddleware


def create_bot() -> tuple[Bot, Dispatcher]:
    """Создаёт и настраивает бота с зарегистрированными хендлерами."""
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # Регистрируем роутеры
    dp.include_router(start_router)
    dp.include_router(save_router)
    dp.include_router(search_router)
    dp.include_router(list_router)
    dp.include_router(entry_router)

    return bot, dp


def setup_di(dp: Dispatcher) -> None:
    """Настраивает DI middleware."""
    container = make_container()
    setup_dishka(container=container, router=dp, auto_inject=True)


def setup_middlewares(dp: Dispatcher) -> None:
    """Настраивает middleware."""
    dp.message.middleware(ErrorHandlerMiddleware())
    dp.callback_query.middleware(ErrorHandlerMiddleware())
