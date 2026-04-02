"""Провайдеры зависимостей для DI-контейнера."""

from __future__ import annotations

from collections.abc import AsyncIterable

from dishka import Provider, Scope, alias, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from config.settings import Settings, settings
from src.domain.interfaces import (
    AIClient,
    EmbeddingGenerator,
    EntryAnalysisService,
    EntryRepository,
    VectorSearcher,
)
from src.infrastructure.ai.analysis import OllamaEntryAnalysisService
from src.infrastructure.ai.embeddings import OllamaEmbeddingService
from src.infrastructure.ai.ollama_client import OllamaClient
from src.infrastructure.db.engine import engine as db_engine
from src.infrastructure.db.repositories import PostgresEntryRepository
from src.application.analyze_entry import AnalyzeEntryInteractor
from src.application.get_entry import GetEntryUseCase
from src.application.list_entries import ListEntriesUseCase
from src.application.save_entry import SaveEntryUseCase
from src.application.search_entries import SearchEntriesUseCase
from src.presentation.responders.entry_responder import EntryResponder
from src.presentation.responders.list_responder import ListEntriesResponder
from src.presentation.responders.save_responder import SaveEntryResponder
from src.presentation.responders.search_responder import SearchEntriesResponder


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

    repo_impl = provide(PostgresEntryRepository)

    entry_repo = alias(source=PostgresEntryRepository, provides=EntryRepository)
    vector_searcher = alias(source=PostgresEntryRepository, provides=VectorSearcher)


class UseCaseProvider(Provider):
    """Провайдер для use cases."""

    save_entry = provide(SaveEntryUseCase, scope=Scope.REQUEST)
    list_entries = provide(ListEntriesUseCase, scope=Scope.REQUEST)
    get_entry = provide(GetEntryUseCase, scope=Scope.REQUEST)
    search_entries = provide(SearchEntriesUseCase, scope=Scope.REQUEST)
    analyze_entry = provide(AnalyzeEntryInteractor, scope=Scope.REQUEST)


class AIProvider(Provider):
    """Провайдер для AI-сервисов."""

    scope = Scope.REQUEST

    analysis_impl = provide(OllamaEntryAnalysisService)
    embedding_impl = provide(OllamaEmbeddingService)
    client = provide(OllamaClient)

    entry_analysis = alias(source=OllamaEntryAnalysisService, provides=EntryAnalysisService)
    embedder = alias(source=OllamaEmbeddingService, provides=EmbeddingGenerator)
    ai_client = alias(source=OllamaClient, provides=AIClient)


class ResponderProvider(Provider):
    """Провайдер для responders."""

    scope = Scope.REQUEST

    list_entries_responder = provide(ListEntriesResponder)
    search_entries_responder = provide(SearchEntriesResponder)
    entry_responder = provide(EntryResponder)
    save_entry_responder = provide(SaveEntryResponder)
