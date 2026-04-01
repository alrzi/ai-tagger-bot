"""Создание и настройка экземпляра бота."""

from aiogram import Bot, Dispatcher

from config.settings import settings
from src.presentation.handlers.save import router as save_router
from src.presentation.handlers.search import router as search_router
from src.presentation.handlers.start import router as start_router


def create_bot() -> tuple[Bot, Dispatcher]:
    """Создаёт и настраивает бота с зарегистрированными хендлерами."""
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # Регистрируем роутеры
    dp.include_router(start_router)
    dp.include_router(save_router)
    dp.include_router(search_router)

    return bot, dp
