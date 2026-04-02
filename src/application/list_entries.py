"""Use case: получение списка записей пользователя."""

from __future__ import annotations

from src.domain.entities import Entry
from src.domain.interfaces import EntryRepository


class ListEntriesUseCase:
    """Сценарий: получить последние записи пользователя."""

    def __init__(self, repository: EntryRepository) -> None:
        self.repository = repository

    async def execute(self, user_id: int, limit: int = 10) -> list[Entry]:
        """Возвращает доменные сущности Entry."""
        return await self.repository.list_recent(user_id, limit)
