"""Создание и конфигурация DI-контейнера."""

from dishka import AsyncContainer, make_async_container
from dishka.integrations.aiogram import AiogramProvider

from src.ioc.providers import (
    AIProvider,
    DatabaseProvider,
    ResponderProvider,
    RepositoryProvider,
    SettingsProvider,
    UseCaseProvider,
)


def make_container() -> AsyncContainer:
    """Создаёт DI-контейнер для aiogram."""
    return make_async_container(
        AiogramProvider(),
        SettingsProvider(),
        DatabaseProvider(),
        RepositoryProvider(),
        UseCaseProvider(),
        AIProvider(),
        ResponderProvider(),
    )
