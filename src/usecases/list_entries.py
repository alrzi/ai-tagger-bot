"""Use case: получение списка записей пользователя."""

from __future__ import annotations

from src.domain.dto import EntryDTO
from src.domain.interfaces import EntryRepository


class ListEntriesUseCase:
    """Сценарий: получить последние записи пользователя."""

    def __init__(self, repository: EntryRepository) -> None:
        self.repository = repository

    async def execute(self, user_id: int, limit: int = 10) -> list[EntryDTO]:
        entries = await self.repository.list_recent(user_id, limit)
        return [EntryDTO.from_entity(e) for e in entries]
