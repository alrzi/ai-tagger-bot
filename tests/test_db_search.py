"""Интеграционный тест поиска по базе данных."""

from __future__ import annotations

import json

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.chunk_search_repository import PostgresChunkSearchRepository


@pytest.mark.asyncio
async def test_chunk_search_query_works(search_repository: PostgresChunkSearchRepository) -> None:
    """Тест что SQL запрос поиска не падает с AmbiguousParameterError."""
    
    # Тест 1: category_id = None
    results = await search_repository.search_with_chunks(
        user_id=1,
        query_vector=[0.0] * 1024,
        category_id=None,
        limit=3
    )
    
    assert isinstance(results, list)
    
    # Тест 2: category_id = число
    results = await search_repository.search_with_chunks(
        user_id=1,
        query_vector=[0.0] * 1024,
        category_id=1,
        limit=3
    )
    
    assert isinstance(results, list)
    
    # Тест 3: limit = 0
    results = await search_repository.search_with_chunks(
        user_id=1,
        query_vector=[0.0] * 1024,
        category_id=None,
        limit=0
    )
    
    assert results == []
    
    # Тест 4: пустой вектор
    results = await search_repository.search_with_chunks(
        user_id=1,
        query_vector=[],
        category_id=None,
        limit=3
    )
    
    assert results == []

@pytest.mark.asyncio
async def test_search_actually_finds_result(db_session: AsyncSession) -> None:
    """Реальный интеграционный тест: сохраняем, потом находим по вектору."""

    test_vector = [0.1] * 768  # вектор правильной размерности 768 как в модели

    # Создаём запись
    await db_session.execute(text("""
        INSERT INTO entries (id, user_id, title, raw_text, category_position, summary)
        VALUES (100, 999999, 'Найди меня', 'Это содержимое которое должно быть найдено', 0, 'Тестовый саммари')
        ON CONFLICT DO NOTHING
    """))

    # Сохраняем чанк с точно таким же вектором
    await db_session.execute(text("""
        INSERT INTO chunks (entry_id, text, embedding, position)
        VALUES (100, 'Найди меня', :vec, 0)
    """), {'vec': json.dumps(test_vector)})

    await db_session.flush()

    repo = PostgresChunkSearchRepository(db_session)

    # Ищем по точно такому же вектору
    results = await repo.search_with_chunks(
        user_id=999999,
        query_vector=test_vector,
        category_id=None,
        limit=5
    )

    assert len(results) >= 1, "Должна найти хотя бы одну запись"
    assert results[0]['entry_id'] == 100, "Должен найти именно ту запись которую сохранили"
    assert results[0]['distance'] < 0.0001, "Дистанция должна быть почти нулевая"
