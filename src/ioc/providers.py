"""Провайдеры зависимостей для DI-контейнера."""

from __future__ import annotations

from collections.abc import AsyncIterable

from aiogram import Bot
from dishka import Provider, Scope, alias, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from config.settings import Settings, settings
from src.domain.interfaces import (
    AIClient,
    CategoryRepository,
    ChunkRepository,
    EmbeddingGenerator,
    EntryAnalysisService,
    EntryRepository,
    TagRepository,
    VectorSearcher,
)
from src.infrastructure.ai.analysis import OllamaEntryAnalysisService
from src.infrastructure.ai.embeddings import NomicEmbeddingService
from src.infrastructure.ai.ollama_client import OllamaClient
from src.infrastructure.db.engine import engine as db_engine
from src.infrastructure.db.entry_repository import PostgresEntryRepository
from src.infrastructure.db.category_repository import PostgresCategoryRepository
from src.infrastructure.db.tag_repository import PostgresTagRepository
from src.infrastructure.db.chunk_repository import PostgresChunkRepository
from src.infrastructure.db.chunk_search_repository import PostgresChunkSearchRepository
from src.application.analyze_entry import AnalyzeEntryInteractor
from src.application.process_entry_chunks import ProcessEntryChunksInteractor
from src.application.get_entry import GetEntryUseCase
from src.application.get_stats import GetStatsUseCase
from src.application.list_entries import ListEntriesUseCase
from src.application.manage_categories import ManageCategoriesUseCase
from src.application.save_entry import SaveEntryUseCase
from src.application.search_entries import SearchEntriesUseCase
from src.application.sync_entry_tags import SyncEntryTags
from src.application.get_all_tags import GetAllTagsUseCase
from src.domain.text_chunker import TextChunker
from src.presentation.responders.analyze_result_responder import AnalyzeResultResponder
from src.presentation.responders.categories_responder import CategoriesResponder
from src.presentation.responders.entry_responder import EntryResponder
from src.presentation.responders.list_responder import ListEntriesResponder
from src.presentation.responders.save_responder import SaveEntryResponder
from src.presentation.responders.search_responder import SearchEntriesResponder
from src.presentation.responders.stats_responder import StatsResponder
from src.presentation.responders.tags_responder import TagsResponder


class SettingsProvider(Provider):
    """Провайдер для настроек."""

    @provide(scope=Scope.APP)
    def get_settings(self) -> Settings:
        return settings

    @provide(scope=Scope.APP)
    def get_bot(self, settings: Settings) -> Bot:
        return Bot(token=settings.bot_token)


class DatabaseProvider(Provider):
    """Провайдер для БД-сессий."""

    @provide(scope=Scope.APP)
    def get_engine(self) -> AsyncEngine:
        return db_engine

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
    category_repo_impl = provide(PostgresCategoryRepository)
    tag_repo_impl = provide(PostgresTagRepository)
    chunk_repo_impl = provide(PostgresChunkRepository)
    chunk_searcher_impl = provide(PostgresChunkSearchRepository)

    entry_repo = alias(source=PostgresEntryRepository, provides=EntryRepository)
    vector_searcher = alias(source=PostgresChunkSearchRepository, provides=VectorSearcher)
    category_repo = alias(source=PostgresCategoryRepository, provides=CategoryRepository)
    tag_repo = alias(source=PostgresTagRepository, provides=TagRepository)
    chunk_repo = alias(source=PostgresChunkRepository, provides=ChunkRepository)


class UseCaseProvider(Provider):
    """Провайдер для use cases."""

    save_entry = provide(SaveEntryUseCase, scope=Scope.REQUEST)
    list_entries = provide(ListEntriesUseCase, scope=Scope.REQUEST)
    get_entry = provide(GetEntryUseCase, scope=Scope.REQUEST)
    get_stats = provide(GetStatsUseCase, scope=Scope.REQUEST)
    search_entries = provide(SearchEntriesUseCase, scope=Scope.REQUEST)
    analyze_entry = provide(AnalyzeEntryInteractor, scope=Scope.REQUEST)
    manage_categories = provide(ManageCategoriesUseCase, scope=Scope.REQUEST)
    sync_entry_tags = provide(SyncEntryTags, scope=Scope.REQUEST)
    process_entry_chunks = provide(ProcessEntryChunksInteractor, scope=Scope.REQUEST)
    get_all_tags = provide(GetAllTagsUseCase, scope=Scope.REQUEST)
    
    @provide(scope=Scope.REQUEST)
    def get_text_chunker(self) -> TextChunker:
        return TextChunker()


class AIProvider(Provider):
    """Провайдер для AI-сервисов."""

    scope = Scope.REQUEST

    @provide
    def get_ollama_client(self, settings: Settings) -> OllamaClient:
        return OllamaClient(settings)

    analysis_impl = provide(OllamaEntryAnalysisService)
    embedding_impl = provide(NomicEmbeddingService)

    entry_analysis = alias(source=OllamaEntryAnalysisService, provides=EntryAnalysisService)
    embedder = alias(source=NomicEmbeddingService, provides=EmbeddingGenerator)
    ai_client = alias(source=OllamaClient, provides=AIClient)


class ResponderProvider(Provider):
    """Провайдер для responders."""

    scope = Scope.REQUEST

    list_entries_responder = provide(ListEntriesResponder)
    search_entries_responder = provide(SearchEntriesResponder)
    entry_responder = provide(EntryResponder)
    save_entry_responder = provide(SaveEntryResponder)
    analyze_result_responder = provide(AnalyzeResultResponder)
    categories_responder = provide(CategoriesResponder)
    stats_responder = provide(StatsResponder)
    tags_responder = provide(TagsResponder)
