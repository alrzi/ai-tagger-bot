"""Use case: семантический поиск записей."""

from __future__ import annotations

from typing import Protocol

from src.domain.entities import Entry


class EmbeddingGenerator(Protocol):
    """Протокол для генерации эмбеддингов."""

    async def embed(self, text: str) -> list[float]: ...


class VectorSearcher(Protocol):
    """Протокол для векторного поиска."""

    async def search_by_vector(
        self, user_id: int, query_vector: list[float], limit: int = 5
    ) -> list[tuple[Entry, float]]: ...


class SearchEntriesUseCase:
    """Сценарий: пользователь ищет по смыслу → находим похожие записи."""

    def __init__(
        self,
        embedder: EmbeddingGenerator,
        searcher: VectorSearcher,
    ) -> None:
        self.embedder = embedder
        self.searcher = searcher

    async def execute(
        self,
        user_id: int,
        query: str,
        limit: int = 5,
    ) -> list[tuple[Entry, float]]:
        query_vector = await self.embedder.embed(query)
        return await self.searcher.search_by_vector(user_id, query_vector, limit)
