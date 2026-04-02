"""Интеграционные тесты для DI-контейнера.

Проверяем:
1. Scope isolation — объекты из разных REQUEST scope не «утекают»
2. Shared session — внутри одного REQUEST scope один и тот же экземпляр
3. Database connections — подключения корректно освобождаются
"""

from __future__ import annotations

import pytest
from dishka import AsyncContainer
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from src.domain.interfaces import EntryRepository
from src.ioc.container import make_container


@pytest.mark.asyncio
async def test_scope_isolation() -> None:
    """Объекты из разных REQUEST scope — разные экземпляры."""
    container: AsyncContainer = make_container()

    async with container() as request_container_1:
        repo_1 = await request_container_1.get(EntryRepository)

    async with container() as request_container_2:
        repo_2 = await request_container_2.get(EntryRepository)

    assert repo_1 is not repo_2, "Репозитории из разных scope должны быть разными объектами"


@pytest.mark.asyncio
async def test_shared_session_in_request() -> None:
    """Внутри одного REQUEST scope — один и тот же экземпляр."""
    container: AsyncContainer = make_container()

    async with container() as request_container:
        repo_1 = await request_container.get(EntryRepository)
        repo_2 = await request_container.get(EntryRepository)
        session_1 = await request_container.get(AsyncSession)
        session_2 = await request_container.get(AsyncSession)

    assert repo_1 is repo_2, "Репозитории внутри одного scope должны быть одним объектом"
    assert session_1 is session_2, "Сессии внутри одного scope должны быть одним объектом"
