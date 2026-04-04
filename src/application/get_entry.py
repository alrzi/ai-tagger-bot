"""Use case: получение одной записи по ID."""

from __future__ import annotations

from src.domain.entities import Entry
from src.domain.exceptions import NotFoundError
from src.domain.interfaces import EntryRepository
from src.application import log_use_case


class GetEntryUseCase:
    """Сценарий: получить запись по ID."""

    def __init__(self, repository: EntryRepository) -> None:
        self.repository = repository

    async def execute(self, entry_id: int, user_id: int) -> Entry:
        """Возвращает доменную сущность Entry."""
        log_use_case.info(f"🔍 Начинаю GetEntry | entry_id={entry_id}, user_id={user_id}")
        entry = await self.repository.get_by_id(entry_id, user_id)
        
        if entry is None:
            log_use_case.warning(f"⚠️ Запись не найдена | entry_id={entry_id}, user_id={user_id}")
            raise NotFoundError("Запись не найдена")
            
        log_use_case.info(f"✅ Запись получена | entry_id={entry_id}")
        return entry
