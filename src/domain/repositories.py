"""Абстрактные интерфейсы репозиториев. Domain не знает про БД."""

from __future__ import annotations

from typing import Protocol, Optional

from src.domain.entities import Entry


class EntryRepository(Protocol):
    """Протокол — контракт для любого хранилища записей."""

    async def save(self, entry: Entry) -> Entry: ...

    async def get_by_id(self, entry_id: int, user_id: int) -> Optional[Entry]: ...

    async def search_by_vector(
        self, user_id: int, query_vector: list[float], limit: int = 5
    ) -> list[tuple[Entry, float]]: ...

    async def search_by_tags(
        self, user_id: int, tags: list[str], limit: int = 10
    ) -> list[Entry]: ...

    async def list_recent(self, user_id: int, limit: int = 10) -> list[Entry]: ...

    async def delete(self, entry_id: int, user_id: int) -> bool: ...
