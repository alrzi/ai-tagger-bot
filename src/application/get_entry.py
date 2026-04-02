"""Use case: получение одной записи по ID."""

from __future__ import annotations

from src.domain.entities import Entry
from src.domain.exceptions import NotFoundError
from src.domain.interfaces import EntryRepository


class GetEntryUseCase:
    """Сценарий: получить запись по ID."""

    def __init__(self, repository: EntryRepository) -> None:
        self.repository = repository

    async def execute(self, entry_id: int, user_id: int) -> Entry:
        """Возвращает доменную сущность Entry."""
        entry = await self.repository.get_by_id(entry_id, user_id)
        if entry is None:
            raise NotFoundError("Запись не найдена")
        return entry
