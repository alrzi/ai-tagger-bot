"""Use case: получение списка записей пользователя."""

from __future__ import annotations

from src.domain.entities import Entry
from src.domain.interfaces import EntryRepository
from src.application import log_use_case


class ListEntriesUseCase:
    """Сценарий: получить последние записи пользователя."""

    def __init__(self, repository: EntryRepository) -> None:
        self.repository = repository

    async def execute(self, user_id: int, limit: int = 10) -> list[Entry]:
        """Возвращает доменные сущности Entry."""
        log_use_case.info(f"📋 Начинаю ListEntries | user_id={user_id}, limit={limit}")
        entries = await self.repository.list_recent(user_id, limit)
        log_use_case.info(f"✅ Список получен | записей={len(entries)}")
        return entries
