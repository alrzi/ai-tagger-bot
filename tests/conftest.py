"""Fixtures для интеграционных тестов базы данных."""

from __future__ import annotations

from typing import AsyncGenerator

import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from config.settings import Settings
from src.infrastructure.db.chunk_search_repository import PostgresChunkSearchRepository
from src.infrastructure.db.models import Base


@pytest_asyncio.fixture(scope="function")
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Фикстура движка базы данных для тестов."""
    settings = Settings(bot_token="test_token")
    
    # Используем отдельную тестовую базу
    test_database_url = settings.database_url.replace("ai_tagger", "ai_tagger_test")
    
    engine = create_async_engine(test_database_url, echo=False)
    
    # Применяем все миграции перед каждым тестом
    async with engine.begin() as connection:
        # Включаем pgvector расширение
        await connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        # Создаём все таблицы
        await connection.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Фикстура сессии базы данных с автоматическим откатом транзакции."""
    connection = await db_engine.connect()
    
    # Открываем транзакцию которую будем откатывать в конце
    transaction = await connection.begin()
    
    # Создаём сессию которая работает внутри этой транзакции
    session = AsyncSession(
        bind=connection,
        expire_on_commit=False,
    )
    
    yield session
    
    await session.close()
    
    # Откатываем ВСЕ изменения сделанные тестом
    await transaction.rollback()
    await connection.close()


@pytest_asyncio.fixture(scope="function")
async def search_repository(db_session: AsyncSession) -> PostgresChunkSearchRepository:
    """Фикстура репозитория поиска."""
    return PostgresChunkSearchRepository(db_session)
