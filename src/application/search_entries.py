"""Use case: семантический поиск записей."""

from __future__ import annotations

from src.domain.entities import Entry
from src.domain.interfaces import EmbeddingGenerator, VectorSearcher


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
        """Возвращает список (Entry, similarity)."""
        query_vector = await self.embedder.embed(query)
        return await self.searcher.search_by_vector(user_id, query_vector, limit)
