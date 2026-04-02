"""Use case: получение одной записи по ID."""

from __future__ import annotations

from src.domain.dto import EntryDTO
from src.domain.exceptions import NotFoundError
from src.domain.interfaces import EntryReader


class GetEntryUseCase:
    """Сценарий: получить запись по ID."""

    def __init__(self, reader: EntryReader) -> None:
        self.reader = reader

    async def execute(self, entry_id: int, user_id: int) -> EntryDTO:
        entry = await self.reader.get_by_id(entry_id, user_id)
        if entry is None:
            raise NotFoundError("Запись не найдена")
        return EntryDTO.from_entity(entry)
