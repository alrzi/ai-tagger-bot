"""Контейнер зависимостей (dishka)."""

from __future__ import annotations

from collections.abc import AsyncIterable

from dishka import Provider, Scope, alias, make_async_container, provide
from dishka.integrations.aiogram import AiogramProvider
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from config.settings import Settings, settings
from src.domain.interfaces import (
    AIClient,
    EmbeddingGenerator,
    EntryAnalysisService,
    EntryReader,
    EntryRepository,
    EntrySaver,
    EntryUpdater,
    VectorSearcher,
)
from src.infrastructure.ai.analysis import OllamaEntryAnalysisService
from src.infrastructure.ai.embeddings import OllamaEmbeddingService
from src.infrastructure.ai.ollama_client import OllamaClient
from src.infrastructure.db.engine import engine as db_engine
from src.infrastructure.db.repositories import PostgresEntryRepository
from src.presentation.presenters.entry_presenter import (
    EntryPresenterProtocol,
    TelegramEntryPresenter,
)
from src.usecases.analyze_entry import AnalyzeEntryUseCase
from src.usecases.get_entry import GetEntryUseCase
from src.usecases.list_entries import ListEntriesUseCase
from src.usecases.save_entry import SaveEntryUseCase
from src.usecases.search_entries import SearchEntriesUseCase


class SettingsProvider(Provider):
    """Провайдер для настроек."""

    @provide(scope=Scope.APP)
    def get_settings(self) -> Settings:
        return settings


class DatabaseProvider(Provider):
    """Провайдер для БД-сессий."""

    @provide(scope=Scope.APP)
    def get_factory(self) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            db_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self,
        factory: async_sessionmaker[AsyncSession],
    ) -> AsyncIterable[AsyncSession]:
        async with factory() as session:
            yield session


class RepositoryProvider(Provider):
    """Провайдер для репозиториев."""

    scope = Scope.REQUEST

    # 1. Создаём один реальный объект на весь запрос
    repo_impl = provide(PostgresEntryRepository)

    # 2. Раздаём "псевдонимы" (ссылки на тот же самый объект)
    entry_repo = alias(source=PostgresEntryRepository, provides=EntryRepository)
    entry_saver = alias(source=PostgresEntryRepository, provides=EntrySaver)
    entry_reader = alias(source=PostgresEntryRepository, provides=EntryReader)
    entry_updater = alias(source=PostgresEntryRepository, provides=EntryUpdater)
    vector_searcher = alias(source=PostgresEntryRepository, provides=VectorSearcher)


class UseCaseProvider(Provider):
    """Провайдер для use cases."""

    save_entry = provide(SaveEntryUseCase, scope=Scope.REQUEST)
    list_entries = provide(ListEntriesUseCase, scope=Scope.REQUEST)
    get_entry = provide(GetEntryUseCase, scope=Scope.REQUEST)
    search_entries = provide(SearchEntriesUseCase, scope=Scope.REQUEST)
    analyze_entry = provide(AnalyzeEntryUseCase, scope=Scope.REQUEST)


class AIProvider(Provider):
    """Провайдер для AI-сервисов."""

    scope = Scope.REQUEST

    # Регистрируем реализации
    analysis_impl = provide(OllamaEntryAnalysisService)
    embedding_impl = provide(OllamaEmbeddingService)
    client = provide(OllamaClient)

    # Делаем алиасы
    entry_analysis = alias(source=OllamaEntryAnalysisService, provides=EntryAnalysisService)
    embedder = alias(source=OllamaEmbeddingService, provides=EmbeddingGenerator)
    ai_client = alias(source=OllamaClient, provides=AIClient)


class PresenterProvider(Provider):
    """Провайдер для презентеров."""

    @provide(scope=Scope.REQUEST)
    def get_presenter(self) -> EntryPresenterProtocol:
        return TelegramEntryPresenter()


def make_container():
    """Создаёт DI-контейнер для aiogram."""
    return make_async_container(
        AiogramProvider(),
        SettingsProvider(),
        DatabaseProvider(),
        RepositoryProvider(),
        UseCaseProvider(),
        AIProvider(),
        PresenterProvider(),
    )
